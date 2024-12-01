import os
from fastapi import APIRouter
router = APIRouter()

from base4.utilities.service.startup import service as app
from base4.utilities.common import import_all_from_dir
import_all_from_dir(
	directory=os.path.dirname(__file__),
    package=__name__,
    namespace=globals()
)
