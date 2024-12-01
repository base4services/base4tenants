from base4.utilities.service.base import api
from . import router
from base4.utilities.service.startup import service as app
from base4.utilities.service.base import BaseAPIController
import services.tenants.schemas as schemas
import services.tenants.services as services
from fastapi import Request


class InitializeAPIService(BaseAPIController):
	def __init__(self, router):
		self.service = services
		super().__init__(router)
	
	@api(
		methods=['POST'],
		path='/initialize',
	)
	async def initialize(self, request: Request, data: schemas.InitializeFirstTenantRequest) -> dict:
		service = self.service.TenantsService()
		try:
			return await service.initialize(data)
		
		except base4.service.exceptions.ServiceException as se:
			raise se.make_http_exception()
		except Exception as e:
			raise base4.service.exceptions.HTTPException(500, detail={'code': 'INTERNAL_SERVER_ERROR', 'message': str(e)})


InitializeAPIService(router)
app.include_router(router, prefix='/api/tenants')
