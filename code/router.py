from flask import Flask
from flask_restx import Api
from jsonschema import FormatChecker

from endpoints.group_endpoints import GroupEndpoints
from endpoints.manager_endpoints import ManagerEndpoints
from endpoints.session_endpoints import SessionEndpoints
from endpoints.student_endpoints import StudentEndpoints
from endpoints.task_endpoints import TaskEndpoints
from endpoints.tcase_endpoints import TCaseEndpoints
from services.group_service import GroupService
from services.task_service import TaskService
from services.tcase_service import TCaseService

class Router:
    def __init__(self, app: Flask) -> None:
        self.__api = Api(
        app=app,
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
        self.__group_service = GroupService()
        self.__task_service = TaskService()
        self.__tcase_service = TCaseService()

    def create_routes(self) -> None:
        ManagerEndpoints(self.__api).register_resources()
        SessionEndpoints(self.__api).register_resources()
        StudentEndpoints(self.__api).register_resources()
        groups_namespace = GroupEndpoints(self.__api, self.__group_service).register_resources()
        tasks_namespace = TaskEndpoints(self.__api, groups_namespace, self.__group_service, self.__task_service).register_resources()
        TCaseEndpoints(self.__api, tasks_namespace, self.__group_service, self.__task_service, self.__tcase_service).register_resources()
