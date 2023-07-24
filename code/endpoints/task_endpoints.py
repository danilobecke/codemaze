from flask import abort, send_file
from flask_restx import Api, Resource, Namespace, inputs, fields
from werkzeug.datastructures import FileStorage

from endpoints.models.user import UserVO
from helpers.authenticator_decorator import authentication_required
from helpers.exceptions import ParameterValidationError, NotFound, ServerError, Forbidden, InvalidFileExtension, InvalidFileSize
from helpers.role import Role
from helpers.unwrapper import unwrap
from services.group_service import GroupService
from services.task_service import TaskService

_namespace = Namespace('tasks', description='')

_new_task_parser = _namespace.parser()

def _set_up_parser():
    _new_task_parser.add_argument('name', type=str, required=True, location='form')
    _new_task_parser.add_argument('max_attempts', type=int, required=False, location='form')
    _new_task_parser.add_argument('starts_on', type=inputs.datetime_from_iso8601, required=False, location='form')
    _new_task_parser.add_argument('ends_on', type=inputs.datetime_from_iso8601, required=False, location='form')
    _new_task_parser.add_argument('file', type=FileStorage, required=True, location='files')

_task_model = _namespace.model('Task', {
    'id': fields.String(required=True),
    'name': fields.String(required=True),
    'max_attempts': fields.Integer,
    'starts_on': fields.DateTime(required=True),
    'ends_on': fields.DateTime,
    'file_url': fields.String(required=True),
})

class TasksResource(Resource):
    _group_service: GroupService | None = None
    _task_service: TaskService | None = None

    @_namespace.doc(description='*Managers only*\nAdd a new task to the group.')
    @_namespace.expect(_new_task_parser, validate=True)
    @_namespace.param('name', _in='formData', required=True)
    @_namespace.param('max_attempts', _in='formData', type=int)
    @_namespace.param('starts_on', _in='formData')
    @_namespace.param('ends_on', _in='formData')
    @_namespace.param('file', _in='formData', type='file', required=True)
    @_namespace.response(400, 'Error')
    @_namespace.response(401, 'Error')
    @_namespace.response(403, 'Error')
    @_namespace.response(404, 'Error')
    @_namespace.response(413, 'Error')
    @_namespace.response(422, 'Error')
    @_namespace.response(500, 'Error')
    @_namespace.doc(security='bearer')
    @_namespace.marshal_with(_task_model)
    @authentication_required(Role.MANAGER)
    def post(self, group_id: int, user: UserVO):
        args = _new_task_parser.parse_args()
        name = args['name']
        max_attempts = args.get('max_attempts')
        starts_on = args.get('starts_on')
        ends_on = args.get('ends_on')
        file_storage: FileStorage = args['file']
        filename = file_storage.filename
        if filename is None:
            abort(400, str(ParameterValidationError('filename', 'None', 'filename')))
        blob = file_storage.stream.read()
        try:
            group = unwrap(TasksResource._group_service).get_group(group_id)
            return unwrap(TasksResource._task_service).create_task(user, group, name, max_attempts, starts_on, ends_on, filename, blob)
        except Forbidden as e:
            abort(403, str(e))
        except NotFound as e:
            abort(404, str(e))
        except InvalidFileSize as e:
            abort(413, str(e))
        except InvalidFileExtension as e:
            abort(422, str(e))
        except ServerError as e:
            abort(500, str(e))

class TaskDownloadResource(Resource):
    _group_service: GroupService | None = None
    _task_service: TaskService | None = None

    @_namespace.doc(description='Downloads the task.')
    @_namespace.response(401, 'Error')
    @_namespace.response(403, 'Error')
    @_namespace.response(404, 'Error')
    @_namespace.response(500, 'Error')
    @_namespace.doc(security='bearer')
    @authentication_required()
    def get(self, id: int, user: UserVO):
        try:
            user_groups = unwrap(TaskDownloadResource._group_service).get_all(user)
            name, path = unwrap(TaskDownloadResource._task_service).get_task_name_path(id, user, user_groups)
            return send_file(path, download_name=name)
        except Forbidden as e:
            abort(403, str(e))
        except NotFound as e:
            abort(404, str(e))
        except ServerError as e:
            abort(500, str(e))

class TaskEndpoints:
    def __init__(self, api: Api, groups_namespace: Namespace, group_service: GroupService, task_service: TaskService):
        _set_up_parser()
        api.add_namespace(_namespace)
        self.__groups_namespace = groups_namespace
        TasksResource._group_service = group_service
        TasksResource._task_service = task_service
        TaskDownloadResource._group_service = group_service
        TaskDownloadResource._task_service = task_service

    def register_resources(self) -> Namespace:
        self.__groups_namespace.add_resource(TasksResource, '/<int:group_id>/tasks')
        _namespace.add_resource(TaskDownloadResource, '/<int:id>/task')
        return _namespace
