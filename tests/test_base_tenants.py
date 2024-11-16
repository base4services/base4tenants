import csv
import datetime
import json
import os
import pprint
from io import StringIO
from unittest.mock import patch
from .test_base import TestBase
from contextlib import ExitStack


class TestBaseTenants(TestBase):
    services = ['tenants']

    default_tenant_code = 'TEST'

    async def setup(self):

        await super().setup()

        if 'tenants' not in self.services:
            self.services.append("tenants")

        healthy_test = await self.api('GET', '/api/tenants/healthy')
        assert healthy_test.status_code == 200

        res = await self.api(
            'POST',
            '/api/tenants/initialize',
            _body={
                'code': self.default_tenant_code,
                'display_name': self.default_tenant_code.capitalize(),
                'master_username': 'admin',
                'master_user_password': '123',
            },
        )

        assert res.status_code == 200
        assert 'id' in res.json()
        self.id_tenant = res.json()['id']

        res = await self.api('POST', '/api/tenants/users/login', _body={'username': 'admin', 'password': '123'}, _headers={'X-Tenant-ID': str(self.id_tenant)})
        assert res.status_code == 200
        assert 'token' in res.json()
        self.current_logged_user = {'username': 'admin', 'token': res.json()['token']}

        res = await self.api('POST', '/api/tenants/users/login', _body={'username': 'admin', 'password': '123'}, _headers={'X-Tenant-ID': str(self.id_tenant)})
        assert res.status_code == 200

        healthy_test = await self.api('GET', '/api/tenants/healthy')
        assert healthy_test.status_code == 200

        ...
