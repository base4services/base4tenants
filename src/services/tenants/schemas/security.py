import pydantic

from typing import Literal, Optional


class Password(pydantic.BaseModel):
    password: Optional[str|None]=None

class PasswordStrengthResponse(pydantic.BaseModel):
    score: int
    description: Literal['weak', 'medium', 'strong']