import datetime
import os
import time
from typing import TypeAlias, Tuple, Any
import uuid

from flask import json
import jwt

from app import run_as_test

__app = run_as_test()

__CONTENT_TYPE_JSON = 'application/json'
StatusCode: TypeAlias = int
HTTPResponse = Tuple[StatusCode, Any]

# HTTP METHODS

def __headers(token: str | None) -> dict[str, str] | None:
    if not token:
        return None
    return {'Authorization': f'Bearer {token}'}

def get(path: str, token: str | None = None, custom_headers: dict[str, str] | None = None) -> HTTPResponse:
    headers = __headers(token)
    if headers and custom_headers:
        headers.update(custom_headers)
    elif custom_headers:
        headers = custom_headers
    response = __app.get(path, headers=headers)
    return (response.status_code, json.loads(response.data.decode('utf-8')))

def post(path: str, payload: dict, token: str | None = None) -> HTTPResponse:
    response = __app.post(path, data=json.dumps(payload), content_type=__CONTENT_TYPE_JSON, headers=__headers(token))
    return (response.status_code, json.loads(response.data.decode('utf-8')))

def patch(path: str, payload: dict, token: str | None = None) -> HTTPResponse:
    response = __app.patch(path, data=json.dumps(payload), content_type=__CONTENT_TYPE_JSON, headers=__headers(token))
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

## Asserts

def assert_user_response(response: HTTPResponse, name: str, email: str, role: str):
    assert response[0] == 200
    data = response[1]
    assert data['id'] is not None
    assert data['name'] == name
    assert data['email'] == email
    assert data['role'] == role
    assert data['token'] is not None
