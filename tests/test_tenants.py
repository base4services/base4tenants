import os
import uuid
from .test_base_tenants import TestBaseTenantsAPIV2


class TestSVC(TestBaseTenantsAPIV2):
	services = ['tenants']
	
	async def setup(self):
		await super().setup()
	
	async def test_is_tenants_healthy(self):
		response = await self.request(method='get', url="/api/tenants/healthy")
		assert response.status_code == 200
