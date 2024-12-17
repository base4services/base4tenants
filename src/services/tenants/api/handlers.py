import os
import datetime
from typing import Dict
import services.tenants.schemas as schemas
import services.tenants.schemas.security as security_schemas
from services.tenants.schemas.me import MeResponse
from services.tenants.schemas.tenants import InitializeFirstTenantRequest, InitializeFirstTenantRequest
from services.tenants.schemas.users import RegisterUserRequest, RegisterUserResponse, LoginRequest, LoginResponse, ForgotPasswordRequest
from base4.utilities.service.base import api, route
from base4.utilities.service.base import BaseAPIHandler
from fastapi import Request, APIRouter
import base4.service.exceptions

router = APIRouter()
# router2 = APIRouter()
# router3 = APIRouter()

from services.tenants.services.users import UsersService
from services.tenants.services.tenants import TenantsService
from services.tenants.services.security import SecurityService


@route(router=router, prefix='/api/tenants')
class GeneralAPIHandler(BaseAPIHandler):
    def __init__(self, router):
        self.security_service = SecurityService()
        self.tenants_service = TenantsService()  # REMVOE KAD RAZDVOJIS
        self.user_service = UsersService()

        super().__init__(router)

    @api(
        method='POST',
        path='/security/check-password-strength',
    )
    async def check_password_strength(self, request: Request, data: security_schemas.Password) -> security_schemas.PasswordStrengthResponse:
        try:
            return self.security_service.check_password_strength(data.password)
        except Exception as e:
            raise

    # @route(router=APIRouter(), prefix='/api/tenants/users')
    # class UsersHandler(BaseAPIHandler):
    #     def __init__(self, router):
    #         self.service = UsersService()
    #         super().__init__(router)
    #
    @api(
        method='POST',
        path='/users/register',
    )
    async def register(self, request: Request, data: RegisterUserRequest):  # -> RegisterUserResponse:
        try:
            return await self.user_service.register(data, request)
        except base4.service.exceptions.ServiceException as se:
            raise se.make_http_exception()
        except Exception as e:
            raise base4.service.exceptions.HTTPException(500,
                                                         detail={'code': 'INTERNAL_SERVER_ERROR', 'message': str(e)})

    #
    @api(
        method='POST',
        path='/users/activate/activation-code/{activation_code}',
    )
    async def activate(self, request: Request, activation_code: str):  # -> ActivateUserResponse
        try:
            return await self.user_service.activate(request, activation_code)
        except base4.service.exceptions.ServiceException as se:
            raise se.make_http_exception()
        except Exception as e:
            raise base4.service.exceptions.HTTPException(500,
                                                         detail={'code': 'INTERNAL_SERVER_ERROR', 'message': str(e)})

    @api(
        method='POST',
        path='/users/login',
    )
    async def login(self, request: Request, data: LoginRequest):  # -> LoginResponse:
        try:
            res = await self.user_service.login(request, data)
            return res
        except base4.service.exceptions.ServiceException as se:
            raise se.make_http_exception()
        except Exception as e:
            raise base4.service.exceptions.HTTPException(500, detail={'code': 'INTERNAL_SERVER_ERROR', 'message': str(e)})

    @api(
        method='POST',
        path='/users/forgot-password',
    )
    async def forgot_password(self, request: Request, data: ForgotPasswordRequest):
        try:
            return await self.user_service.forgot_password(request, data)
        except base4.service.exceptions.ServiceException as se:
            raise se.make_http_exception()
        except Exception as e:
            raise base4.service.exceptions.HTTPException(500, detail={'code': 'INTERNAL_SERVER_ERROR', 'message': str(e)})

    @api(
        method='POST',
        path='/users/reset-password/reset-password-code/{reset_password_code}',
    )
    async def reset_password(self, request: Request, reset_password_code: str, data: security_schemas.Password):
        try:
            return await self.user_service.reset_password(request, reset_password_code, data)
        except base4.service.exceptions.ServiceException as se:
            raise se.make_http_exception()
        except Exception as e:
            raise base4.service.exceptions.HTTPException(500, detail={'code': 'INTERNAL_SERVER_ERROR', 'message': str(e)})

    @api(
        method='GET',
        path='/users/me',
    )
    async def session(self, request: Request) -> MeResponse:
        try:
            return await self.tenants_service.me(self.session)
        except base4.service.exceptions.ServiceException as se:
            raise se.make_http_exception()
        except Exception as e:
            raise base4.service.exceptions.HTTPException(500,
                                                         detail={'code': 'INTERNAL_SERVER_ERROR', 'message': str(e)})

    #
    # @route(router=APIRouter(), prefix='/api/tenants')
    # class TenantsHandler(BaseAPIHandler):
    #     def __init__(self, router):
    #         self.service = TenantsService()
    #         super().__init__(router)

    @api(
        method='POST',
        path='/initialize',
    )
    async def initialize(self, request: Request, data: InitializeFirstTenantRequest):  # ? -> InitializeFirstTenantRequest:
        try:
            res = await self.tenants_service.initialize(data)

            # res = res.model_dump(mode='json')
            return res

        except base4.service.exceptions.ServiceException as se:
            raise se.make_http_exception()
        except Exception as e:
            raise base4.service.exceptions.HTTPException(500,
                                                         detail={'code': 'INTERNAL_SERVER_ERROR', 'message': str(e)})
