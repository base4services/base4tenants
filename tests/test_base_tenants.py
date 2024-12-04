import csv
import datetime
import ujson as json
import os
import pytest
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


@pytest.mark.asyncio
class TestBaseTenantsAPIV2:
    app = app
    services = []
    client = TestClient(app)
    current_logged_user = None
    default_tenant_code = 'TEST'

    async def setup(self):

        if 'tenants' not in self.services:
            self.services.append("tenants")
        
        healthy_test = self.client.get('/api/tenants/healthy')
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
        assert 'id' in res.json()
        self.id_tenant = res.json()['id']

        res = await self.request(method='post',url='/api/tenants/users/login', json_data={'username': 'admin', 'password': '123'}, headers={'X-Tenant-ID': str(self.id_tenant)})
        assert res.status_code == 200
        assert 'token' in res.json()
        self.current_logged_user = {'username': 'admin', 'token': res.json()['token']}

    @pytest.fixture(autouse=True, scope="function")
    async def setup_fixture(self) -> None:
        """
        Fixture for tests of application.
        It will be executed everytime before each test and after.

        decorator:
                @pytest.fixture(autouse=True, scope="function")
                        autouse (bool): If true this fixture will be executed
                                                        before and after every test.
                        scope (str): This fixture is meant for function tests.

        :return: None
        """
        
        for service in self.services:
            try:
                module = importlib.import_module(f'services.{service}.api.run')
                self.app.include_router(module.router, prefix=f"/api/{service}")
            except Exception as e:
                raise

        self.app.app_services = self.services
        await startup_event(self.services)
        await self.setup()
        yield
        await shutdown_event()
        
    async def request(self, method: str, url: str, json_data: dict = None, data: dict = None, params=None, headers={}, files=[]):
        #if 'Authorization' not in headers:
        if self.current_logged_user and "token" in self.current_logged_user and self.current_logged_user["token"]:
            headers['Authorization'] = f'Bearer {self.current_logged_user["token"]}'
        
        if json_data:
           json_data = json.loads(json.dumps(json_data, default=str))
           
        response = self.client.request(
            method=method, url=url, json=json_data, data=data, params=params, headers=headers,
            cookies={'token': f'{self.current_logged_user["token"]}' if self.current_logged_user and "token" in self.current_logged_user else None, },
            files=files
        )
        if response.status_code == 422:
            return json.loads(response.text)
        return response
