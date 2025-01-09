import uuid
import pydantic


class Me(pydantic.BaseModel):
    id: uuid.UUID
    role: str
    id_tenant: uuid.UUID
    id_session: uuid.UUID
