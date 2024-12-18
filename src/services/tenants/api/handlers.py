import os
import datetime
from typing import Dict
import services.tenants.schemas as schemas
import services.tenants.services as services
import services.tenants.models as models
from services.tenants.schemas.me import LoginResponse, MeResponse
from base4.utilities.service.base import api, route
from base4.utilities.service.base import BaseAPIHandler
from fastapi import Request, APIRouter
import base4.service.exceptions

router = APIRouter()


@route(router=router, prefix='/api/tenants')
class APIHandler(BaseAPIHandler):
    def __init__(self, router):
        self.service = services
        super().__init__(router)
        
    @api(
        method='POST',
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
        method='GET',
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
    
    @api(
        method='POST',
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
    
    @api(
        method='POST',
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
