import uuid
import pydantic
from fastapi import Request


class Me(pydantic.BaseModel):
    id: uuid.UUID
    role: str
    id_tenant: uuid.UUID
    id_session: uuid.UUID

    # def __init__(self, request: Request):
        # token = request.headers.get('Authorization')
        # token = token.replace('Bearer ', '')
        #
        # from base4.utilities.security.jwt import decode_token
        # session = decode_token(token)
        #
        # self.super().__init__(id=session.user_id,
        #                       role=session.role,
        #                       id_tenant=session.tenant_id)

    @staticmethod
    async def get(request: Request) -> 'Me':

        token = request.headers.get('Authorization')
        token = token.replace('Bearer ', '')

        from base4.utilities.security.jwt import decode_token
        session = decode_token(token)

        # TODO Dohvati propertije preko redisa ili preko baze.. !

        return Me(id=session.user_id, role=session.role, id_tenant=session.tenant_id, id_session=session.session_id)