#


# import services.tenants.schemas as schemas
# import services.tenants.services as services
# import services.tenants.models as models
# from services.tenants.schemas.me import LoginResponse, MeResponse
# from base4.utilities.service.base import BaseAPIHandler, api, route
# from fastapi import Request, APIRouter
# import base4.service.exceptions
#
#
# @route(router=APIRouter(), prefix='/api/tenants')
# class APIHandler(BaseAPIHandler):
#     def __init__(self, router):
#         self.service = services
#         super().__init__(router)
#
#     @api(
#         is_authorized=False,
#         method='POST',
#         path='/users/login',
#     )
#     async def login(self, request: Request, data: schemas.LoginRequest) -> LoginResponse:
#         service = self.service.UsersService()
#         try:
#             return await service.login(data)
#         except base4.service.exceptions.ServiceException as se:
#             raise se.make_http_exception()
#         except Exception as e:
#             raise base4.service.exceptions.HTTPException(500, detail={'code': 'INTERNAL_SERVER_ERROR', 'message': str(e)})
#
#     @api(
#         method='GET',
#         path='/users/me',
#     )
#     async def session(self, request: Request) -> MeResponse:
#         service = self.service.UsersService()
#         try:
#             return await service.me(self.session)
#         except base4.service.exceptions.ServiceException as se:
#             raise se.make_http_exception()
#         except Exception as e:
#             raise base4.service.exceptions.HTTPException(500, detail={'code': 'INTERNAL_SERVER_ERROR', 'message': str(e)})
#
#     @api(
#         method='POST',
#         path='/key-auth',
#     )
#     async def key_auth(self, request: Request, data: schemas.KeyAuth) -> dict:
#         service = self.service.KeyAuthService()
#
#         try:
#             c = await models.Tenant.all().count()
#         except Exception as e:
#             raise
#
#         try:
#             return {'token': await service.generate_token(data.key)}
#         except base4.service.exceptions.ServiceException as se:
#             raise se.make_http_exception()
#         except Exception as e:
#             raise base4.service.exceptions.HTTPException(500, detail={'code': 'INTERNAL_SERVER_ERROR', 'message': str(e)})
#
#     @api(
#         method='POST',
#         path='/initialize',
#     )
#     async def initialize(self, request: Request, data: schemas.InitializeFirstTenantRequest) -> dict:
#         service = self.service.TenantsService()
#         try:
#             return await service.initialize(data)
#
#         except base4.service.exceptions.ServiceException as se:
#             raise se.make_http_exception()
#         except Exception as e:
#             raise base4.service.exceptions.HTTPException(500, detail={'code': 'INTERNAL_SERVER_ERROR', 'message': str(e)})
