from flask import abort
from flask_restx import Api, Resource, Namespace

from endpoints.manager_endpoints import signup_model
from endpoints.session_endpoints import user_model
from helpers.email_validation_decorator import validate_email
from helpers.exceptions import ServerError
from helpers.role import Role
from helpers.unwrapper import json_unwrapped, unwrap
from services.session_service import SessionService

_namespace = Namespace('students', description='')

class StudentResource(Resource):
    @_namespace.doc(description='Create a new student.')
    @_namespace.expect(signup_model, validate=True)
    @_namespace.response(400, 'Error')
    @_namespace.response(500, 'Error')
    @_namespace.marshal_with(user_model, code=201)
    @validate_email()
    def post(self):
        name = json_unwrapped()['name']
        email = json_unwrapped()['email']
        password = json_unwrapped()['password']
        try:
            return unwrap(SessionService.shared).create_user(email, name, password, Role.STUDENT), 201
        except ServerError as e:
            abort(500, str(e))

class StudentEndpoints:
    def __init__(self, api: Api):
        api.add_namespace(_namespace)
        _namespace.add_model('User', user_model)
        _namespace.add_model('Sign Up', signup_model)

    def register_resources(self):
        _namespace.add_resource(StudentResource, '')
