from flask import Flask, Blueprint
from flask_restx import Api
from jsonschema import FormatChecker

from endpoints.group_endpoints import GroupEndpoints
from endpoints.manager_endpoints import ManagerEndpoints
from endpoints.results_endpoints import ResultsEndpoints
from endpoints.session_endpoints import SessionEndpoints
from endpoints.student_endpoints import StudentEndpoints
from endpoints.task_endpoints import TaskEndpoints
from endpoints.tcase_endpoints import TCaseEndpoints
from services.group_service import GroupService
from services.moss_service import MossService
from services.result_service import ResultService
from services.runner_service import RunnerService
from services.task_service import TaskService
from services.tcase_service import TCaseService

class Router:
    def __init__(self, moss_user_id: str | None) -> None:
        self.__moss_service = MossService(moss_user_id) if moss_user_id else None
        self.__runner_service = RunnerService()
        self.__group_service = GroupService()
        self.__task_service = TaskService(self.__runner_service)
        self.__tcase_service = TCaseService()
        self.__result_service = ResultService(self.__runner_service, self.__moss_service)

    def __create_v1_api(self, blueprint: Blueprint) -> Api:
        return Api(
        blueprint,
        doc='/docs',
        version='1.0.0',
        title='Codemaze',
        description='',
        format_checker=FormatChecker(),
        authorizations={
            'bearer': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization',
                'description': 'Type in the *Value* input box below: **Bearer &lt;JWT&gt;**, where &lt;JWT&gt; is the token'
            }
        })

    def __register_v1_routes(self, app: Flask) -> None:
        v1_blueprint = Blueprint('api/v1', __name__, url_prefix='/api/v1')
        v1_api = self.__create_v1_api(v1_blueprint)

        ManagerEndpoints(v1_api).register_resources()
        SessionEndpoints(v1_api).register_resources()
        StudentEndpoints(v1_api).register_resources()
        groups_namespace = GroupEndpoints(v1_api, self.__group_service).register_resources()
        tasks_namespace = TaskEndpoints(v1_api, groups_namespace, self.__group_service, self.__task_service, self.__tcase_service).register_resources()
        TCaseEndpoints(v1_api, tasks_namespace, self.__group_service, self.__task_service, self.__tcase_service).register_resources()
        ResultsEndpoints(v1_api, tasks_namespace, self.__group_service, self.__task_service, self.__tcase_service, self.__result_service).register_resources()

        app.register_blueprint(v1_blueprint)

    def create_routes(self, app: Flask) -> None:
        self.__register_v1_routes(app)
