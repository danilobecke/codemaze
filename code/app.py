import os
import shutil

from dotenv import load_dotenv
from flask import Flask
from flask.testing import FlaskClient

from repository.database import Database
from router import Router
from services.session_service import SessionService

def __init_app(db_string: str, storage_path: str, resetting_db: bool = False) -> Flask:
    key = __get_env('CODEMAZE_KEY')
    app = Flask(__name__)
    app.config['STORAGE_PATH'] = storage_path
    Database.initialize(db_string, resetting_db)
    SessionService.initialize(key)
    Router().create_routes(app)
    return app

def __get_env(name: str) -> str:
    var = os.getenv(name)
    if var is None or var.strip() == '':
        raise ValueError(f'Missing env var {name}')
    return var

def __set_up() -> None:
    load_dotenv()

def run_as_debug() -> None:
    __set_up()
    db_string = __get_env('DEBUG_DB_STRING')
    storage_path = os.path.join(os.path.realpath(os.path.curdir), 'files')
    app = __init_app(db_string, storage_path)
    app.run(port=48345, debug=True)

def run_as_test() -> FlaskClient:
    __set_up()
    db_string = __get_env('TEST_DB_STRING')
    storage_path = os.path.join(os.path.realpath(os.path.curdir), 'files_test')
    if os.path.isdir(storage_path):
        shutil.rmtree(storage_path, ignore_errors=True)
    os.mkdir(storage_path)
    app = __init_app(db_string, storage_path, resetting_db=True)
    return app.test_client()

if __name__ == '__main__':
    run_as_debug()
