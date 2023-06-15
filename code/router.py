from flask import Flask
from flask_restx import Api
from endpoints.manager_endpoints import ManagerEndpoints
from endpoints.session_endpoints import SessionEndpoints
from endpoints.student_endpoints import StudentEndpoints
from services.session_service import SessionService

class Router:
    def __init__(self, app: Flask, key: str):
        self.__api = Api(
        app=app,
        doc='/docs',
        version='1.0.0',
        title='Codemaze',
        description=''
        )
        self.__session_service = SessionService(key)

    def create_routes(self):
        ManagerEndpoints(self.__api, self.__session_service).register_resources()
        SessionEndpoints(self.__api, self.__session_service).register_resources()
        StudentEndpoints(self.__api, self.__session_service).register_resources()