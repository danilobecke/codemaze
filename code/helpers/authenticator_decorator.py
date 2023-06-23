import re

from flask import request, abort

from helpers.exceptions import Unauthorized, NotFound, ServerError
from helpers.role import Role
from services.session_service import SessionService

_PATTERN = r'^Bearer ((?:\.?(?:[A-Za-z0-9-_]+)){3})$'

def authentication_required(role: Role | None = None):
    def decorator(function):
        def wrapper(*args, **kwargs):
            if 'Authorization' not in request.headers:
                abort(401, str(Unauthorized()))
            try:
                header = request.headers['Authorization']
                match = re.match(_PATTERN, header)
                if not match:
                    abort(401, str(Unauthorized()))
                token = match.group(1)
                user = SessionService.shared.validate_token(token, role)
                kwargs['user'] = user
                return function(*args, **kwargs)
            except (Unauthorized, NotFound):
                abort(401, str(Unauthorized()))
            except ServerError as e:
                abort(500, str(e))
        return wrapper
    return decorator
