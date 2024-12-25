import os
import uuid
from pprint import pprint

import tortoise.timezone
from services.tenants.schemas import Password, ChangePasswordRequest, ChangeMyPreferencesRequest
from .test_base_tenants import TestBaseTenantsAPIV2

import pytest
import fakeredis
from base4.utilities.db.async_redis import get_redis

from services.tenants.schemas.users import (RegisterUserRequest,
                                            ActivateUserResponse,
                                            LoginRequest,
                                            ForgotPasswordRequest,

                                            )

from unittest.mock import MagicMock, patch
import tortoise.timezone
import datetime
from shared.services.sendmail.test import enable_emailing_in_test_mode


class TestUserRegistration(TestBaseTenantsAPIV2):
    services = ['tenants', 'sendmail']

    async def setup(self):
        await super().setup()

    async def test_is_tenants_healthy(self):
        response = await self.request(method='get', url="/api/tenants/healthy", headers={'X-Tenant-ID': 'pass'})
        assert response.status_code == 200

    async def test_check_password_strength(self):
        from services.tenants.schemas.security import PasswordStrengthResponse, Password

        await self.request(method='post', url="/api/tenants/security/check-password-strength",
                           model_data=Password(password='testpassword'),
                           response_format_schema=PasswordStrengthResponse, headers={'X-Tenant-ID': 'pass'})
        assert self.last_status_code == 200
        assert self.last_response == PasswordStrengthResponse(score=3, description='medium')

    async def test_healthy(self):
        response = await self.request(method='get', url="/api/tenants/healthy", headers={'X-Tenant-ID': 'pass'})
        assert response.status_code == 200

    async def test_register_and_activate_user_full_successful_process(self):
        self._username = 'testuser'
        self._password = 'testpassword'
        self._email = 'igor+testemail@digitalcube.rs'
        self._first_name = 'John'
        self._last_name = 'Doe'
        self._mobile_phone = "+123456789"
        self._lang = 'en'

        # first try to login with user that does not exist

        await self.request(method='post', url="/api/tenants/users/login",
                           model_data=LoginRequest(username=self._username, password=self._password),
                           headers={'X-Tenant-ID': str(self.id_tenant)})

        assert self.last_status_code == 401
        assert self.last_response['detail']['code'] == 'INVALID_CREDENTIALS'

        # register but don't activate user

        await self.request(method='post', url="/api/tenants/users/register",
                           model_data=RegisterUserRequest(
                               username=self._username,
                               password=self._password,
                               email=self._email,
                               first_name=self._first_name,
                               last_name=self._last_name,
                               mobile_phone=self._mobile_phone,
                               lang=self._lang
                           ),
                           headers={'X-Tenant-ID': str(self.id_tenant)})

        assert self.last_status_code == 200

        # user ist still unable to login

        await self.request(method='post', url="/api/tenants/users/login",
                           model_data=LoginRequest(username=self._username, password=self._password),
                           headers={'X-Tenant-ID': str(self.id_tenant)})

        assert self.last_status_code == 401
        assert self.last_response['detail']['code'] == 'INVALID_CREDENTIALS'

        # read email from mailqueue

        async with get_redis() as redis_client:
            email = await redis_client.lpop("mailqueue")
            assert email
            assert 'to' in email and email['to'] == self._email
            assert 'body' in email

            body = email['body']
            hash = body.split('/')[-1]
            assert hash

        # activate user

        await self.request(method='post', url=f"/api/tenants/users/activate/activation-code/{hash}",
                           response_format_schema=ActivateUserResponse,
                           headers={'x-tenant-id': self.id_tenant}
                           )

        assert self.last_status_code == 200
        assert self.last_response == ActivateUserResponse(active=True)

        # now user can login
        await self.request(method='post', url="/api/tenants/users/login",
                           model_data=LoginRequest(username=self._username, password=self._password),
                           headers={'X-Tenant-ID': str(self.id_tenant)})

        assert self.last_status_code == 200

    async def test_logout(self):
        await self.test_register_and_activate_user_full_successful_process()

        # login with correct password to prove that user is activated
        await self.request(method='post', url="/api/tenants/users/login",
                           model_data=LoginRequest(username=self._username, password=self._password),
                           headers={'X-Tenant-ID': str(self.id_tenant)})

        assert self.last_status_code == 200
        assert 'token' in self.last_response
        token = self.last_response["token"]

        # check who am I
        await self.request(method='get', url="/api/tenants/users/me",
                           headers={'Authorization': f'Bearer {token}'})

        assert self.last_status_code == 200

        # logout
        await self.request(method='post', url="/api/tenants/users/logout",
                           headers={'Authorization': f'Bearer {token}'})

        assert self.last_status_code == 200

        await self.request(method='get', url="/api/tenants/users/me",
                           headers={'Authorization': f'Bearer {token}'})

        assert self.last_status_code == 401


    async def test_try_register_user_after_activation_expires(self):
        _username = 'testuser'
        _password = 'testpassword'
        _email = 'testemail@example.com'

        mock_date = tortoise.timezone.make_aware(datetime.datetime.fromisoformat('2024-08-01T00:00:00'))
        with patch('tortoise.timezone.now', MagicMock(return_value=mock_date)):
            await self.request(method='post', url="/api/tenants/users/register",
                               model_data=RegisterUserRequest(
                                   username=_username,
                                   password=_password,
                                   email=_email),
                               headers={'X-Tenant-ID': str(self.id_tenant)})

            assert self.last_status_code == 200

        # read email from mailqueue

        async with get_redis() as redis_client:
            email = await redis_client.lpop("mailqueue")
            assert email
            assert 'to' in email and email['to'] == _email
            assert 'body' in email

            body = email['body']
            hash = body.split('/')[-1]
            assert hash

        # after 15 days activation will not be possible

        mock_date = tortoise.timezone.make_aware(datetime.datetime.fromisoformat('2024-08-15T00:00:00'))
        with patch('tortoise.timezone.now', MagicMock(return_value=mock_date)):
            await self.request(method='post', url=f"/api/tenants/users/activate/activation-code/{hash}",
                               response_format_schema=ActivateUserResponse,
                               headers={'x-tenant-id': self.id_tenant}
                               )

            assert self.last_status_code == 406
            assert self.last_response['detail']['code'] == 'ACTIVATION_CODE_EXPIRED'

        # try to activate after 1 day instead

        mock_date = tortoise.timezone.make_aware(datetime.datetime.fromisoformat('2024-08-01T00:00:00'))
        with patch('tortoise.timezone.now', MagicMock(return_value=mock_date)):
            await self.request(method='post', url=f"/api/tenants/users/activate/activation-code/{hash}",
                               response_format_schema=ActivateUserResponse,
                               headers={'x-tenant-id': self.id_tenant}
                               )

            assert self.last_status_code == 200
            assert self.last_response == ActivateUserResponse(active=True)

    # @enable_emailing_in_test_mode
    async def test_forgot_password(self):
        await self.test_register_and_activate_user_full_successful_process()

        # login with correct password to prove that user is activated
        await self.request(method='post', url="/api/tenants/users/login",
                           model_data=LoginRequest(username=self._username, password=self._password),
                           headers={'X-Tenant-ID': str(self.id_tenant)})

        assert self.last_status_code == 200

        # try to login with random password

        await self.request(method='post', url="/api/tenants/users/login",
                           model_data=LoginRequest(username=self._username, password=str(uuid.uuid4())),
                           headers={'X-Tenant-ID': str(self.id_tenant)})

        assert self.last_status_code == 401

        # try to reset password for non existing user, for example use random email

        await self.request(method='post', url="/api/tenants/users/forgot-password",
                           model_data=ForgotPasswordRequest(email=f'{uuid.uuid4()}@example.com'),
                           headers={'X-Tenant-ID': str(self.id_tenant)})
        # system will return successful response
        assert self.last_status_code == 200

        # email can not be sent - 404
        await self.request('post', url='/api/sendmail/send-next')
        assert self.last_status_code == 404

        # # but email can not be sent
        # async with get_redis() as redis_client:
        #     email = await redis_client.lpop("mailqueue")
        #     assert not email

        # request password reset using forgot password feature
        await self.request(method='post', url="/api/tenants/users/forgot-password",
                           model_data=ForgotPasswordRequest(email=self._email),
                           headers={'X-Tenant-ID': str(self.id_tenant)})

        assert self.last_status_code == 200

        # email was found in mailqueue
        async with get_redis() as redis_client:
            email = await redis_client.lpop("mailqueue")
            assert email
            assert 'to' in email and email['to'] == self._email
            assert 'body' in email

            body = email['body']
            hash = body.split('/')[-1]
            assert hash

            # return email into queue, becuse send-next will fetch it
            await redis_client.lpush("mailqueue", email)

        await self.request('post', url='/api/sendmail/send-next')
        assert self.last_status_code == 200

        await self.request(method='post', url=f"/api/tenants/users/reset-password/reset-password-code/{hash}",
                           model_data=Password(password='newpassword'),
                           headers={'x-tenant-id': self.id_tenant})

        assert self.last_status_code == 200

        # try to login with old password
        await self.request(method='post', url="/api/tenants/users/login",
                           model_data=LoginRequest(username=self._username, password=self._password),
                           headers={'X-Tenant-ID': str(self.id_tenant)})

        assert self.last_status_code == 401

        # login with new password
        await self.request(method='post', url="/api/tenants/users/login",
                           model_data=LoginRequest(username=self._username, password='newpassword'),
                           headers={'X-Tenant-ID': str(self.id_tenant)})

        assert self.last_status_code == 200

    async def test_try_to_reset_password_after_reset_link_expires(self):
        await self.test_register_and_activate_user_full_successful_process()

        mock_date = tortoise.timezone.make_aware(datetime.datetime.fromisoformat('2024-08-01T00:00:00'))
        with patch('tortoise.timezone.now', MagicMock(return_value=mock_date)):
            # request password reset using forgot password feature
            await self.request(method='post', url="/api/tenants/users/forgot-password",
                               model_data=ForgotPasswordRequest(email=self._email),
                               headers={'X-Tenant-ID': str(self.id_tenant)})

        # email was found in mailqueue
        async with get_redis() as redis_client:
            email = await redis_client.lpop("mailqueue")
            assert email
            assert 'to' in email and email['to'] == self._email
            assert 'body' in email

            body = email['body']
            hash = body.split('/')[-1]
            assert hash

        # try to reset after 12 hours

        mock_date = tortoise.timezone.make_aware(datetime.datetime.fromisoformat('2024-08-01T12:00:00'))
        with patch('tortoise.timezone.now', MagicMock(return_value=mock_date)):
            await self.request(method='post', url=f"/api/tenants/users/reset-password/reset-password-code/{hash}",
                               model_data=Password(password='newpassword'),
                               headers={'x-tenant-id': self.id_tenant})

            assert self.last_status_code == 406
            assert self.last_response['detail']['code'] == 'RESET_PASSWORD_CODE_EXPIRED'

        # instead this reset after 5 minutes

        mock_date = tortoise.timezone.make_aware(datetime.datetime.fromisoformat('2024-08-01T00:05:00'))
        with patch('tortoise.timezone.now', MagicMock(return_value=mock_date)):
            await self.request(method='post', url=f"/api/tenants/users/reset-password/reset-password-code/{hash}",
                               model_data=Password(password='newpassword'),
                               headers={'x-tenant-id': self.id_tenant})

            assert self.last_status_code == 200

        # login with new password
        await self.request(method='post', url="/api/tenants/users/login",
                           model_data=LoginRequest(username=self._username, password='newpassword'),
                           headers={'X-Tenant-ID': str(self.id_tenant)})

        assert self.last_status_code == 200

    async def test_logged_user_changes_his_password(self):
        await self.test_register_and_activate_user_full_successful_process()

        # login with correct password to prove that user is activated
        await self.request(method='post', url="/api/tenants/users/login",
                           model_data=LoginRequest(username=self._username, password=self._password),
                           headers={'X-Tenant-ID': str(self.id_tenant)})

        assert self.last_status_code == 200
        assert 'token' in self.last_response
        token = self.last_response["token"]

        # change password, try with same as old one

        await self.request(method='post', url="/api/tenants/users/change-password",
                           model_data=ChangePasswordRequest(old_password='testpassword',
                                                            new_password='testpassword'),
                           headers={'Authorization': f'Bearer {token}'},
                           )

        assert self.last_status_code == 406
        assert self.last_response['detail']['code'] == 'SAME_PASSWORD'

        # change password, try with incorect old one

        await self.request(method='post', url="/api/tenants/users/change-password",
                           model_data=ChangePasswordRequest(old_password='incorect-old-one',
                                                            new_password='newpassword'),
                           headers={'Authorization': f'Bearer {token}'},
                           )

        assert self.last_status_code == 401
        assert self.last_response['detail']['code'] == 'INVALID_PASSWORD'

        # change password with acceptable one

        await self.request(method='post', url="/api/tenants/users/change-password",
                           model_data=ChangePasswordRequest(old_password='testpassword',
                                                            new_password='newpassword'),
                           headers={'Authorization': f'Bearer {token}'},
                           )

        assert self.last_status_code == 200

        # try login with old password

        await self.request(method='post', url="/api/tenants/users/login",
                           model_data=LoginRequest(username=self._username, password=self._password),
                           headers={'X-Tenant-ID': str(self.id_tenant)})

        assert self.last_status_code == 401

        # login with new password
        await self.request(method='post', url="/api/tenants/users/login",
                           model_data=LoginRequest(username=self._username, password='newpassword'),
                           headers={'X-Tenant-ID': str(self.id_tenant)})

        assert self.last_status_code == 200

    async def test_logged_user_get_me(self):
        await self.test_register_and_activate_user_full_successful_process()

        # login with correct password to prove that user is activated
        await self.request(method='post', url="/api/tenants/users/login",
                           model_data=LoginRequest(username=self._username, password=self._password),
                           headers={'X-Tenant-ID': str(self.id_tenant)})

        assert self.last_status_code == 200
        assert 'token' in self.last_response
        pprint(self.last_response)

        token = self.last_response["token"]

        await self.request(method='get', url="/api/tenants/users/me",
                           headers={'Authorization': f'Bearer {token}'})

        # assert self.last_status_code == 200

    async def test_logged_user_change_his_own_attributes(self):
        await self.test_register_and_activate_user_full_successful_process()

        # login with correct password to prove that user is activated
        await self.request(method='post', url="/api/tenants/users/login",
                           model_data=LoginRequest(username=self._username, password=self._password),
                           headers={'X-Tenant-ID': str(self.id_tenant)})

        assert self.last_status_code == 200
        assert 'token' in self.last_response
        token = self.last_response["token"]

        await self.request(method='get', url="/api/tenants/users/me", headers={'Authorization': f'Bearer {token}'})
        assert self.last_status_code == 200
        me_before = self.last_response

        await self.request(method='patch', url="/api/tenants/users/me",
                           model_data=ChangeMyPreferencesRequest(
                               first_name='Noe',
                           ),
                           headers={'Authorization': f'Bearer {token}'}
                           )

        assert self.last_status_code == 200
        pprint(self.last_response)

        await self.request(method='get', url="/api/tenants/users/me", headers={'Authorization': f'Bearer {token}'})
        assert self.last_status_code == 200
        me_after = self.last_response

        assert me_before['first_name'] == 'John'
        assert me_after['first_name'] == 'Noe'
        assert me_before['last_name'] == 'Doe'
        assert me_after['last_name'] == 'Doe'

        await self.request(method='patch', url="/api/tenants/users/me",
                           model_data=ChangeMyPreferencesRequest(
                               first_name='Eon',
                               last_name='Toe',
                               email='email@toe.com',
                               mobile_phone='+987654321'
                           ),
                           headers={'Authorization': f'Bearer {token}'}
                           )

        assert self.last_status_code == 200

        await self.request(method='get', url="/api/tenants/users/me", headers={'Authorization': f'Bearer {token}'})
        assert self.last_status_code == 200
        me_after = self.last_response

        assert me_after['first_name'] == 'Eon'
        assert me_after['last_name'] == 'Toe'

        await self.request(method='patch', url="/api/tenants/users/me",
                           model_data=ChangeMyPreferencesRequest(
                               profile_picture='avatar.png',
                           ),
                           headers={'Authorization': f'Bearer {token}'}
                           )

        assert self.last_status_code == 200

        await self.request(method='get', url="/api/tenants/users/me", headers={'Authorization': f'Bearer {token}'})
        assert self.last_status_code == 200
        me_after = self.last_response
        assert me_after['first_name'] == 'Eon'
        assert me_after['last_name'] == 'Toe'
        assert me_after['profile_picture'] == 'avatar.png'
        assert me_after['lang'] == 'en'

        await self.request(method='patch', url="/api/tenants/users/me",
                           model_data=ChangeMyPreferencesRequest(
                               lang='de',
                           ),
                           headers={'Authorization': f'Bearer {token}'}
                           )
        assert self.last_status_code == 200

        await self.request(method='get', url="/api/tenants/users/me", headers={'Authorization': f'Bearer {token}'})
        assert self.last_status_code == 200
        assert self.last_response['lang'] == 'de'
