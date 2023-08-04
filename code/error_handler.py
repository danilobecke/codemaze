from flask import Flask, json
from flask.typing import ResponseReturnValue
from werkzeug.exceptions import HTTPException

class ErrorHandler:
    @staticmethod
    def __handle_http_exception(e: HTTPException) -> ResponseReturnValue:
        # https://flask.palletsprojects.com/en/2.3.x/errorhandling/#generic-exception-handlers
        response = e.get_response()
        response.data = json.dumps({ # type: ignore
            "code": e.code,
            "name": e.name,
            "description": e.description,
        })
        response.content_type = "application/json"
        return response # type: ignore

    @staticmethod
    def register(app: Flask) -> None:
        app.register_error_handler(HTTPException, ErrorHandler.__handle_http_exception)
