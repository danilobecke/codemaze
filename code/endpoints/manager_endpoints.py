from flask_restx import Api, Resource, Namespace, fields
from flask import request, abort
from services.session_service import SessionService
from helpers.role import Role
from endpoints.session_endpoints import user_model
from helpers.exceptions import *
from helpers.email_validation_decorator import validate_email

_namespace = Namespace('managers', description='')

signup_model = _namespace.model('Sign Up', {
     'name': fields.String(required=True),
     'email': fields.String(required=True),
     'password': fields.String(required=True)
})

class ManagerResource(Resource):
        @_namespace.doc(description="Create a new manager.")
        @_namespace.expect(signup_model, validate=True)
        @_namespace.response(500, 'Error')
        @_namespace.marshal_with(user_model)
        @validate_email()
        def post(self):
            name = request.json['name']
            email = request.json['email']
            password = request.json['password']
            try:
                return SessionService.shared.create_user(email, name, password, Role.MANAGER)
            except ServerError as e:
                 abort(500, str(e))

class ManagerEndpoints:
    def __init__(self, api: Api):
        api.add_namespace(_namespace)
        _namespace.add_model('User', user_model)

    def register_resources(self):
        _namespace.add_resource(ManagerResource, '')