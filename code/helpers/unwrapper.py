from typing import Optional, TypeVar, Mapping, Any

from flask import abort, request

from helpers.exceptions import ServerError

T = TypeVar('T')

def unwrap(optional: Optional[T]) -> T:
    if optional is None:
        abort(500, ServerError())
    return optional

def json_unwrapped() -> Mapping[str, Any]:
    return unwrap(request.json)
