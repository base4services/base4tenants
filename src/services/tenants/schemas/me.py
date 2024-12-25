import datetime
import uuid
from typing import Optional

import pydantic

class ChangeMyPreferencesRequest(pydantic.BaseModel):
    first_name: Optional[str|None] = None
    last_name: Optional[str|None] = None
    profile_picture: Optional[str|None] = None
    lang: Optional[str|None] = None

    # email: Optional[str|None] = None
    # mobile_phone: Optional[str|None] = None

class MeResponse(pydantic.BaseModel):
    id: uuid.UUID
    username: str
    id_tenant: uuid.UUID
    first_name: Optional[str|None] = None
    last_name: Optional[str|None] = None
    email: Optional[str|None] = None
    mobile_phone: Optional[str|None] = None
    profile_picture: Optional[str|None] = None
    lang: Optional[str|None] = None

    '''
    password expiring at
    password last changed
    last login
    '''


class LoginResponse(pydantic.BaseModel):
    token: str
    exp: datetime.datetime
    me: MeResponse
