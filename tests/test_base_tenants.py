import csv
import datetime
import inspect
import ujson as json
import os
import pytest
from typing import Dict
import pprint
import importlib
from io import StringIO
from unittest.mock import patch
import pydantic
from base4.utilities.service.startup import shutdown_event, startup_event
from fastapi import FastAPI
from fastapi.testclient import TestClient
from base4.utilities.service.startup import service as app
import uuid
import httpx
from httpx import AsyncClient, ASGITransport
from base4.utilities.files import get_project_root
from base4.utilities.db.async_redis import get_redis
project_root = get_project_root()


@pytest.mark.asyncio
class TestBaseTenantsAPIV2:
    services = []
    app: FastAPI = FastAPI()
    default_tenant_code = "TEST"
    current_logged_user = None

    async def setup(self):
        async with get_redis() as redis_client:
            await redis_client.flushall()

        self.get_app()

        if 'tenants' not in self.services:
            self.services.append("tenants")

        healthy_test = await self.request(method='get', url='/api/tenants/healthy', headers={'X-Tenant-ID': 'pass'})
        assert healthy_test.status_code == 200

        res = await self.request(method='post', url='/api/tenants/initialize',
                                 json_data={
                                     'code': self.default_tenant_code,
                                     'display_name': self.default_tenant_code.capitalize(),
                                     'master_username': 'admin',
                                     'master_user_password': '123',
                                 },
                                 )

        assert res.status_code == 200
        assert 'id_tenant' in res.json()
        self.id_tenant = res.json()['id_tenant']

        from services.tenants.schemas.users import LoginRequest, LoginResponse

        res = await self.request(method='post', url='/api/tenants/users/login',
                                 model_data=LoginRequest(username='admin', password='123'),
                                 response_format_schema=LoginResponse, headers={'X-Tenant-ID': str(self.id_tenant)})

        # res = await self.request(method='post',url='/api/tenants/users/login',
        #                          json_data={'username': 'admin', 'password': '123'}, headers={'X-Tenant-ID': str(self.id_tenant)})

        assert res.status_code == 200
        assert 'token' in res.json()
        self.current_logged_user = {'username': 'admin', 'token': res.json()['token']}

    def get_app(self):
        for service in self.services:
            if os.path.isdir(f"{project_root}/src/services/{service}"):
                if '__' not in service:
                    for api_handler_file in os.listdir(f"{project_root}/src/services/{service}/api"):
                        if '__' not in api_handler_file:
                            module = importlib.import_module(f'services.{service}.api.{api_handler_file[:-3]}')
                            for api_handler in inspect.getmembers(module):
                                try:
                                    if hasattr(api_handler[1], 'router'):
                                        obj = api_handler[1]
                                        try:
                                            self.app.include_router(obj.router, prefix=obj.router.prefix)
                                        except Exception as e:
                                            self.app.include_router(obj.router, prefix=f"/api/{service}")
                                except Exception as e:
                                    continue

    @pytest.fixture(autouse=True, scope="function")
    async def setup_fixture(self) -> None:
        self.app.app_services = self.services
        await startup_event(self.services)
        await self.setup()
        yield
        await shutdown_event()

    async def request(self, method: str, url: str, json_data: dict = None, params={},model_data: pydantic.BaseModel = None,
                      headers: Dict={}, files=[], response_format_schema=None) -> httpx.Response:

        self.last_response = None
        self.last_status_code = None

        if model_data and json_data:
            raise Exception('You can only pass one of model_data or json_data')

        _method = method.lower()

        if not headers:
            headers = {}

        if 'Authorization' not in headers:
            if self.current_logged_user and "token" in self.current_logged_user and self.current_logged_user["token"]:
                headers['Authorization'] = f'Bearer {self.current_logged_user["token"]}'

        if _method not in ('delete', 'get'):

            if model_data:
                json_data = model_data.model_dump(mode='json')
            else:
                if json_data:
                    json_data = json.loads(json.dumps(json_data, default=str))

            if json_data:
                params['json'] = json_data if json_data else {}
        else:
            try:
                del params['json']
            except:
                pass

        params['url'] = url
        params['headers'] = headers

        async with httpx.AsyncClient(transport=ASGITransport(app=self.app), base_url='https://test') as client:
            client.cookies.set(
                'token',
                f'{self.current_logged_user["token"]}' if self.current_logged_user and "token" in self.current_logged_user else None,
            )
            func = getattr(client, _method, None)
            if not func:
                raise Exception(f'Invalid method: {_method}')

            try:
                response = await func(**params)
            except Exception as e:
                raise

            self.last_status_code = response.status_code
            self.last_response = response.json()

            if response.status_code in (200, 201):
                if response_format_schema:
                    resp = response_format_schema.model_validate(response.json())
                    assert resp
                    assert resp.model_dump(mode='json') == response.json()
                    self.last_response = resp

        return response
