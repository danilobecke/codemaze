from flask import abort
from flask_restx import Api, Resource, Namespace, fields

from endpoints.models.user import UserVO
from endpoints.session_endpoints import user_model
from helpers.email_validation_decorator import validate_email
from helpers.exceptions import ServerError, Internal_UniqueViolation, Conflict, Forbidden
from helpers.role import Role
from helpers.unwrapper import json_unwrapped, unwrap
from services.session_service import SessionService

_namespace = Namespace('managers', description='')

signup_model = _namespace.model('Sign Up', {
     'name': fields.String(required=True),
     'email': fields.String(required=True),
     'password': fields.String(required=True)
})

class ManagerResource(Resource): # type: ignore
    @_namespace.doc(description='Create a new manager.')
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
            return unwrap(SessionService.shared).create_user(email, name, password, Role.MANAGER), 201
        except Forbidden as e:
            abort(403, str(e))
        except Internal_UniqueViolation:
            abort(409, str(Conflict()))
        except ServerError as e:
            abort(500, str(e))

class ManagerEndpoints:
    def __init__(self, api: Api) -> None:
        api.add_namespace(_namespace)
        _namespace.add_model('User', user_model)

    def register_resources(self) -> None:
        _namespace.add_resource(ManagerResource, '')
