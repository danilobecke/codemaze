import datetime
import os
import time
from typing import TypeAlias, Tuple, Any
import uuid

from flask import json
import jwt

from app import run_as_test

__app = run_as_test()

CONTENT_TYPE_JSON = 'application/json'
CONTENT_TYPE_FORM_DATA = 'multipart/form-data'
StatusCode: TypeAlias = int
HTTPResponse = Tuple[StatusCode, Any]

# HTTP METHODS

def __headers(token: str | None) -> dict[str, str] | None:
    if not token:
        return None
    return {'Authorization': f'Bearer {token}'}

def get(path: str, token: str | None = None, custom_headers: dict[str, str] | None = None, decode_as_json: bool = True) -> HTTPResponse:
    headers = __headers(token)
    if headers and custom_headers:
        headers.update(custom_headers)
    elif custom_headers:
        headers = custom_headers
    response = __app.get(path, headers=headers)
    data = response.data.decode('utf-8')
    if decode_as_json:
        data = json.loads(data)
    return (response.status_code, data)

def post(path: str, payload: dict, token: str | None = None, content_type: str = CONTENT_TYPE_JSON) -> HTTPResponse:
    data: Any | None = None
    if content_type == CONTENT_TYPE_JSON:
        data = json.dumps(payload)
    elif content_type == CONTENT_TYPE_FORM_DATA:
        data = payload
    else:
        assert 1 == -1
    response = __app.post(path, data=data, content_type=content_type, headers=__headers(token))
    return (response.status_code, json.loads(response.data.decode('utf-8')))

def patch(path: str, payload: dict, token: str | None = None) -> HTTPResponse:
    response = __app.patch(path, data=json.dumps(payload), content_type=CONTENT_TYPE_JSON, headers=__headers(token))
    return (response.status_code, json.loads(response.data.decode('utf-8')))

# DATABSE HELPERS

def get_random_name() -> str:
    return str(uuid.uuid1())

def get_manager_id_token() -> tuple[str, str]:
    manager_email = 'manager@email.com'
    manager_password = 'manager'

    login_payload = {
        'email': manager_email,
        'password': manager_password
    }
    response = post('/session', login_payload)
    if response[0] == 200:
        return (response[1]['id'], response[1]['token'])

    create_payload = {
        'name': 'Manager',
        'email': manager_email,
        'password': manager_password
    }
    response = post('/managers', create_payload)
    return (response[1]['id'], response[1]['token'])

def get_student_id_token() -> tuple[str, str]:
    student_email = 'student@email.com'
    student_password = 'student'

    login_payload = {
        'email': student_email,
        'password': student_password
    }
    response = post('/session', login_payload)
    if response[0] == 200:
        return (response[1]['id'], response[1]['token'])

    create_payload = {
        'name': 'Student',
        'email': student_email,
        'password': student_password
    }
    response = post('/students', create_payload)
    return (response[1]['id'], response[1]['token'])

def get_random_manager_token() -> str:
    random = get_random_name()
    payload = {
        'name': random,
        'email': f'{random}@email.com',
        'password': 'password'
    }
    response = post('/managers', payload)
    return response[1]['token']

def get_new_group_id_code(name: str, token: str) -> tuple[str, str]:
    payload = {
        'name': name
    }
    response = post('/groups', payload, token)
    return (response[1]['id'], response[1]['code'])

def create_expired_token(user_id: int) -> str:
    payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, hours=0, minutes=0, seconds=0, milliseconds=1),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id,
        }
    token = jwt.encode(payload, key=os.getenv('CODEMAZE_KEY'), algorithm='HS256')
    time.sleep(0.2) # expire the token
    return token

def create_join_request_group_id(student_token: str, manager_token: str, approve: bool = False):
    group_id, code = get_new_group_id_code(get_random_name(), manager_token)
    join_payload = {
        'code': code
    }
    post('groups/join', join_payload, student_token)
    if approve is False:
        return group_id

    request_id = get(f'groups/{group_id}/requests', manager_token)[1]['requests'][0]['id']
    approve_payload = {
        'approve': True
    }
    patch(f'/groups/{group_id}/requests/{request_id}', approve_payload, manager_token)
    return group_id
## Asserts

def assert_user_response(response: HTTPResponse, name: str, email: str, role: str):
    assert response[0] == 200
    data = response[1]
    assert data['id'] is not None
    assert data['name'] == name
    assert data['email'] == email
    assert data['role'] == role
    assert data['token'] is not None

## File helper

def get_filepath_of_size(size: int) -> str:
    full_path = os.path.join(__app.application.config['STORAGE_PATH'], get_random_name() + '.txt')
    with open(full_path, 'wb') as file:
        file.seek(size - 1)
        file.write(b'\0')
    return full_path
