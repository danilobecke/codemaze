from flask import abort, send_file
from flask.wrappers import Response
from flask_restx import Api, Namespace, Resource, inputs, fields
from flask_restx.reqparse import RequestParser
from werkzeug.datastructures import FileStorage

from endpoints.models.tcase_vo import TCaseVO
from endpoints.models.user import UserVO
from helpers.authenticator_decorator import authentication_required
from helpers.exceptions import Forbidden, NotFound, ServerError, InvalidFileSize, InvalidFileExtension
from helpers.file import File
from helpers.role import Role
from helpers.unwrapper import unwrap
from services.group_service import GroupService
from services.task_service import TaskService
from services.tcase_service import TCaseService

_namespace = Namespace('tests', description='')

_new_test_parser = _namespace.parser()

def _set_up_test_parser(parser: RequestParser) -> None:
    parser.add_argument('input', type=FileStorage, required=True, location='files')
    parser.add_argument('output', type=FileStorage, required=True, location='files')
    parser.add_argument('closed', type=inputs.boolean, required=True, location='form')

test_model = _namespace.model('Test Case', {
    'id': fields.Integer(required=True),
    'closed': fields.Boolean(required=True),
    'input_url': fields.String(required=False),
    'output_url': fields.String(required=False)
})

class TestsResource(Resource): # type: ignore
    _group_service: GroupService | None
    _task_service: TaskService | None
    _tcase_service: TCaseService | None

    @_namespace.doc(description='*Managers only*\nAdd a new test case to the task.')
    @_namespace.expect(_new_test_parser, validate=True)
    @_namespace.param('input', _in='formData', type='file', required=True)
    @_namespace.param('output', _in='formData', type='file', required=True)
    @_namespace.param('closed', _in='formData', type=bool, required=True)
    @_namespace.response(400, 'Error')
    @_namespace.response(401, 'Error')
    @_namespace.response(403, 'Error')
    @_namespace.response(404, 'Error')
    @_namespace.response(500, 'Error')
    @_namespace.marshal_with(test_model, code=201)
    @_namespace.doc(security='bearer')
    @authentication_required(Role.MANAGER)
    def post(self, task_id: int, user: UserVO) -> tuple[TCaseVO, int]:
        args = _new_test_parser.parse_args()
        input_storage: FileStorage = args['input']
        output_storage: FileStorage = args['output']
        closed = args['closed']
        try:
            user_groups = unwrap(TestsResource._group_service).get_all(user)
            task = unwrap(TestsResource._task_service).get_task(task_id, user_groups)
            input_file = File(unwrap(input_storage.filename), input_storage.stream.read())
            output_file = File(unwrap(output_storage.filename), output_storage.stream.read())
            return unwrap(TestsResource._tcase_service).add_test_case(task, input_file, output_file, closed), 201
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

    @_namespace.doc(description='Returns a list of tests for the current task.')
    @_namespace.response(401, 'Error')
    @_namespace.response(403, 'Error')
    @_namespace.response(404, 'Error')
    @_namespace.response(500, 'Error')
    @_namespace.marshal_with(test_model, as_list=True, envelope='tests')
    @_namespace.doc(security='bearer')
    @authentication_required()
    def get(self, task_id: int, user: UserVO) -> list[TCaseVO]:
        try:
            user_groups = unwrap(TestsResource._group_service).get_all(user)
            task = unwrap(TestsResource._task_service).get_task(task_id, user_groups)
            return unwrap(TestsResource._tcase_service).get_tests(user.id, task, user_groups)
        except Forbidden as e:
            abort(403, str(e))
        except NotFound as e:
            abort(404, str(e))
        except ServerError as e:
            abort(500, str(e))

class TestDownloadInResource(Resource): # type: ignore
    _group_service: GroupService | None
    _task_service: TaskService | None
    _tcase_service: TCaseService | None

    @_namespace.doc(description='Downloads the test input file.')
    @_namespace.response(401, 'Error')
    @_namespace.response(403, 'Error')
    @_namespace.response(404, 'Error')
    @_namespace.response(500, 'Error')
    @_namespace.doc(security='bearer')
    @authentication_required()
    def get(self, id: int, user: UserVO) -> Response:
        try:
            user_groups = unwrap(TestDownloadInResource._group_service).get_all(user)
            path = unwrap(TestDownloadInResource._tcase_service).get_test_case_in_path(id, user.id, unwrap(TestDownloadInResource._task_service).get_task, user_groups)
            return send_file(path, download_name='test.in')
        except Forbidden as e:
            abort(403, str(e))
        except NotFound as e:
            abort(404, str(e))
        except ServerError as e:
            abort(500, str(e))

class TestDownloadOutResource(Resource): # type: ignore
    _group_service: GroupService | None
    _task_service: TaskService | None
    _tcase_service: TCaseService | None

    @_namespace.doc(description='Downloads the test output file.')
    @_namespace.response(401, 'Error')
    @_namespace.response(403, 'Error')
    @_namespace.response(404, 'Error')
    @_namespace.response(500, 'Error')
    @_namespace.doc(security='bearer')
    @authentication_required()
    def get(self, id: int, user: UserVO) -> Response:
        try:
            user_groups = unwrap(TestDownloadOutResource._group_service).get_all(user)
            path = unwrap(TestDownloadOutResource._tcase_service).get_test_case_out_path(id, user.id, unwrap(TestDownloadOutResource._task_service).get_task, user_groups)
            return send_file(path, download_name='test.out')
        except Forbidden as e:
            abort(403, str(e))
        except NotFound as e:
            abort(404, str(e))
        except ServerError as e:
            abort(500, str(e))

class TCaseEndpoints:
    def __init__(self, api: Api, tasks_namespace: Namespace, group_service: GroupService, task_service: TaskService, tcase_service: TCaseService) -> None:
        _set_up_test_parser(_new_test_parser)
        api.add_namespace(_namespace)
        self.__tasks_namespace = tasks_namespace
        TestsResource._group_service = group_service
        TestsResource._task_service = task_service
        TestsResource._tcase_service = tcase_service
        TestDownloadInResource._group_service = group_service
        TestDownloadInResource._task_service = task_service
        TestDownloadInResource._tcase_service = tcase_service
        TestDownloadOutResource._group_service = group_service
        TestDownloadOutResource._task_service = task_service
        TestDownloadOutResource._tcase_service = tcase_service

    def register_resources(self) -> None:
        self.__tasks_namespace.add_resource(TestsResource, '/<int:task_id>/tests')
        _namespace.add_resource(TestDownloadInResource, '/<int:id>/in')
        _namespace.add_resource(TestDownloadOutResource, '/<int:id>/out')
