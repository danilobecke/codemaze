from flask_restx import Api, Resource, Namespace, fields
from flask import request, abort, jsonify
from services.group_service import GroupService
from helpers.role import Role
from helpers.exceptions import *
from endpoints.authenticator_decorator import authentication_required
from endpoints.models.user import UserVO

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

_get_groups_model = _namespace.model('Get Groups', {
    'member_of': fields.Boolean(required=True)
})

_manage_group_model = _namespace.model('Manage Group', {
    'active': fields.Boolean(required=True)
})

_join_group_model = _namespace.model('Create Join Request', {
     'code': fields.String(required=True)
})

_join_request_model = _namespace.model('Join Request', {
    'id': fields.Integer(required=True),
    'student': fields.String(required=True)
})

_manage_request_model = _namespace.model('Manage Request', {
    'approve': fields.Boolean(required=True)
})

class GroupsResource(Resource):
    _group_service: GroupService | None = None

    @_namespace.doc(description="*Managers only*\nCreate a new group.")
    @_namespace.expect(_new_group_model, validate=True)
    @_namespace.param('Authorization', 'Bearer {JWT}', 'header')
    @_namespace.response(401, 'Error')
    @_namespace.response(500, 'Error')
    @_namespace.marshal_with(_group_model)
    @authentication_required(Role.MANAGER)
    def post(self, user: UserVO):
        name = request.json['name']
        try:
            return GroupsResource._group_service.create(name, user.id)
        except Exception as e:
                abort(500, str(e))

    @_namespace.doc(description="Get all groups. If `member_of = true`, get all groups where the current user is either a manager or a student.")
    @_namespace.expect(_get_groups_model, validate=True)
    @_namespace.param('Authorization', 'Bearer {JWT}', 'header')
    @_namespace.response(401, 'Error')
    @_namespace.response(500, 'Error')
    @_namespace.marshal_with(_group_model, as_list=True, envelope='groups')
    @authentication_required()
    def get(self, user: UserVO):
        member_of = request.json['member_of']
        try:
            return GroupsResource._group_service.get_all(user if member_of else None)
        except Exception as e:
            abort(500, str(e))

class GroupResource(Resource):
    _group_service: GroupService | None = None

    @_namespace.doc(description="*Managers only*\nUpdate the group `active` status.")
    @_namespace.expect(_manage_group_model, validate=True)
    @_namespace.param('Authorization', 'Bearer {JWT}', 'header')
    @_namespace.response(200, 'Success')
    @_namespace.response(401, 'Error')
    @_namespace.response(403, 'Error')
    @_namespace.response(404, 'Error')
    @_namespace.response(500, 'Error')
    @authentication_required(Role.MANAGER)
    def patch(self, id: int, user: UserVO):
        active = request.json['active']
        try:
            GroupResource._group_service.update_group_active(id, user.id, active)
            return jsonify(message='Success')
        except Forbidden as e:
            abort(403, str(e))
        except NotFound as e:
            abort(404, str(e))
        except ServerError as e:
            abort(500, str(e))

class JoinResource(Resource):
    _group_service: GroupService | None = None

    @_namespace.doc(description="*Students only*\nAsk to join a group.")
    @_namespace.expect(_join_group_model, validate=True)
    @_namespace.param('Authorization', 'Bearer {JWT}', 'header')
    @_namespace.response(200, 'Success')
    @_namespace.response(401, 'Error')
    @_namespace.response(404, 'Error')
    @_namespace.response(409, 'Error')
    @_namespace.response(500, 'Error')
    @authentication_required(Role.STUDENT)
    def post(self, user: UserVO):
         code = request.json['code']
         try:
            JoinResource._group_service.add_join_request(code, user.id)
            return jsonify(message='Success')
         except NotFound as e:
             abort(404, str(e))
         except Internal_UniqueViolation:
             abort(409, str(Conflict()))
         except Exception as e:
             abort(500, str(e))

class RequestsResource(Resource):
    _group_service: GroupService | None = None

    @_namespace.doc(description="*Managers only*\nRetrieve a list of join requests.")
    @_namespace.param('Authorization', 'Bearer {JWT}', 'header')
    @_namespace.response(401, 'Error')
    @_namespace.response(403, 'Error')
    @_namespace.response(404, 'Error')
    @_namespace.response(500, 'Error')
    @_namespace.marshal_with(_join_request_model, as_list=True, envelope="requests")
    @authentication_required(Role.MANAGER)
    def get(self, group_id: int, user: UserVO):
        try:
            return RequestsResource._group_service.get_students_with_join_request(group_id, user.id)
        except NotFound as e:
            abort(404, str(e))
        except Forbidden as e:
            abort(403, str(e))
        except Exception as e:
            abort(500, str(ServerError()))

class RequestResource(Resource):
    _group_service: GroupService | None = None

    @_namespace.doc(description="*Managers only*\nApprove or decline a join request.")
    @_namespace.expect(_manage_request_model, validate=True)
    @_namespace.param('Authorization', 'Bearer {JWT}', 'header')
    @_namespace.response(200, 'Success')
    @_namespace.response(401, 'Error')
    @_namespace.response(403, 'Error')
    @_namespace.response(404, 'Error')
    @_namespace.response(500, 'Error')
    @authentication_required(Role.MANAGER)
    def patch(self, group_id: int, id: int, user: UserVO):
        approve = request.json['approve']
        try:
            RequestResource._group_service.update_join_request(group_id, id, user.id, approve)
            return jsonify(message='Success')
        except NotFound as e:
            abort(404, str(e))
        except Forbidden as e:
            abort(403, str(e))
        except Exception as e:
            abort(500, str(ServerError()))

class GroupEndpoints:
    def __init__(self, api: Api, group_service: GroupService):
        api.add_namespace(_namespace)
        GroupsResource._group_service = group_service
        GroupResource._group_service = group_service
        JoinResource._group_service = group_service
        RequestsResource._group_service = group_service
        RequestResource._group_service = group_service

    def register_resources(self):
        _namespace.add_resource(GroupsResource, '')
        _namespace.add_resource(GroupResource, '/<int:id>')
        _namespace.add_resource(JoinResource, '/join')
        _namespace.add_resource(RequestsResource, '/<int:group_id>/requests')
        _namespace.add_resource(RequestResource, '/<int:group_id>/requests/<int:id>')