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
    def set_up(root_path: str, papertrail_address: str | None) -> None:
        logs_path = os.path.join(root_path, 'logs')
        if not os.path.exists(logs_path):
            os.mkdir(logs_path)
        handlers = {
            'console': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
                'formatter': 'default',
            },
            'time-rotate': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': os.path.join(logs_path, 'codemaze.log'),
                'when': 'D',
                'interval': 1,
                'backupCount': 10,
                'formatter': 'default',
            }
        }
        handlers_array = ['console', 'time-rotate']
        if papertrail_address is not None:
            host, port = papertrail_address.split(':', 1)
            handlers['SysLog'] = {
                'class': 'logging.handlers.SysLogHandler',
                'address': (host, int(port)),
                'formatter': 'default',
            }
            handlers_array.append('SysLog')
        config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'default': {
                    'format': '[%(asctime)s] %(levelname)s | %(module)s >>> %(message)s',
                }
            },
            'handlers': handlers,
            'root': {'level': 'DEBUG', 'handlers': handlers_array},
        }
        dictConfig(config)

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
