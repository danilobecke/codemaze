from flask import Flask

class Router:
    def __init__(self, app: Flask):
        self.__app = app
    
    def create_routes(self):
        # __app.add_url_rule
        return