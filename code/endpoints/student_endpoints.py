from flask_restx import Api, Resource, Namespace
from flask import request, abort
from services.session_service import SessionService
from helpers.role import Role
from endpoints.session_endpoints import user_model
from endpoints.manager_endpoints import signup_model
from helpers.exceptions import *

_namespace = Namespace('students', description='')

class StudentResource(Resource):
        @_namespace.doc(description="Create a new student.")
        @_namespace.expect(signup_model, validate=True)
        @_namespace.response(200, 'Success', user_model)
        @_namespace.response(500, 'Error')
        @_namespace.marshal_with(user_model)
        def post(self):
            name = request.json['name']
            email = request.json['email']
            password = request.json['password']
            try:
                return SessionService.shared.create_user(email, name, password, Role.STUDENT)
            except Exception as e:
                 abort(500, str(e))

class StudentEndpoints:
    def __init__(self, api: Api):
        api.add_namespace(_namespace)
        _namespace.add_model('User', user_model)
        _namespace.add_model('Sign Up', signup_model)

    def register_resources(self):
        _namespace.add_resource(StudentResource, '')