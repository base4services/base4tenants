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
from base4.utilities.service.startup import shutdown_event, startup_event
from fastapi import FastAPI
from fastapi.testclient import TestClient
from base4.utilities.service.startup import service as app
import uuid
import httpx
from httpx import AsyncClient
from base4.utilities.files import get_project_root

project_root = get_project_root()


@pytest.mark.asyncio
class TestBaseTenantsAPIV2:
    services = []
    app: FastAPI = FastAPI()
    default_tenant_code = "TEST"
    current_logged_user = None
    
    async def setup(self):
        self.get_app()
        
        if 'tenants' not in self.services:
            self.services.append("tenants")
        
        healthy_test = await self.request(method='get', url='/api/tenants/healthy', headers={'X-Tenant-ID': 'pass'})
        assert healthy_test.status_code == 200
        
        res = await self.request(
            method='post', url='/api/tenants/initialize',
            json_data={
                'code':                 self.default_tenant_code,
                'display_name':         self.default_tenant_code.capitalize(),
                'master_username':      'admin',
                'master_user_password': '123',
            }
            )
        
        assert res.status_code == 200
        assert 'id' in res.json()
        self.id_tenant = res.json()['id']
        
        res = await self.request(method='post', url='/api/tenants/users/login', json_data={'username': 'admin', 'password': '123'}, headers={'X-Tenant-ID': str(self.id_tenant)})
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
    
    async def request(self, method: str, url: str, json_data: dict = None, data: dict = None, params={}, headers={}, files=[]):
        
        _method = method.lower()
        
        if not headers:
            headers = {}
        
        if 'Authorization' not in headers:
            if self.current_logged_user and "token" in self.current_logged_user and self.current_logged_user["token"]:
                headers['Authorization'] = f'Bearer {self.current_logged_user["token"]}'
        
        if _method not in ('delete', 'get'):
            if json_data:
                json_data = json.loads(json.dumps(json_data, default=str))
                params['json'] = json_data if json_data else {}
        else:
            try:
                del params['json']
            except:
                pass
        
        params['url'] = url
        params['headers'] = headers
        
        async with httpx.AsyncClient(app=self.app, base_url='https://test') as client:
            client.cookies.set(
                'token',
                f'{self.current_logged_user["token"]}' if self.current_logged_user and "token" in self.current_logged_user else None,
            )
            func = getattr(client, _method, None)
            
            if not func:
                raise Exception(f'Invalid method: {_method}')
            
            try:
                response = await func(**params)
                del params
            except Exception as e:
                raise
        
        return response
