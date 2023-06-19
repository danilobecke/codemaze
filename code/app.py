from flask import Flask
from router import Router
from repository.database import Database
from services.session_service import SessionService
import os

def __init_app(db_string: str, resetting_db: bool = False):
    key = __get_env('CODEMAZE_KEY')
    app = Flask(__name__)
    Database.initialize(db_string, resetting_db)
    SessionService.initialize(key)
    Router(app).create_routes()
    return app

def __get_env(name: str):
    var = os.getenv(name)
    if var is None or var.strip() == '':
        raise ValueError(f'Missing env var {name}')
    return var

def run_as_debug():
    db_string = __get_env('DEBUG_DB_STRING')
    app = __init_app(db_string)
    app.run(port=48345, debug=True)

def run_as_test():
    db_string = __get_env('TEST_DB_STRING')
    app = __init_app(db_string, resetting_db=True)
    return app.test_client()

if __name__ == '__main__':
    run_as_debug()