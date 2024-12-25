# THIS IS AN AUTO-GENERATED AND PROTECTED FILE. PLEASE USE
# THE compile-yaml SCRIPT TO GENERATE THIS FILE. DO NOT EDIT DIRECTLY
# AS IT CAN BE OVERWRITTEN.
#
# FILE GENERATED ON: 2024-12-25 00:12:37.806329


import datetime
import uuid
from typing import Any, AnyStr, Dict, List, Literal, Optional

from base4.project_specifics import lookups_module as Lookups
from base4.schemas.base import NOT_SET, Base
from fastapi.requests import Request
from pydantic import BaseModel, field_validator


class OptionSchema(Base):
    key: str
    value: str

    @classmethod
    def check_existence_rules(cls):
        return {}

    @classmethod
    def model_loc(cls):
        return {
            'created': 'created',
            'last_updated': 'last_updated',
            'is_deleted': 'is_deleted',
            'deleted': 'deleted',
            'id': 'id',
            'key': 'key',
            'value': 'value',
        }

    @classmethod
    def schema_class_loc(cls):
        return {
            "key": str,
            "value": str,
        }


class TenantSchema(Base):
    id: Optional[uuid.UUID | None | Literal[NOT_SET]] = NOT_SET
    code: str
    display_name: str

    @classmethod
    def check_existence_rules(cls):
        return {}

    @classmethod
    def model_loc(cls):
        return {
            'created': 'created',
            'last_updated': 'last_updated',
            'is_deleted': 'is_deleted',
            'deleted': 'deleted',
            'id': 'id',
            'code': 'code',
            'display_name': 'display_name',
        }

    @classmethod
    def schema_class_loc(cls):
        return {
            "id": uuid.UUID,
            "code": str,
            "display_name": str,
        }


class UserSchema(Base):
    tenant_id: Optional[uuid.UUID | None | Literal[NOT_SET]] = NOT_SET
    username: Optional[str | None | Literal[NOT_SET]] = NOT_SET
    password: Optional[str | None | Literal[NOT_SET]] = NOT_SET
    display_name: Optional[str | None | Literal[NOT_SET]] = NOT_SET
    profile_picture: Optional[str | None | Literal[NOT_SET]] = NOT_SET
    first_name: Optional[str | None | Literal[NOT_SET]] = NOT_SET
    last_name: Optional[str | None | Literal[NOT_SET]] = NOT_SET
    email: Optional[str | None | Literal[NOT_SET]] = NOT_SET
    mobile_phone: Optional[str | None | Literal[NOT_SET]] = NOT_SET
    temporary_hash: Optional[str | None | Literal[NOT_SET]] = NOT_SET
    temporary_hash_expire_on: Optional[datetime.datetime | None | Literal[NOT_SET]] = NOT_SET
    lang: Optional[str | None | Literal[NOT_SET]] = NOT_SET

    @classmethod
    def check_existence_rules(cls):
        return {}

    @classmethod
    def model_loc(cls):
        return {
            'created': 'created',
            'last_updated': 'last_updated',
            'is_deleted': 'is_deleted',
            'deleted': 'deleted',
            'id': 'id',
            'tenant_id': 'tenant_id',
            'username': 'username',
            'password': 'password',
            'display_name': 'display_name',
            'profile_picture': 'profile_picture',
            'first_name': 'first_name',
            'last_name': 'last_name',
            'email': 'email',
            'mobile_phone': 'mobile_phone',
            'temporary_hash': 'temporary_hash',
            'temporary_hash_expire_on': 'temporary_hash_expire_on',
            'lang': 'lang',
        }

    @classmethod
    def schema_class_loc(cls):
        return {
            "tenant_id": uuid.UUID,
            "username": str,
            "password": str,
            "display_name": str,
            "profile_picture": str,
            "first_name": str,
            "last_name": str,
            "email": str,
            "mobile_phone": str,
            "temporary_hash": str,
            "temporary_hash_expire_on": datetime.datetime,
            "lang": str,
        }
