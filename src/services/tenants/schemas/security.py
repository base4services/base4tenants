import pydantic

from typing import Literal, Optional


class Password(pydantic.BaseModel):
    password: Optional[str|None]=None

class ChangePasswordRequest(pydantic.BaseModel):
    old_password: str
    new_password: str

class PasswordStrengthResponse(pydantic.BaseModel):
    score: int
    description: Literal['weak', 'medium', 'strong']