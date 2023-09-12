import glob
import os

from dotenv import load_dotenv
from flask import Flask
from flask.testing import FlaskClient

from error_handler import ErrorHandler
from helpers.config import Config
from helpers.codemaze_logger import CodemazeLogger
from helpers.runner_queue_manager import RunnerQueueManager
from repository.database import Database
from router import Router
from services.session_service import SessionService

def __get_path(*relative_path: str) -> str:
    cur_dir = os.path.realpath(os.path.curdir)
    current_path = os.path.split(cur_dir)[1]
    if current_path == 'code':
        # back to root dir (/codemaze)
        cur_dir = os.path.normpath(os.path.join(cur_dir, '..'))
    return os.path.join(cur_dir, *relative_path)

def __init_app(storage_path: str) -> Flask:
    key = __get_env('CODEMAZE_KEY')
    app = Flask(__name__)
    app.config['STORAGE_PATH'] = storage_path
    CodemazeLogger.start(app)
    Database.initialize(__get_env('CODEMAZE_DB_STRING'))
    Config.initialize(__get_path('config.toml'))
    RunnerQueueManager.initialize(__get_env('REDIS_ADDRESS'))
    SessionService.initialize(key)
    Router(os.getenv('MOSS_USER_ID')).create_routes(app)
    ErrorHandler.register(app)
    return app

def __get_env(name: str) -> str:
    var = os.getenv(name)
    if var is None or var.strip() == '':
        raise ValueError(f'Missing env var {name}')
    return var

def __set_up() -> None:
    load_dotenv()
    CodemazeLogger.set_up(__get_path(), os.getenv('PAPERTRAIL_ADDRESS'))

def run() -> Flask:
    __set_up()
    storage_path = __get_path('files', 'production')
    return __init_app(storage_path)

def run_as_debug() -> Flask:
    __set_up()
    storage_path = __get_path('files', 'debug')
    return __init_app(storage_path)

def run_as_test() -> FlaskClient:
    __set_up()
    storage_path = __get_path('files', 'test')
    for file in glob.glob(os.path.join(storage_path, '*')):
        os.remove(file)
    app = __init_app(storage_path)
    return app.test_client()

if __name__ == '__main__':
    run_as_debug()
