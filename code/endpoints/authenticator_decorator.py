import re
from flask import request, abort
from services.session_service import SessionService
from helpers.role import Role
from helpers.exceptions import *

_PATTERN = "^Bearer ((?:\.?(?:[A-Za-z0-9-_]+)){3})$"

def authentication_required(role: Role | None = None):
    def decorator(function):
        def wrapper(*args, **kwargs):
            if "Authorization" not in request.headers:
                abort(401, str(Unauthorized())) 
            try:
                header = request.headers["Authorization"]
                token = re.match(_PATTERN, header).group(1)
                user = SessionService.shared.validate_token(token, role)
                kwargs['user'] = user
                return function(*args, **kwargs)
            except (Unauthorized, NotFound) as e:
                abort(401, str(Unauthorized()))
            except ServerError as e:
                abort(500, str(e))
        return wrapper
    return decorator