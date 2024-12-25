# THIS IS AN AUTO-GENERATED AND PROTECTED FILE. PLEASE USE
# THE bmanager compile-env SCRIPT TO GENERATE THIS FILE. DO NOT EDIT DIRECTLY
# AS IT CAN BE OVERWRITTEN.
#
# FILE GENERATED ON: 2024-12-25 00:12:37.678621

import tortoise
from base4.models.base import *
from tortoise import fields
from tortoise.fields import CASCADE, RESTRICT
from tortoise.models import Model


class Option(Base, Model):

    class Meta:
        table = "tenants_options"
        app = "tenants"

    key = fields.CharField(255, null=False, unique=True)
    value = fields.TextField(null=True)

    mk_cache_rules = []

    @staticmethod
    def schema_service_loc():
        return None

    schema_loc_dict = {'created': 'created', 'last_updated': 'last_updated', 'key': 'key', 'value': 'value'}


class Tenant(Base, Model):

    class Meta:
        table = "tenants"
        app = "tenants"

    code = fields.CharField(255, null=False, unique=True)
    display_name = fields.CharField(255, null=False)

    mk_cache_rules = []

    @staticmethod
    def schema_service_loc():
        return None

    schema_loc_dict = {'created': 'created', 'last_updated': 'last_updated', 'code': 'code', 'display_name': 'display_name'}


class User(BaseNoTenant, Model):

    class Meta:
        table = "tenants_users"
        app = "tenants"
        unique_together = (('tenant', 'username'),)

    tenant = fields.ForeignKeyField('tenants.Tenant', index=True, on_delete=tortoise.fields.base.OnDelete.RESTRICT, related_name='users')
    username = fields.CharField(255, null=True)
    password = fields.CharField(255, null=True)
    display_name = fields.CharField(255, null=True)
    profile_picture = fields.CharField(255, null=True)
    first_name = fields.CharField(255, null=True)
    last_name = fields.CharField(255, null=True)
    email = fields.CharField(255, null=True)
    mobile_phone = fields.CharField(255, null=True)
    role = fields.CharField(64)
    permissions = fields.JSONField(default={})
    temporary_hash = fields.CharField(255, null=True, unuque=True)
    temporary_hash_expire_on = fields.DatetimeField(null=True)
    lang = fields.CharField(16, null=True, default='en')

    mk_cache_rules = []

    @staticmethod
    def schema_service_loc():
        return None

    schema_loc_dict = {
        'created': 'created',
        'last_updated': 'last_updated',
        'tenant_id': 'tenant_id',
        'username': 'username',
        'password': 'password',
        'display_name': 'display_name',
        'profile_picture': 'profile_picture',
        'first_name': 'first_name',
        'last_name': 'last_name',
        'email': 'email',
        'mobile_phone': 'mobile_phone',
        'role': 'role',
        'permissions': 'permissions',
        'temporary_hash': 'temporary_hash',
        'temporary_hash_expire_on': 'temporary_hash_expire_on',
        'lang': 'lang',
    }


class UserC11(BaseCache11, Model):

    class Meta:
        table = "tenants_users_c11"
        app = "tenants"

    user = fields.OneToOneField('tenants.User', index=True, related_name='cache11')

    mk_cache_rules = []

    @staticmethod
    def schema_service_loc():
        return None

    schema_loc_dict = {'created': 'created', 'last_updated': 'last_updated', 'user': 'user'}
