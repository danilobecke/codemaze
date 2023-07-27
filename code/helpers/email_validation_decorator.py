import re

from flask import abort

from helpers.exceptions import ParameterValidationError
from helpers.unwrapper import json_unwrapped

_PATTERN = r'^[\w\-\.]+@([\w\-]+\.)+[\w\-]{2,4}$'

def validate_email(key: str = 'email'):
    def decorator(function):
        def wrapper(*args, **kwargs):
            email = json_unwrapped()[key]
            if not re.findall(_PATTERN, email):
                abort(400, str(ParameterValidationError(key, email, 'email')))
            return function(*args, **kwargs)
        return wrapper
    return decorator
