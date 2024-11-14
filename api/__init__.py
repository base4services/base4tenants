from fastapi import APIRouter

router = APIRouter()

from base4.utilities.service.startup import service as app

from .health import *
from .initialize import *
from .keyauth import *
from .options import *
from .tenants import *
from .users import *

app.include_router(router, prefix="/api/tenants")
