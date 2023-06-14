from flask import Flask
from flask_restx import Api
from endpoints.manager_endpoints import ManagerEndpoints

class Router:
    def __init__(self, app: Flask):
        self.__api = Api(
        app=app,
        doc='/docs',
        version='1.0.0',
        title='Codemaze',
        description=''
    )

    def create_routes(self):
        ManagerEndpoints(self.__api).register_resources()