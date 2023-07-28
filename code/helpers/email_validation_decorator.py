import re
from typing import Callable, TypeVar, Any

from flask import abort

from helpers.exceptions import ParameterValidationError
from helpers.unwrapper import json_unwrapped

RT = TypeVar('RT')

_PATTERN = r'^[\w\-\.]+@([\w\-]+\.)+[\w\-]{2,4}$'

def validate_email(key: str = 'email') -> Callable[[Callable[..., RT]], Callable[..., RT]]:
    def decorator(function: Callable[..., RT]) -> Callable[..., RT]:
        def wrapper(*args: Any, **kwargs: Any) -> RT:
            email = json_unwrapped()[key]
            if not re.findall(_PATTERN, email):
                abort(400, str(ParameterValidationError(key, email, 'email')))
            return function(*args, **kwargs)
        return wrapper
    return decorator
