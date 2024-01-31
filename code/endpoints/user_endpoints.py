from flask import abort
from flask_restx import Api, Resource, Namespace, fields

from endpoints.models.user import UserVO
from helpers.authenticator_decorator import authentication_required
from helpers.exceptions import NotFound, ServerError
from helpers.unwrapper import json_unwrapped, unwrap
from services.session_service import SessionService

_namespace = Namespace('user', description='')

_update_user_model = _namespace.model('Update User', {
    'name': fields.String(required=False),
})

_user_info_model = _namespace.model('User Info', {
    'id': fields.Integer(required=True),
    'name': fields.String(required=True),
    'email': fields.String(required=True),
    'role': fields.String(required=True),
})

class UserResource(Resource): # type: ignore
    @_namespace.doc(description='Update user info.')
    @_namespace.expect(_update_user_model, validate=True)
    @_namespace.response(404, 'Error')
    @_namespace.response(500, 'Error')
    @_namespace.marshal_with(_user_info_model)
    @_namespace.doc(security='bearer')
    @authentication_required()
    def patch(self, user: UserVO) -> UserVO:
        updated_name: str | None = json_unwrapped().get('name')
        if updated_name is None or updated_name == user.name:
            return user
        try:
            return unwrap(SessionService.shared).update_user(user.id, updated_name)
        except NotFound as e:
            abort(404, str(e))
        except ServerError as e:
            abort(500, str(e))

class UserEndpoints:
    def __init__(self, api: Api):
        api.add_namespace(_namespace)

    def register_resources(self) -> None:
        _namespace.add_resource(UserResource, '')
