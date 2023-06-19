from flask import json
from app import run_as_test

__app = run_as_test()

__CONTENT_TYPE_JSON = 'application/json'
StatusCode = int
HTTPResponse = tuple[StatusCode, any]

def headers(token: str | None) -> dict[str, str] | None:
    if not token:
        return None
    return {"Authorization": f"Bearer {token}"}

def get(path: str, token: str | None = None) -> HTTPResponse:
    response = __app.get(path, headers=headers(token))
    return (response.status_code, json.loads(response.data.decode('utf-8')))

def post(path: str, payload: dict, token: str | None = None) -> HTTPResponse:
    response = __app.post(path, data=json.dumps(payload), content_type=__CONTENT_TYPE_JSON, headers=headers(token))
    return (response.status_code, json.loads(response.data.decode('utf-8')))

def patch(path: str, payload: dict, token: str | None = None) -> HTTPResponse:
    response = __app.patch(path, data=json.dumps(payload), content_type=__CONTENT_TYPE_JSON, headers=headers(token))
    return (response.status_code, json.loads(response.data.decode('utf-8')))