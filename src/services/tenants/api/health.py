import datetime
from base4.utilities.service.base import api
from . import router
from base4.utilities.service.startup import service as app
from base4.utilities.service.base import BaseAPIController
from fastapi import Request


class HealthyAPIService(BaseAPIController):
    @api(
        path='/healthy',
    )
    async def healthy(self, request: Request):
        return {'status': 'ok'}


HealthyAPIService(router)
app.include_router(router, prefix='/api/tenants')
