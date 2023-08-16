from flask import abort, send_file
from flask.wrappers import Response
from flask_restx import Api, Resource, Namespace, inputs, fields
from flask_restx.reqparse import RequestParser
from werkzeug.datastructures import FileStorage

from endpoints.tcase_endpoints import test_model
from endpoints.models.task_vo import TaskVO
from endpoints.models.user import UserVO
from helpers.authenticator_decorator import authentication_required
from helpers.exceptions import NotFound, ServerError, Forbidden, InvalidFileExtension, InvalidFileSize, ParameterValidationError
from helpers.file import File
from helpers.role import Role
from helpers.unwrapper import unwrap
from services.group_service import GroupService
from services.task_service import TaskService
from services.tcase_service import TCaseService

_namespace = Namespace('tasks', description='')

_new_task_parser = _namespace.parser()
_update_task_parser = _namespace.parser()

def _set_up_task_parser(parser: RequestParser, updating: bool) -> None:
    required = not updating
    parser.add_argument('name', type=str, required=required, location='form')
    parser.add_argument('max_attempts', type=int, required=False, location='form')
    parser.add_argument('languages', type=str, required=required, action='append', location='form')
    parser.add_argument('starts_on', type=inputs.datetime_from_iso8601, required=False, location='form')
    parser.add_argument('ends_on', type=inputs.datetime_from_iso8601, required=False, location='form')
    parser.add_argument('file', type=FileStorage, required=required, location='files')

_task_model = _namespace.model('Task', {
    'id': fields.String(required=True),
    'name': fields.String(required=True),
    'max_attempts': fields.Integer,
    'languages': fields.List(fields.String),
    'starts_on': fields.DateTime(required=True),
    'ends_on': fields.DateTime,
    'file_url': fields.String(required=True),
}, skipNone=True)

_task_details_model = _task_model.inherit('Task Details', {
    'open_tests': fields.Nested(test_model, as_list=True, skip_none=True, required=False),
    'closed_tests': fields.Nested(test_model, as_list=True, skip_none=True, required=False)
})

class TasksResource(Resource): # type: ignore
    _group_service: GroupService | None = None
    _task_service: TaskService | None = None

    @_namespace.doc(description='*Managers only*\nAdd a new task to the group.')
    @_namespace.expect(_new_task_parser, validate=True)
    @_namespace.param('name', _in='formData', required=True)
    @_namespace.param('max_attempts', _in='formData', type=int)
    @_namespace.param('languages', _in='formData', description='Array with languanges.')
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
    @_namespace.marshal_with(_task_model, code=201)
    @authentication_required(Role.MANAGER)
    def post(self, group_id: int, user: UserVO) -> tuple[TaskVO, int]:
        args = _new_task_parser.parse_args()
        name = args['name']
        max_attempts = args.get('max_attempts')
        languages = args['languages']
        starts_on = args.get('starts_on')
        ends_on = args.get('ends_on')
        file_storage: FileStorage = args['file']
        filename = unwrap(file_storage.filename)
        blob = file_storage.stream.read()
        try:
            group = unwrap(TasksResource._group_service).get_group(group_id)
            return unwrap(TasksResource._task_service).create_task(user, group, name, max_attempts, languages, starts_on, ends_on, File(filename, blob)), 201
        except ParameterValidationError as e:
            abort(400, str(e))
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

    @_namespace.doc(description='Returns a list of tasks for the current group.')
    @_namespace.response(401, 'Error')
    @_namespace.response(403, 'Error')
    @_namespace.response(404, 'Error')
    @_namespace.response(500, 'Error')
    @_namespace.doc(security='bearer')
    @_namespace.marshal_with(_task_model, as_list=True, envelope='tasks')
    @authentication_required()
    def get(self, group_id: int, user: UserVO) -> list[TaskVO]:
        try:
            group = unwrap(TasksResource._group_service).get_group(group_id)
            user_groups = unwrap(TasksResource._group_service).get_all(user)
            return unwrap(TasksResource._task_service).get_tasks(user.id, group, user_groups)
        except Forbidden as e:
            abort(403, str(e))
        except NotFound as e:
            abort(404, str(e))
        except ServerError as e:
            abort(500, str(e))

