from flask import abort
from flask_restx import Api, Resource, Namespace, fields

from endpoints.models.user import UserVO
from helpers.email_validation_decorator import validate_email
from helpers.exceptions import Forbidden, ServerError
from helpers.unwrapper import json_unwrapped, unwrap
from services.session_service import SessionService

_namespace = Namespace('session', description='')

user_model = _namespace.model('User', {
     'id': fields.Integer(required=True),
     'name': fields.String(required=True),
     'email': fields.String(required=True),
     'role': fields.String(required=True),
     'token': fields.String(required=True)
})

_signin_model = _namespace.model('Sign In', {
     'email': fields.String(required=True),
     'password': fields.String(required=True)
})

class SessionResource(Resource): # type: ignore
    @_namespace.doc(description='Create a new session (log in).')
    @_namespace.expect(_signin_model, validate=True)
    @_namespace.response(400, 'Error')
    @_namespace.response(403, 'Credentials error')
    @_namespace.response(500, 'Server error')
    @_namespace.marshal_with(user_model)
    @validate_email()
    def post(self) -> UserVO:
        email = json_unwrapped()['email']
        password = json_unwrapped()['password']
        try:
            return unwrap(SessionService.shared).login(email, password)
        except Forbidden as e:
            abort(403, str(e))
        except ServerError as e:
            abort(500, str(e))

class SessionEndpoints:
    def __init__(self, api: Api):
        api.add_namespace(_namespace)

    def register_resources(self) -> None:
        _namespace.add_resource(SessionResource, '')
