import datetime
import uuid
from typing import Optional

import pydantic


class MeResponse(pydantic.BaseModel):
    id: uuid.UUID
    username: str
    id_tenant: uuid.UUID

    '''
    password expiring at
    password last changed
    last login
    '''


