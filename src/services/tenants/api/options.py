from typing import Dict

import base4.service.exceptions
from base4.utilities.service.base import api
from . import router
from base4.utilities.service.startup import service as app
from base4.utilities.service.base import BaseAPIController
import services.tenants.services as services
from fastapi import Request


class OptionsAPIService(BaseAPIController):
    def __init__(self, router):
        self.service = services
        super().__init__(router)
    
    @api(
        methods=['GET'],
        path='/options/by-key/{key}',
        response_model=Dict[str, str]
    )
    async def get_by_key(self, request: Request, key: str) -> dict:
        service = self.service.OptionService()
        return await service.get_option_by_key(key)
    
    
OptionsAPIService(router)
app.include_router(router, prefix='/api/tenants')
