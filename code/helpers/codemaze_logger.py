from logging import Logger
from logging.config import dictConfig
import os

from flask import Flask, Response, request

from helpers.unwrapper import unwrap

class CodemazeLogger:
    __shared: Logger | None = None

    @staticmethod
    def shared() -> Logger:
        return unwrap(CodemazeLogger.__shared)

    @staticmethod
    def set_up() -> None:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        dictConfig({
            'version': 1,
            'formatters': {
                'default': {
                    'format': '[%(asctime)s] %(levelname)s | %(module)s >>> %(message)s',
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'stream': 'ext://sys.stdout',
                    'formatter': 'default',
                },
                'time-rotate': {
                    'class': 'logging.handlers.TimedRotatingFileHandler',
                    'filename': 'logs/codemaze.log',
                    'when': 'D',
                    'interval': 1,
                    'backupCount': 10,
                    'formatter': 'default',
                },
            },
            'root': {'level': 'DEBUG', 'handlers': ['console', 'time-rotate']},
        })

    @staticmethod
    def start(app: Flask) -> None:
        CodemazeLogger.__shared = app.logger
        app.after_request_funcs.setdefault(None, []).append(CodemazeLogger.log_after_request)

    @staticmethod
    def log_after_request(response: Response) -> Response:
        message = f'{request.method} {request.path} | status: {response.status_code}'
        try:
            json = request.get_json(silent=True)
            if json is not None:
                if json.get('password') is not None:
                    json['password'] = '****'
                message += f' | body: {json}'
            form = request.form
            if bool(form):
                if form.get('password') is not None:
                    form['password'] = '****'
                message += f' | body: {form}'
        # pylint: disable=broad-exception-caught
        except Exception:
            pass
        if response.status_code > 499:
            CodemazeLogger.shared().error(message)
        else:
            CodemazeLogger.shared().info(message)
        return response
