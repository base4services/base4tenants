import datetime
import os
import uuid
import json

import fastapi
import tortoise.timezone
import dotenv
import jwt
from base4.service.base import BaseService
from base4.service.exceptions import ServiceException
from base4.utilities.logging.setup import class_exception_traceback_logging, get_logger
from tortoise.exceptions import IntegrityError

import shared.common as common

import services.tenants.models.generated_tenants_model as models
import services.tenants.schemas.users as users_schemas
import services.tenants.schemas.security as security_schemas
from services.tenants.schemas.me import MeResponse
from base4.utilities.db.async_redis import get_redis

from fastapi import Request

from ._db_conn import get_conn_name

logger = get_logger()

from base4.utilities.files import read_file

dotenv.load_dotenv()
default_id_user = uuid.UUID(os.getenv('DEFAULT_ID_USER', '00000000-0000-0000-0000-000000000000'))

private_key = read_file('security/private_key.pem')
public_key = read_file('security/public_key.pem')


# @class_exception_traceback_logging(logger)
class UsersService(BaseService[models.Tenant]):
    def __init__(self):
        super().__init__(users_schemas, models.User, get_conn_name())

    def check_password(self, user, password):

        # TODO - Implement bcrypt, and also mock bcrypt in tests, so in tests we will use plain text passwords

        return user.password == password

    def generate_token_payload(self, user):
        return {
            'username': user.username,
            'id_user': str(user.id),
            'id_tenant': str(user.tenant_id),
            'exp': int((datetime.datetime.now() + datetime.timedelta(days=2)).timestamp()),
        }

    def generate_token(self, payload):
        # JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'secret')

        global private_key

        try:

            encoded_jwt = jwt.encode(payload, private_key, algorithm='RS256')
            # encoded_jwt = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
        except Exception as e:
            raise
        return encoded_jwt

    async def register(self, data: users_schemas.RegisterUserRequest, request: Request) -> users_schemas.RegisterUserResponse:

        tenant = await common.get_tenant_from_headers(models.Tenant, request)

        if await self.model.filter(tenant=tenant, username=data.username).count():
            raise ServiceException('USER_ALREADY_EXISTS', 'User already exists', status_code=406)

        try:

            user = self.model(
                logged_user_id=default_id_user,
                tenant=tenant,
                username=data.username,
                password=data.password,
                email=data.email.strip().lower(),
                temporary_hash=str(uuid.uuid4()),
                temporary_hash_expire_on=tortoise.timezone.now() + datetime.timedelta(days=7),
            )

            await user.save()
        except IntegrityError:  # (IntegrityError('UNIQUE constraint failed: tenants_users.tenant_id, tenants_users.username'))
            raise ServiceException('ERROR_ADDING_USER', 'User already exists', status_code=500)
        except Exception as e:
            raise

        from shared.services.sendmail.schemas.email_schema import EmailRequest, NameEmail
        from shared.services.sendmail.sendmail import enqueue_to_redis

        SERVICES_TENANTS_ACTIVATION_LINK = os.getenv('SERVICES_TENANTS_ACTIVATION_LINK', '{}')
        SERVICES_TENANTS_ACTIVATION_LINK = SERVICES_TENANTS_ACTIVATION_LINK.format(user.temporary_hash)

        email_request = EmailRequest(
            sender=NameEmail(name='ChosenAPP',email='info@digitalcube.rs'),
            to=[NameEmail(name=data.username.split('@')[0],email=data.email)],
            subject='Activate your account',
            body=f'Please click on this link to activate your account: {SERVICES_TENANTS_ACTIVATION_LINK}')

        await enqueue_to_redis(email_request)

        if os.getenv('TEST_MODE', 'False') != 'true':
            import shared.services.sendmail.sendmail as sendmail
            await sendmail.send_next()

        return users_schemas.RegisterUserResponse(registration_control_id=user.id)

    async def activate(self, request: Request, activation_code: str) -> users_schemas.ActivateUserResponse:

        tenant = await common.get_tenant_from_headers(models.Tenant, request)

        try:
            user = await self.model.filter(tenant=tenant,
                                           is_valid=False,
                                           is_deleted=False,
                                           temporary_hash=activation_code).get()
        except Exception as e:
            raise

        if user.temporary_hash_expire_on < tortoise.timezone.now():
            raise ServiceException('ACTIVATION_CODE_EXPIRED', 'Activation code expired', status_code=406)

        user.is_valid = True
        user.temporary_hash = None
        user.temporary_hash_expire_on = None

        await user.save()

        return users_schemas.ActivateUserResponse(active=user.is_valid)

    async def login(self, request: Request, data: users_schemas.LoginRequest) -> users_schemas.LoginResponse:

        tenant = await common.get_tenant_from_headers(models.Tenant, request)

        user = await self.model.filter(tenant=tenant, username=data.username, is_valid=True, is_deleted=False).get_or_none()

        if not user or not self.check_password(user, data.password):
            raise ServiceException('INVALID_CREDENTIALS',
                                   'Invalid credentials',
                                   status_code=401
                                   )

        payload = self.generate_token_payload(user)

        try:
            me = MeResponse(
                id=user.id,
                username=user.username,
                id_tenant=user.tenant_id,
            )

            res = users_schemas.LoginResponse(token=self.generate_token(payload), exp=payload['exp'], me=me)

            return res

        except Exception as e:
            raise

    async def forgot_password(self, request: Request, data: users_schemas.ForgotPasswordRequest) -> None:

        tenant = await common.get_tenant_from_headers(models.Tenant, request)

        user = await self.model.filter(tenant=tenant,
                                       email=data.email.strip().lower(),
                                       is_valid=True,
                                       is_deleted=False).get_or_none()

        if not user:
            return None

        user.temporary_hash = str(uuid.uuid4())
        user.temporary_hash_expire_on = tortoise.timezone.now() + datetime.timedelta(hours=1)
        await user.save()

        from shared.services.sendmail.schemas.email_schema import EmailRequest, NameEmail
        from shared.services.sendmail.sendmail import enqueue_to_redis

        SERVICES_TENANTS_RESET_PASSWORD_LINK = os.getenv('SERVICES_TENANTS_RESET_PASSWORD_LINK', '{}')
        SERVICES_TENANTS_RESET_PASSWORD_LINK = SERVICES_TENANTS_RESET_PASSWORD_LINK.format(user.temporary_hash)

        try:
            email_request = EmailRequest(
                sender=NameEmail(name='ChosenAPP', email='info@digitalcube.rs'),
                to=[NameEmail(name=data.email.split('@')[0],email=data.email)],
                subject='Reset your password',
                body=f'Please click on this link to reset your password: {SERVICES_TENANTS_RESET_PASSWORD_LINK}')
                # body=f'Please click on this link to activate your account: http://localhost:4200/reset-password/{user.temporary_hash}')

        except Exception as e:
            raise

        await enqueue_to_redis(email_request)

        if os.getenv('TEST_MODE', 'False') != 'true':
            import shared.services.sendmail.sendmail as sendmail
            await sendmail.send_next()

        return None

    async def reset_password(self, request: Request, reset_password_code: str, data: security_schemas.Password) -> None:

        tenant = await common.get_tenant_from_headers(models.Tenant, request)

        try:
            user = await self.model.filter(tenant=tenant,
                                           is_valid=True,
                                           is_deleted=False,
                                           temporary_hash=reset_password_code).get()
        except Exception as e:
            raise ServiceException('INVALID_CODE', 'Invalid reset password code', status_code=401)

        if user.temporary_hash_expire_on < tortoise.timezone.now():
            raise ServiceException('RESET_PASSWORD_CODE_EXPIRED', 'Code expired', status_code=406)

        user.password = data.password
        user.temporary_hash = None
        user.temporary_hash_expire_on = None

        await user.save()

        return None

    async def me(self, session) -> MeResponse:

        try:
            me = await self.model.filter(id=session.user_id, tenant_id=session.tenant_id, is_deleted=False).get_or_none()

            res = MeResponse(
                id=me.id,
                username=me.username,
                id_tenant=me.tenant_id,
            )

        except Exception as e:
            raise

        return res

    async def create_master_user_only_if_there_is_one_tenant_and_no_users(self, tenant, username, password):

        nr_of_users = await self.model.all().count()
        if nr_of_users > 0:
            raise ServiceException('CAN_NOT_INITIALIZE_TENANT', 'Primary tenant already initialized')

        try:
            user = self.model(
                logged_user_id=default_id_user,
                tenant=tenant,
                username=username,
                password=password,
                is_valid=True,
                is_deleted=False,
            )
        except Exception as e:
            raise

        await user.save()
        return user
