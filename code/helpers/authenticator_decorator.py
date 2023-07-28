import re
from typing import Callable, TypeVar, Any

from flask import request, abort

from helpers.exceptions import Unauthorized, NotFound, ServerError
from helpers.role import Role
from helpers.unwrapper import unwrap
from services.session_service import SessionService

RT = TypeVar('RT')

_PATTERN = r'^Bearer ((?:\.?(?:[A-Za-z0-9-_]+)){3})$'

def authentication_required(role: Role | None = None) -> Callable[[Callable[..., RT]], Callable[..., RT]]:
    def decorator(function: Callable[..., RT]) -> Callable[..., RT]:
        def wrapper(*args: Any, **kwargs: Any) -> RT:
            if 'Authorization' not in request.headers:
                abort(401, str(Unauthorized()))
            try:
                header = request.headers['Authorization']
                match = re.match(_PATTERN, header)
                if not match:
                    abort(401, str(Unauthorized()))
                token = match.group(1)
                user = unwrap(SessionService.shared).validate_token(token, role)
                kwargs['user'] = user
                return function(*args, **kwargs)
            except (Unauthorized, NotFound):
                abort(401, str(Unauthorized()))
            except ServerError as e:
                abort(500, str(e))
        return wrapper
    return decorator
