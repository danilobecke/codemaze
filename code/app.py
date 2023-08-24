import glob
import os

from dotenv import load_dotenv
from flask import Flask
from flask.testing import FlaskClient

from error_handler import ErrorHandler
from helpers.config import Config
from helpers.codemaze_logger import CodemazeLogger
from repository.database import Database
from router import Router
from services.session_service import SessionService

def __init_app(db_string: str, storage_path: str, resetting_db: bool = False) -> Flask:
    key = __get_env('CODEMAZE_KEY')
    app = Flask(__name__)
    app.config['STORAGE_PATH'] = storage_path
    CodemazeLogger.start(app)
    Database.initialize(db_string, resetting_db)
    Config.initialize(os.path.join(os.path.realpath(os.path.curdir), 'code', 'config.toml'))
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
    CodemazeLogger.set_up()
    load_dotenv()

def run_as_debug() -> None:
    __set_up()
    db_string = __get_env('DEBUG_DB_STRING')
    storage_path = os.path.join(os.path.realpath(os.path.curdir), 'files', 'debug')
    app = __init_app(db_string, storage_path)
    app.run(port=48345, debug=True)

def run_as_test() -> FlaskClient:
    __set_up()
    db_string = __get_env('TEST_DB_STRING')
    storage_path = os.path.join(os.path.realpath(os.path.curdir), 'files', 'test')
    for file in glob.glob(os.path.join(storage_path, '*')):
        os.remove(file)
    app = __init_app(db_string, storage_path, resetting_db=True)
    return app.test_client()

if __name__ == '__main__':
    run_as_debug()
