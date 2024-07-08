from typing import Callable, TypeVar, Any

from flask import request, abort

from helpers.exceptions import Unauthorized, NotFound, ServerError
from helpers.role import Role
from helpers.unwrapper import unwrap
from services.session_service import SessionService

RT = TypeVar('RT')

def authentication_required(role: Role | None = None) -> Callable[[Callable[..., RT]], Callable[..., RT]]:
    def decorator(function: Callable[..., RT]) -> Callable[..., RT]:
        def wrapper(*args: Any, **kwargs: Any) -> RT:
            authorization = request.authorization
            if not authorization:
                abort(401, str(Unauthorized()))
            token = authorization.token
            if authorization.type != 'bearer' or not token:
                abort(401, str(Unauthorized()))
            try:
                user = unwrap(SessionService.shared).validate_session_token(token, role)
                kwargs['user'] = user
                return function(*args, **kwargs)
            except (Unauthorized, NotFound):
                abort(401, str(Unauthorized()))
            except ServerError as e:
                abort(500, str(e))
        return wrapper
    return decorator