class TaskDownloadResource(Resource): # type: ignore
    _group_service: GroupService | None = None
    _task_service: TaskService | None = None

    @_namespace.doc(description='Downloads the task.')
    @_namespace.response(401, 'Error')
    @_namespace.response(403, 'Error')
    @_namespace.response(404, 'Error')
    @_namespace.response(500, 'Error')
    @_namespace.doc(security='bearer')
    @authentication_required()
    def get(self, id: int, user: UserVO) -> Response:
        try:
            user_groups = unwrap(TaskDownloadResource._group_service).get_all(user)
            name, path = unwrap(TaskDownloadResource._task_service).get_task_name_path(id, user_groups, user.id)
            return send_file(path, download_name=name)
        except Forbidden as e:
            abort(403, str(e))
        except NotFound as e:
            abort(404, str(e))
        except ServerError as e:
            abort(500, str(e))

class TaskResource(Resource): # type: ignore
    _group_service: GroupService | None = None
    _task_service: TaskService | None = None
    _tcase_service: TCaseService | None = None

    @_namespace.doc(description='*Managers only*\nUpdates a task.')
    @_namespace.expect(_update_task_parser, validate=True)
    @_namespace.param('name', _in='formData')
    @_namespace.param('max_attempts', _in='formData', type=int)
    @_namespace.param('languages', _in='formData', description='Array with languanges.')
    @_namespace.param('starts_on', _in='formData')
    @_namespace.param('ends_on', _in='formData')
    @_namespace.param('file', _in='formData', type='file')
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
    def patch(self, id: int, user: UserVO) -> TaskVO:
        args = _update_task_parser.parse_args()
        name = args['name']
        max_attempts = args.get('max_attempts')
        languages = args['languages']
        starts_on = args.get('starts_on')
        ends_on = args.get('ends_on')
        file: File | None = None
        file_storage: FileStorage | None = args['file']
        if file_storage is not None:
            file = File(unwrap(file_storage.filename), file_storage.stream.read())
        try:
            return unwrap(TaskResource._task_service).update_task(user, unwrap(TaskResource._group_service).get_group, id, name, max_attempts, languages, starts_on, ends_on, file)
        except ParameterValidationError as e:
            abort(400, str(e))
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

    @_namespace.doc(description='Returns the details for the given task - test cases included.')
    @_namespace.response(401, 'Error')
    @_namespace.response(403, 'Error')
    @_namespace.response(404, 'Error')
    @_namespace.response(500, 'Error')
    @_namespace.marshal_with(_task_details_model)
    @_namespace.doc(security='bearer')
    @authentication_required()
    def get(self, id: int, user: UserVO) -> TaskVO:
        try:
            user_groups = unwrap(TaskResource._group_service).get_all(user)
            task = unwrap(TaskResource._task_service).get_task(id, user.id, user_groups, active_required=False)
            tests = unwrap(TaskResource._tcase_service).get_tests(user.id, task, user_groups)
            return task.appending_tests(tests)
        except Forbidden as e:
            abort(403, str(e))
        except NotFound as e:
            abort(404, str(e))
        except ServerError as e:
            abort(500, str(e))

class TaskEndpoints:
    def __init__(self, api: Api, groups_namespace: Namespace, group_service: GroupService, task_service: TaskService, tcase_service: TCaseService) -> None:
        _set_up_task_parser(_new_task_parser, updating=False)
        _set_up_task_parser(_update_task_parser, updating=True)
        _namespace.add_model('Task Details', _task_details_model)
        api.add_namespace(_namespace)
        self.__groups_namespace = groups_namespace
        TasksResource._group_service = group_service
        TasksResource._task_service = task_service
        TaskDownloadResource._group_service = group_service
        TaskDownloadResource._task_service = task_service
        TaskResource._group_service = group_service
        TaskResource._task_service = task_service
        TaskResource._tcase_service = tcase_service

    def register_resources(self) -> Namespace:
        self.__groups_namespace.add_resource(TasksResource, '/<int:group_id>/tasks')
        _namespace.add_resource(TaskDownloadResource, '/<int:id>/task')
        _namespace.add_resource(TaskResource, '/<int:id>')
        return _namespace
