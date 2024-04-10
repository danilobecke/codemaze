import os

from flask import url_for, current_app
from werkzeug.utils import secure_filename as w_secure_filename

from helpers.exceptions import InvalidCodec

ALLOWED_TEXT_EXTENSIONS = { '.txt', '.pdf', '.doc', '.docx', '.md', '.in', '.out' }
CODEC_LIST = { 'utf-8', 'ascii', 'cp037', 'cp437', 'cp500', 'cp850', 'cp852', 'cp858', 'cp860', 'cp863', 'cp1140', 'cp1250', 'cp1252', 'latin-1', 'iso8859-2', 'iso8859-15', 'iso8859-16', 'mac-latin2', 'mac-roman', 'utf-16', 'utf-32' }

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

def lossless_decode(bytes_str: bytes) -> str:
    for codec in CODEC_LIST:
        try:
            return bytes_str.decode(codec)
        except UnicodeDecodeError:
            continue
    raise InvalidCodec('code')
