import os

from flask import url_for, current_app
from werkzeug.utils import secure_filename as w_secure_filename

ALLOWED_TEXT_EXTENSIONS = { '.txt', '.pdf', '.doc', '.docx', '.md', '.in', '.out' }

def storage_path() -> str:
    return str(current_app.config['STORAGE_PATH'])

def scripts_path() -> str:
    return str(current_app.config['SCRIPTS_PATH'])

def filename(path: str) -> str:
    return os.path.split(path)[1]

def file_extension(path: str) -> str:
    return os.path.splitext(path)[1]

def task_download_url(task_id: int) -> str:
    return url_for('api/v1.tasks_task_download_resource', id=task_id)

def test_download_url_in(test_id: int) -> str:
    return url_for('api/v1.tests_test_download_in_resource', id=test_id)

def test_download_url_out(test_id: int) -> str:
    return url_for('api/v1.tests_test_download_out_resource', id=test_id)

def latest_source_code_download_url(task_id: int) -> str:
    return url_for('api/v1.tasks_source_code_download_resource', task_id=task_id)

def source_code_download_url(result_id: int) -> str:
    return url_for('api/v1.results_result_code_resource', id=result_id)

def create_test_script_download_url() -> str:
    return url_for('api/v1.configs_download_create_test_script_resource')

def secure_filename(fname: str) -> str:
    return w_secure_filename(fname)

def compute_percentage(open_tests_percentage: float, closed_tests_percentage: float | None, len_open_tests: int, len_closed_tests: int) -> float:
    return open_tests_percentage if closed_tests_percentage is None else round((open_tests_percentage * len_open_tests + closed_tests_percentage * len_closed_tests) / (len_open_tests + len_closed_tests), 2)
