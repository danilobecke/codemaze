from flask import Flask
from router import Router
from repository.database import Database
import os

def __init_app(db_string: str, debug: bool):
    app = Flask(__name__)
    Router(app).create_routes()
    Database.initialize(db_string, debug)
    return app

def __get_env(name: str):
    var = os.getenv(name)
    if var is None or var.strip() == '':
        raise ValueError(f'Missing env var {name}')
    return var

def run_as_debug():
    # postgresql://root:admin@localhost/postgres
    db_string = __get_env('DEBUG_DB_STRING')
    app = __init_app(db_string, debug=True)
    app.run(debug=True)

def run_as_test():
    db_string = __get_env('TEST_DB_STRING')
    app = __init_app(db_string, debug=False)
    return app.test_client()

if __name__ == '__main__':
    run_as_debug()