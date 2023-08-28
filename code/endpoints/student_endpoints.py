from flask import abort
from flask_restx import Api, Resource, Namespace

from endpoints.manager_endpoints import signup_model
from endpoints.models.user import UserVO
from endpoints.session_endpoints import user_model
from helpers.email_validation_decorator import validate_email
from helpers.exceptions import ServerError, Internal_UniqueViolation, Conflict
from helpers.role import Role
from helpers.unwrapper import json_unwrapped, unwrap
from services.session_service import SessionService

_namespace = Namespace('students', description='')

class StudentResource(Resource): # type: ignore
    @_namespace.doc(description='Create a new student.')
    @_namespace.expect(signup_model, validate=True)
    @_namespace.response(400, 'Error')
    @_namespace.response(500, 'Error')
    @_namespace.marshal_with(user_model, code=201)
    @validate_email()
    def post(self) -> tuple[UserVO, int]:
        name = json_unwrapped()['name']
        email = json_unwrapped()['email']
        password = json_unwrapped()['password']
        try:
            return unwrap(SessionService.shared).create_user(email, name, password, Role.STUDENT), 201
        except Internal_UniqueViolation:
            abort(409, str(Conflict()))
        except ServerError as e:
            abort(500, str(e))

class StudentEndpoints:
    def __init__(self, api: Api) -> None:
        api.add_namespace(_namespace)
        _namespace.add_model('User', user_model)
        _namespace.add_model('Sign Up', signup_model)

    def register_resources(self) -> None:
        _namespace.add_resource(StudentResource, '')
