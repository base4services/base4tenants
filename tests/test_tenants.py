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
	
	# todo, zavrsi dodavanje  u servis
	# async def test_option_post_get_over_multi_handler(self):
	# 	key = str(uuid.uuid4())
	# 	response = await self.request(method='post', url='/api/tenants/options/key/%s' % key)
	# 	assert response.status_code == 201
	# 	json: dict = response.json()
	# 	assert json == key
	#
	# 	response = await self.request(method='get', url='/api/tenants/options/key/%s' % key)
	# 	assert response.status_code == 200
	# 	json: dict = response.json()
	# 	assert json == key
	#
