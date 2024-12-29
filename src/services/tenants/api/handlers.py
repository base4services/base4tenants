import services.tenants.schemas as schemas
from services.tenants.schemas.me import LoginResponse, MeResponse
from base4.utilities.service.base import BaseAPIHandler, api, route
from services.tenants.schemas.users import RegisterUserRequest, RegisterUserResponse, LoginRequest, LoginResponse, ForgotPasswordRequest
import services.tenants.schemas.security as security_schemas

from fastapi import Request, APIRouter
import base4.service.exceptions
from services.tenants.services.users import UsersService
from services.tenants.services.tenants import TenantsService
from services.tenants.services.security import SecurityService
from base4.utilities.oauth import oauth_login, oauth_callback
from base4.utilities.totp import generate_totp_secret, get_totp_uri, verify_totp_token



@route(router=APIRouter(), prefix='/api/tenants')
class APIHandler(BaseAPIHandler):
    def __init__(self, router):
        self.security_service = SecurityService()
        self.tenants_service = TenantsService()  # REMVOE KAD RAZDVOJIS
        self.user_service = UsersService()
        super().__init__(router)

    @api(
        is_authorized=False,
        method='POST',
        path='/users/login',
    )
    async def login(self, request: Request, data: schemas.LoginRequest) -> LoginResponse:
        try:
            return await self.user_service.login(request, data)
        except base4.service.exceptions.ServiceException as se:
            raise se.make_http_exception()
        except Exception as e:
            raise base4.service.exceptions.HTTPException(500, detail={'code': 'INTERNAL_SERVER_ERROR', 'message': str(e)})

    @api(
        method='POST',
        path='/users/logout',
    )
    async def logout(self, request: Request):
        try:
            return await self.user_service.logout(request)
        except base4.service.exceptions.ServiceException as se:
            raise se.make_http_exception()
        except Exception as e:
            raise base4.service.exceptions.HTTPException(500, detail={'code': 'INTERNAL_SERVER_ERROR', 'message': str(e)})

    @api(
        method='GET',
        path='/users/me',
    )
    async def me(self, request: Request) -> MeResponse:
        try:
            return await self.user_service.me(self.session)
        except base4.service.exceptions.ServiceException as se:
            raise se.make_http_exception()
        except Exception as e:
            raise base4.service.exceptions.HTTPException(500, detail={'code': 'INTERNAL_SERVER_ERROR', 'message': str(e)})

    @api(
        method='PATCH',
        path='/users/me',
    )
    async def change_own_attribute(self, request: Request, data: schemas.ChangeMyPreferencesRequest):
        try:
            return await self.user_service.change_me(request, data)
        except base4.service.exceptions.ServiceException as se:
            raise se.make_http_exception()
        except Exception as e:
            raise base4.service.exceptions.HTTPException(500, detail={'code': 'INTERNAL_SERVER_ERROR', 'message': str(e)})

    @api(
        is_public=False,
        method='POST',
        path='/initialize',
    )
    async def initialize(self, request: Request, data: schemas.InitializeFirstTenantRequest):
        try:
            res = await self.tenants_service.initialize(data)
            return res

        except base4.service.exceptions.ServiceException as se:
            raise se.make_http_exception()
        except Exception as e:
            raise base4.service.exceptions.HTTPException(500, detail={'code': 'INTERNAL_SERVER_ERROR', 'message': str(e)})

    @api(
        is_authorized=False,
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
        is_authorized=False,
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
        is_authorized=False,
        method='POST',
        path='/users/activate/activation-code/{activation_code}',
    )
    async def activate(self, request: Request, activation_code: str):  # -> ActivateUserResponse
        try:
            return await self.user_service.activate(request, activation_code)
        except base4.service.exceptions.ServiceException as se:
            raise se.make_http_exception()
        except Exception as e:
            raise base4.service.exceptions.HTTPException(
                500,
                detail={'code': 'INTERNAL_SERVER_ERROR', 'message': str(e)}
            )

    @api(
        is_authorized=False,
        method='POST',
        path='/security/check-password-strength',
    )
    async def check_password_strength(self, request: Request, data: security_schemas.Password) -> security_schemas.PasswordStrengthResponse:
        try:
            return self.security_service.check_password_strength(data.password)
        except Exception as e:
            raise

    @api(
        is_authorized=False,
        method='POST',
        path='/users/register',
    )
    async def register(self, request: Request, data: RegisterUserRequest):  # -> RegisterUserResponse:
        try:
            return await self.user_service.register(data, request)
        except base4.service.exceptions.ServiceException as se:
            raise se.make_http_exception()
        except Exception as e:
            raise base4.service.exceptions.HTTPException(
                500,
                detail={'code': 'INTERNAL_SERVER_ERROR', 'message': str(e)}
            )

    @api(
        method='POST',
        path='/users/change-password',
    )
    async def change_password(self, request: Request, data: security_schemas.ChangePasswordRequest):
        try:
            return await self.user_service.change_password(request, data)
        except base4.service.exceptions.ServiceException as se:
            raise se.make_http_exception()
        except Exception as e:
            raise base4.service.exceptions.HTTPException(
                500,
                detail={'code': 'INTERNAL_SERVER_ERROR', 'message': str(e)}
            )

