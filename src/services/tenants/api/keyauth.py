import base4.service.exceptions
from base4.utilities.service.base import api
from . import router
from base4.utilities.service.startup import service as app
from base4.utilities.service.base import BaseAPIController
import services.tenants.schemas as schemas
import services.tenants.services as services
from fastapi import Request
import services.tenants.models as models


class KeyAuthAPIService(BaseAPIController):
    def __init__(self, router):
        self.service = services
        super().__init__(router)
    
    @api(
        methods=['POST'],
        path='/key-auth',
    )
    async def key_auth(self, request: Request, data: schemas.KeyAuth) -> dict:
        service = self.service.KeyAuthService()
        
        try:
            c = await models.Tenant.all().count()
        except Exception as e:
            raise
        
        try:
            return {'token': await service.generate_token(data.key)}
        except base4.service.exceptions.ServiceException as se:
            raise se.make_http_exception()
        except Exception as e:
            raise base4.service.exceptions.HTTPException(500, detail={'code': 'INTERNAL_SERVER_ERROR', 'message': str(e)})


KeyAuthAPIService(router)
app.include_router(router, prefix='/api/tenants')
