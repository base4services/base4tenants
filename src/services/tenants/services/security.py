import uuid
from itertools import starmap

from base4.service.base import BaseService
from base4.service.exceptions import ServiceException
from base4.utilities.logging.setup import class_exception_traceback_logging, get_logger

import services.tenants.models as models
import services.tenants.schemas.security as schemas

from ._db_conn import get_conn_name

logger = get_logger()


class SecurityService:

    @staticmethod
    def check_password_strength(password: str) -> schemas.PasswordStrengthResponse:

        # Initialize score
        score = 0

        # Check length
        if len(password) < 8:
            score += 0
        elif len(password) < 12:
            score += 1
        else:
            score += 2

        # Check for lowercase letters
        if any(c.islower() for c in password):
            score += 1

        # Check for uppercase letters
        if any(c.isupper() for c in password):
            score += 1

        # Check for numbers
        if any(c.isdigit() for c in password):
            score += 1

        # Check for special characters
        if any(not c.isalnum() for c in password):
            score += 1

        # Determine strength based on score
        if score < 2:
            return schemas.PasswordStrengthResponse(score=score, description="weak")
        elif score < 4:
            return schemas.PasswordStrengthResponse(score=score, description="medium")

        return schemas.PasswordStrengthResponse(score=score, description="strong")
