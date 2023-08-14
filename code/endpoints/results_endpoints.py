from flask import abort, send_file
from flask.wrappers import Response
from flask_restx import Api, Namespace, Resource, fields
from flask_restx.reqparse import RequestParser
from werkzeug.datastructures import FileStorage

from endpoints.models.result_vo import ResultVO
from endpoints.models.user import UserVO
from helpers.authenticator_decorator import authentication_required
from helpers.exceptions import Forbidden, NotFound, InvalidFileExtension, InvalidFileSize, ServerError, InvalidSourceCode
from helpers.file import File
from helpers.role import Role
from helpers.unwrapper import unwrap
from services.group_service import GroupService
from services.result_service import ResultService
from services.task_service import TaskService
from services.tcase_service import TCaseService

_namespace = Namespace('results', description='')

_submit_result_parser = _namespace.parser()

def _set_up_parser(parser: RequestParser) -> None:
    parser.add_argument('code', type=FileStorage, required=True, location='files')

_test_result_model = _namespace.model('Test Case Result', {
    'success': fields.Boolean(required=True),
    'diff': fields.String()
})

_result_model = _namespace.model('Result', {
    'id': fields.Integer(required=True),
    'attempt_number': fields.Integer(required=True),
    'correct_open': fields.Integer(required=True),
    'correct_closed': fields.Integer(),
    'source_url': fields.String(required=True),
    'open_results': fields.Nested(_test_result_model, as_list=True, skip_none=True, required=True),
    'closed_results': fields.Nested(_test_result_model, as_list=True, skip_none=True, required=True)
})

class ResultsResource(Resource): # type: ignore
    _group_service: GroupService | None
    _task_service: TaskService | None
    _tcase_service: TCaseService | None
    _result_service: ResultService | None

    @_namespace.doc(description='*Students only*\nSubmit a code to be evaluated.')
    @_namespace.expect(_submit_result_parser, validate=True)
    @_namespace.param('code', _in='formData', type='file', required=True)
    @_namespace.response(400, 'Error')
    @_namespace.response(401, 'Error')
    @_namespace.response(403, 'Error')
    @_namespace.response(404, 'Error')
    @_namespace.response(500, 'Error')
    @_namespace.marshal_with(_result_model, code=201)
    @_namespace.doc(security='bearer')
    @authentication_required(Role.STUDENT)
    def post(self, task_id: int, user: UserVO) -> tuple[ResultVO, int]:
        args = _submit_result_parser.parse_args()
        file_storage: FileStorage = args['code']
        filename = unwrap(file_storage.filename)
        blob = file_storage.stream.read()
        try:
            user_groups = unwrap(ResultsResource._group_service).get_all(user)
            task = unwrap(ResultsResource._task_service).get_task(task_id, user.id, user_groups)
            tests = unwrap(ResultsResource._tcase_service).get_tests(user.id, task, user_groups, running_context=True)
            return unwrap(ResultsResource._result_service).run(user, task, tests, File(filename, blob)), 201
        except Forbidden as e:
            abort(403, str(e))
        except NotFound as e:
            abort(404, str(e))
        except (InvalidFileSize, InvalidSourceCode) as e:
            abort(413, str(e))
        except InvalidFileExtension as e:
            abort(422, str(e))
        except ServerError as e:
            abort(500, str(e))

class SourceCodeDownloadResource(Resource): # type: ignore
    _group_service: GroupService | None
    _task_service: TaskService | None
    _result_service: ResultService | None

    @_namespace.doc(description='*Students only*\nDownloads the latest submitted source code for the given task.')
    @_namespace.response(401, 'Error')
    @_namespace.response(403, 'Error')
    @_namespace.response(404, 'Error')
    @_namespace.response(500, 'Error')
    @_namespace.doc(security='bearer')
    @authentication_required(role=Role.STUDENT)
    def get(self, task_id: int, user: UserVO) -> Response:
        try:
            user_groups = unwrap(SourceCodeDownloadResource._group_service).get_all(user)
            task = unwrap(SourceCodeDownloadResource._task_service).get_task(task_id, user.id, user_groups)
            name, path = unwrap(SourceCodeDownloadResource._result_service).get_latest_source_code_name_path(task, user.id)
            return send_file(path, download_name=name)
        except Forbidden as e:
            abort(403, str(e))
        except NotFound as e:
            abort(404, str(e))
        except ServerError as e:
            abort(500, str(e))

class LatestResultResource(Resource): # type: ignore
    _group_service: GroupService | None
    _task_service: TaskService | None
    _tcase_service: TCaseService | None
    _result_service: ResultService | None

    @_namespace.doc(description='*Students only*\nGet the latest submitted result for the given task.')
    @_namespace.response(401, 'Error')
    @_namespace.response(403, 'Error')
    @_namespace.response(404, 'Error')
    @_namespace.response(500, 'Error')
    @_namespace.marshal_with(_result_model)
    @_namespace.doc(security='bearer')
    @authentication_required(role=Role.STUDENT)
    def get(self, task_id: int, user: UserVO) -> ResultVO:
        try:
            user_groups = unwrap(LatestResultResource._group_service).get_all(user)
            task = unwrap(LatestResultResource._task_service).get_task(task_id, user.id, user_groups)
            tests = unwrap(LatestResultResource._tcase_service).get_tests(user.id, task, user_groups, running_context=True)
            return unwrap(LatestResultResource._result_service).get_latest_result(task, user, tests)
        except Forbidden as e:
            abort(403, str(e))
        except NotFound as e:
            abort(404, str(e))
        except ServerError as e:
            abort(500, str(e))

class ResultsEndpoints():
    def __init__(self, api: Api, tasks_namespace: Namespace, group_service: GroupService, task_service: TaskService, tcase_service: TCaseService, result_service: ResultService) -> None:
        api.add_namespace(_namespace)
        _set_up_parser(_submit_result_parser)
        self.__tasks_namespace = tasks_namespace
        ResultsResource._group_service = group_service
        ResultsResource._task_service = task_service
        ResultsResource._tcase_service = tcase_service
        ResultsResource._result_service = result_service
        SourceCodeDownloadResource._group_service = group_service
        SourceCodeDownloadResource._task_service = task_service
        SourceCodeDownloadResource._result_service = result_service
        LatestResultResource._group_service = group_service
        LatestResultResource._task_service = task_service
        LatestResultResource._tcase_service = tcase_service
        LatestResultResource._result_service = result_service

    def register_resources(self) -> None:
        self.__tasks_namespace.add_resource(ResultsResource, '/<int:task_id>/results')
        self.__tasks_namespace.add_resource(LatestResultResource, '/<int:task_id>/results/latest')
        self.__tasks_namespace.add_resource(SourceCodeDownloadResource, '/<int:task_id>/results/latest/code')
