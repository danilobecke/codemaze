# from flask import request, abort, jsonify
from flask_restx import Api, Resource, Namespace, inputs
from werkzeug.datastructures import FileStorage

from endpoints.models.user import UserVO
from helpers.authenticator_decorator import authentication_required
# from helpers.exceptions import ServerError, NotFound, Forbidden, Internal_UniqueViolation, Conflict
from helpers.role import Role
from services.group_service import GroupService

_namespace = Namespace('tasks', description='')

_new_task_parser = _namespace.parser()

def _set_up_parser():
    _new_task_parser.add_argument('name', type=str, required=True, location='form')
    _new_task_parser.add_argument('max_attempts', type=int, required=False, location='form')
    _new_task_parser.add_argument('starts_on', type=inputs.datetime_from_iso8601, required=False, location='form')
    _new_task_parser.add_argument('ends_on', type=inputs.datetime_from_iso8601, required=False, location='form')
    _new_task_parser.add_argument('file', type=FileStorage, required=True, location='files')

class TasksResource(Resource):
    _group_service: GroupService | None = None

    @_namespace.doc(description='*Managers only*\nAdd a new task to the group.')
    @_namespace.expect(_new_task_parser, validate=True)
    @_namespace.param('name', _in='formData', required=True)
    @_namespace.param('max_attempts', _in='formData', type=int)
    @_namespace.param('starts_on', _in='formData')
    @_namespace.param('ends_on', _in='formData')
    @_namespace.param('file', _in='formData', type='file', required=True)
    @_namespace.response(400, 'Error')
    @_namespace.response(401, 'Error')
    @_namespace.response(500, 'Error')
    @_namespace.doc(security='bearer')
    # @_namespace.marshal_with(_group_model)
    @authentication_required(Role.MANAGER)
    def post(self, group_id: int, user: UserVO):
        args = _new_task_parser.parse_args()
        name = args['name']
        max_attempts = args.get('max_attempts', None)
        starts_on = args.get('starts_on', None)
        ends_on = args.get('ends_on', None)
        file = args['file']

class TaskEndpoints:
    def __init__(self, api: Api, groups_namespace: Namespace, group_service: GroupService):
        _set_up_parser()
        api.add_namespace(_namespace)
        self.__groups_namespace = groups_namespace
        TasksResource._group_service = group_service

    def register_resources(self) -> Namespace:
        self.__groups_namespace.add_resource(TasksResource, '/<int:group_id>/tasks')
        return _namespace
