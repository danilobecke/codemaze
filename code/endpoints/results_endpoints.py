from flask import abort
from flask_restx import Api, Namespace, Resource
from flask_restx.reqparse import RequestParser
from werkzeug.datastructures import FileStorage

from endpoints.models.user import UserVO
from helpers.authenticator_decorator import authentication_required
from helpers.exceptions import Forbidden, NotFound, InvalidFileExtension, InvalidFileSize, ServerError
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
    @_namespace.doc(security='bearer')
    @authentication_required(Role.STUDENT)
    def post(self, task_id: int, user: UserVO):
        args = _submit_result_parser.parse_args()
        file_storage: FileStorage = args['code']
        filename = unwrap(file_storage.filename)
        blob = file_storage.stream.read()
        try:
            user_groups = unwrap(ResultsResource._group_service).get_all(user)
            task = unwrap(ResultsResource._task_service).get_task(task_id, user.id, user_groups)
            tests = unwrap(ResultsResource._tcase_service).get_tests(user.id, task, user_groups, running_context=True)
            unwrap(ResultsResource._result_service).run(user, task, tests, File(filename, blob))
            return [], 201
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

class ResultsEndpoints():
    def __init__(self, api: Api, tasks_namespace: Namespace, group_service: GroupService, task_service: TaskService, tcase_service: TCaseService, result_service: ResultService) -> None:
        api.add_namespace(_namespace)
        _set_up_parser(_submit_result_parser)
        self.__tasks_namespace = tasks_namespace
        ResultsResource._group_service = group_service
        ResultsResource._task_service = task_service
        ResultsResource._tcase_service = tcase_service
        ResultsResource._result_service = result_service

    def register_resources(self) -> None:
        self.__tasks_namespace.add_resource(ResultsResource, '/<int:task_id>/results')
