# pylint: disable=duplicate-code

from flask import request, abort
from flask_restx import Api, Resource, Namespace, fields

from endpoints.models.group import GroupVO
from endpoints.models.join_request import JoinRequestVO
from endpoints.models.user import UserVO
from helpers.authenticator_decorator import authentication_required
from helpers.exceptions import ServerError, NotFound, Forbidden, Internal_UniqueViolation, Conflict
from helpers.role import Role
from helpers.unwrapper import unwrap, json_unwrapped
from services.group_service import GroupService
from services.session_service import SessionService

_namespace = Namespace('groups', description='')

_new_group_model = _namespace.model('New Group', {
     'name': fields.String(required=True)
})

_public_user_model = _namespace.model('Public User', {
    'name': fields.String(required=True),
    'email': fields.String(required=True)
})

_group_model = _namespace.model('Group', {
     'id': fields.Integer(required=True),
     'name': fields.String(required=True),
     'active': fields.Boolean(required=True),
     'code': fields.String(required=True),
     'manager': fields.Nested(_public_user_model)
})

_update_group_model = _namespace.model('Update Group', {
    'name': fields.String(required=False),
    'active': fields.Boolean(required=False)
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

success_model = _namespace.model('Success', {
    'message': fields.String(required=True)
})

class GroupsResource(Resource): # type: ignore
    _group_service: GroupService | None = None

    @_namespace.doc(description='*Managers only*\nCreate a new group.')
    @_namespace.expect(_new_group_model, validate=True)
    @_namespace.response(400, 'Error')
    @_namespace.response(401, 'Error')
    @_namespace.response(500, 'Error')
    @_namespace.marshal_with(_group_model, code=201)
    @_namespace.doc(security='bearer')
    @authentication_required(Role.MANAGER)
    def post(self, user: UserVO) -> tuple[GroupVO, int]:
        name = json_unwrapped()['name']
        try:
            return unwrap(GroupsResource._group_service).create(name, user), 201
        except ServerError as e:
            abort(500, str(e))

    @_namespace.doc(description='Get all groups. If `member_of = true`, get all groups where the current user is either a manager or a student.')
    @_namespace.param('member_of', 'true or false', 'query')
    @_namespace.response(401, 'Error')
    @_namespace.response(500, 'Error')
    @_namespace.marshal_with(_group_model, as_list=True, envelope='groups')
    @_namespace.doc(security='bearer')
    @authentication_required()
    def get(self, user: UserVO) -> list[GroupVO]:
        raw_member_of = request.args.get('member_of')
        member_of = False
        if raw_member_of:
            match raw_member_of:
                case 'true' | 'True':
                    member_of = True
                case 'false' | 'False':
                    member_of = False
        try:
            return unwrap(GroupsResource._group_service).get_all(user if member_of else None, unwrap(SessionService.shared).get_user)
        except ServerError as e:
            abort(500, str(e))

class GroupResource(Resource): # type: ignore
    _group_service: GroupService | None = None

    @_namespace.doc(description='*Managers only*\nUpdate the group `active` status and/or `name`.')
    @_namespace.expect(_update_group_model, validate=True)
    @_namespace.response(400, 'Error')
    @_namespace.response(401, 'Error')
    @_namespace.response(403, 'Error')
    @_namespace.response(404, 'Error')
    @_namespace.response(500, 'Error')
    @_namespace.marshal_with(_group_model)
    @_namespace.doc(security='bearer')
    @authentication_required(Role.MANAGER)
    def patch(self, id: int, user: UserVO) -> GroupVO:
        active: bool | None = json_unwrapped().get('active')
        name: str | None = json_unwrapped().get('name')
        try:
            return unwrap(GroupResource._group_service).update_group(id, user, active, name)
        except Forbidden as e:
            abort(403, str(e))
        except NotFound as e:
            abort(404, str(e))
        except ServerError as e:
            abort(500, str(e))

    # pylint: disable=unused-argument
    @_namespace.doc(description='Get info about a group.')
    @_namespace.response(401, 'Error')
    @_namespace.response(404, 'Error')
    @_namespace.response(500, 'Error')
    @_namespace.marshal_with(_group_model)
    @_namespace.doc(security='bearer')
    @authentication_required()
    def get(self, id: int, user: UserVO) -> GroupVO:
        try:
            return unwrap(GroupResource._group_service).get_group(id, unwrap(SessionService.shared).get_user)
        except NotFound as e:
            abort(404, str(e))
        except ServerError as e:
            abort(500, str(e))

class JoinResource(Resource): # type: ignore
    _group_service: GroupService | None = None

    @_namespace.doc(description='*Students only*\nAsk to join a group.')
    @_namespace.expect(_join_group_model, validate=True)
    @_namespace.response(400, 'Error')
    @_namespace.response(401, 'Error')
    @_namespace.response(403, 'Error')
    @_namespace.response(404, 'Error')
    @_namespace.response(409, 'Error')
    @_namespace.response(500, 'Error')
    @_namespace.marshal_with(success_model)
    @_namespace.doc(security='bearer')
    @authentication_required(Role.STUDENT)
    def post(self, user: UserVO) -> dict[str, str]:
        code = json_unwrapped()['code']
        try:
            unwrap(JoinResource._group_service).add_join_request(code, user.id)
            return {'message': 'Success'}
        except Forbidden as e:
            abort(403, str(e))
        except NotFound as e:
            abort(404, str(e))
        except Internal_UniqueViolation:
            abort(409, str(Conflict()))
        except ServerError as e:
            abort(500, str(e))

class RequestsResource(Resource): # type: ignore
    _group_service: GroupService | None = None

    @_namespace.doc(description='*Managers only*\nRetrieve a list of join requests.')
    @_namespace.response(401, 'Error')
    @_namespace.response(403, 'Error')
    @_namespace.response(404, 'Error')
    @_namespace.response(500, 'Error')
    @_namespace.marshal_with(_join_request_model, as_list=True, envelope='requests')
    @_namespace.doc(security='bearer')
    @authentication_required(Role.MANAGER)
    def get(self, group_id: int, user: UserVO) -> list[JoinRequestVO]:
        try:
            return unwrap(RequestsResource._group_service).get_students_with_join_request(group_id, user.id)
        except NotFound as e:
            abort(404, str(e))
        except Forbidden as e:
            abort(403, str(e))
        except ServerError as e:
            abort(500, str(e))

class RequestResource(Resource): # type: ignore
    _group_service: GroupService | None = None

    @_namespace.doc(description='*Managers only*\nApprove or decline a join request.')
    @_namespace.expect(_manage_request_model, validate=True)
    @_namespace.response(400, 'Error')
    @_namespace.response(401, 'Error')
    @_namespace.response(403, 'Error')
    @_namespace.response(404, 'Error')
    @_namespace.response(500, 'Error')
    @_namespace.marshal_with(success_model)
    @_namespace.doc(security='bearer')
    @authentication_required(Role.MANAGER)
    def patch(self, group_id: int, id: int, user: UserVO) -> dict[str, str]:
        approve = json_unwrapped()['approve']
        try:
            unwrap(RequestResource._group_service).update_join_request(group_id, id, user.id, approve)
            return {'message': 'Success'}
        except NotFound as e:
            abort(404, str(e))
        except Forbidden as e:
            abort(403, str(e))
        except ServerError as e:
            abort(500, str(e))

class GroupStudentResource(Resource): # type: ignore
    _group_service: GroupService | None = None

    @_namespace.doc(description='*Managers only*\nGet a students\' list of the current group.')
    @_namespace.response(401, 'Error')
    @_namespace.response(403, 'Error')
    @_namespace.response(404, 'Error')
    @_namespace.response(500, 'Error')
    @_namespace.marshal_with(_public_user_model, as_list=True, envelope='students')
    @_namespace.doc(security='bearer')
    @authentication_required(Role.MANAGER)
    def get(self, group_id: int, user: UserVO) -> list[UserVO]:
        try:
            return unwrap(GroupStudentResource._group_service).get_students_of_group(group_id, user.id)
        except NotFound as e:
            abort(404, str(e))
        except Forbidden as e:
            abort(403, str(e))
        except ServerError as e:
            abort(500, str(e))

class GroupEndpoints:
    def __init__(self, api: Api, group_service: GroupService) -> None:
        api.add_namespace(_namespace)
        GroupsResource._group_service = group_service
        GroupResource._group_service = group_service
        JoinResource._group_service = group_service
        RequestsResource._group_service = group_service
        RequestResource._group_service = group_service
        GroupStudentResource._group_service = group_service

    def register_resources(self) -> Namespace:
        _namespace.add_resource(GroupsResource, '')
        _namespace.add_resource(GroupResource, '/<int:id>')
        _namespace.add_resource(JoinResource, '/join')
        _namespace.add_resource(RequestsResource, '/<int:group_id>/requests')
        _namespace.add_resource(RequestResource, '/<int:group_id>/requests/<int:id>')
        _namespace.add_resource(GroupStudentResource, '/<int:group_id>/students')
        return _namespace
