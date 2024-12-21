import datetime

from typing import Optional

import pydantic
import uuid

from .me import MeResponse

class LoginRequest(pydantic.BaseModel):
    username: str
    password: str


class LoginResponse(pydantic.BaseModel):
    token: str
    exp: datetime.datetime
    me: MeResponse

class ForgotPasswordRequest(pydantic.BaseModel):
    email: str

class RegisterUserRequest(pydantic.BaseModel):
    username: str
    password: str
    first_name: Optional[str | None] = None
    last_name: Optional[str | None] = None
    email: Optional[str | None] = None
    mobile_phone: Optional[str | None] = None


class RegisterUserResponse(pydantic.BaseModel):
    registration_control_id: uuid.UUID

class ActivateUserResponse(pydantic.BaseModel):
    active: bool

