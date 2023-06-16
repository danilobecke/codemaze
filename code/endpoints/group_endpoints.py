from flask_restx import Api, Resource, Namespace, fields
from flask import request, abort
from services.group_service import GroupService
from helpers.role import Role
from helpers.exceptions import *
from endpoints.authenticator_decorator import authentication_required
from endpoints.models.user import UserVO
from typing import Self

_namespace = Namespace('groups', description='')

_new_group_model = _namespace.model('New Group', {
     'name': fields.String(required=True)
})

_group_model = _namespace.model('Group', {
     'id': fields.Integer(required=True),
     'name': fields.String(required=True),
     'active': fields.Boolean(required=True),
     'code': fields.String(required=True),
     'manager_id': fields.Integer(required=True)
})

class GroupResource(Resource):
        _group_service: GroupService | None = None

        @_namespace.doc(description="*Managers only*\nCreate a new group.")
        @_namespace.expect(_new_group_model, validate=True)
        @_namespace.response(200, 'Success', _group_model)
        @_namespace.response(201, 'Error')
        @_namespace.response(500, 'Error')
        @_namespace.marshal_with(_group_model)
        @authentication_required(Role.MANAGER)
        def post(self, user: UserVO):
            name = request.json['name']
            try:
                return GroupResource._group_service.create(name, user.id)
            except Exception as e:
                 abort(500, str(e))

class GroupEndpoints:
    def __init__(self, api: Api, group_service: GroupService):
        api.add_namespace(_namespace)
        GroupResource._group_service = group_service

    def register_resources(self):
        _namespace.add_resource(GroupResource, '')