@route(router=APIRouter(), prefix='/api/tenants/oauth')
class OauthAPIHandler(BaseAPIHandler):
    def __init__(self, router):
        self.security_service = SecurityService()
        self.tenants_service = TenantsService()  # REMVOE KAD RAZDVOJIS
        self.user_service = UsersService()
        super().__init__(router)

    @api(
        is_authorized=False,
        method='GET',
        path='/users/{provider}/login',
    )
    async def oauth_login(self, request: Request, provider: str) -> dict:
        try:
            return await oauth_login(request, provider)
        except base4.service.exceptions.ServiceException as se:
            raise se.make_http_exception()
        except Exception as e:
            raise base4.service.exceptions.HTTPException(500,detail={'code': 'INTERNAL_SERVER_ERROR', 'message': str(e)})

    @api(
        is_authorized=False,
        method='GET',
        path='/users/{provider}/callback',
    )
    async def oauth_callback(self, request: Request, provider: str) -> dict:
        user_info = await oauth_callback(request, provider)
        if not user_info:
            raise base4.service.exceptions.HTTPException(status_code=400, detail="PROVIDER_ERROR")

        email = user_info.get("email") or user_info.get("username")
        if not email:
            data_part = user_info.get("data")
            if data_part and data_part.get("username"):
                email = data_part["username"]
            else:
                raise base4.service.exceptions.HTTPException(status_code=400, detail="MISSING_CREDENTIALS")

        user = await self.user_service.oauth_check_is_users_exits(request, email)
        if not user:
            try:
                return await self.user_service.oauth_register(request, provider, user_info)
            except base4.service.exceptions.ServiceException as se:
                raise se.make_http_exception()
            except Exception as e:
                raise base4.service.exceptions.HTTPException(500, detail={'code': 'INTERNAL_SERVER_ERROR', 'message': str(e)})


@route(router=APIRouter(), prefix='/api/tenants/mfa')
class MFAAPIHandler(BaseAPIHandler):
    def __init__(self, router):
        self.security_service = SecurityService()
        self.tenants_service = TenantsService()  # REMVOE KAD RAZDVOJIS
        self.user_service = UsersService()
        super().__init__(router)

    @api(
        is_authorized=False,
        method='POST',
        path='/enable',
    )
    async def enable(self, request: Request, email: str) -> dict:
        user = await self.user_service.oauth_check_is_users_exits(request, email)
        if not user:
            raise base4.service.exceptions.HTTPException(status_code=404, detail="USER_NOT_FOUND")

        if user.totp_secret:
            raise base4.service.exceptions.HTTPException(status_code=400, detail="ALREADY_ENABLED")

        totp_secret = await self.user_service.save_totp_secret(request, user.username)

        return get_totp_uri(totp_secret, user.username)


    @api(
        is_authorized=False,
        method='POST',
        path='/verify',
    )
    async def verify(self, request: Request, token: str, email:str) -> dict:

        user = await self.user_service.oauth_check_is_users_exits(request, email)
        if not user or not user.totp_secret:
            raise base4.service.exceptions.HTTPException(status_code=404, detail="2FA_NOT_ENABLED")

        if verify_totp_token(user.totp_secret, token):
            return {"success": True}
        raise base4.service.exceptions.HTTPException(status_code=401, detail="INVALID_TOTP")