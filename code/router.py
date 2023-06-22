from flask import Flask
from flask_restx import Api

from endpoints.group_endpoints import GroupEndpoints
from endpoints.manager_endpoints import ManagerEndpoints
from endpoints.session_endpoints import SessionEndpoints
from endpoints.student_endpoints import StudentEndpoints
from services.group_service import GroupService

class Router:
    def __init__(self, app: Flask):
        self.__api = Api(
        app=app,
        doc='/docs',
        version='1.0.0',
        title='Codemaze',
        description=''
        )
        self.__group_service = GroupService()

    def create_routes(self):
        ManagerEndpoints(self.__api).register_resources()
        SessionEndpoints(self.__api).register_resources()
        StudentEndpoints(self.__api).register_resources()
        GroupEndpoints(self.__api, self.__group_service).register_resources()