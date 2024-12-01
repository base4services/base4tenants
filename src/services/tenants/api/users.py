import base4.service.exceptions
from base4.utilities.service.base import api
import services.tenants.schemas as schemas
from services.tenants.schemas.me import LoginResponse, MeResponse
from . import router
from base4.utilities.service.startup import service as app
from base4.utilities.service.base import BaseAPIController
import services.tenants.services as services
from fastapi import Request


class LoginAPIService(BaseAPIController):
    def __init__(self, router):
        self.service = services
        super().__init__(router)
    
    @api(
        methods=['POST'],
        path='/users/login',
    )
    async def login(self, request: Request, data: schemas.LoginRequest) -> LoginResponse:
        service = self.service.UsersService()
        try:
            return await service.login(data)
        except base4.service.exceptions.ServiceException as se:
            raise se.make_http_exception()
        except Exception as e:
            raise base4.service.exceptions.HTTPException(500, detail={'code': 'INTERNAL_SERVER_ERROR', 'message': str(e)})
    
    @api(
        methods=['GET'],
        path='/users/me',
    )
    async def session(self, request: Request) -> MeResponse:
        service = self.service.UsersService()
        try:
            return await service.me(self.session)
        except base4.service.exceptions.ServiceException as se:
            raise se.make_http_exception()
        except Exception as e:
            raise base4.service.exceptions.HTTPException(500, detail={'code': 'INTERNAL_SERVER_ERROR', 'message': str(e)})
    
    
LoginAPIService(router)
app.include_router(router, prefix='/api/tenants')
