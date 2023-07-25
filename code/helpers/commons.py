import os

from flask import url_for, current_app

ALLOWED_TEXT_EXTENSIONS = { '.txt', '.pdf', '.doc', '.docx', '.md', '.in', '.out' }

def storage_path() -> str:
    return current_app.config['STORAGE_PATH']

def file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1]

def file_name(path: str) -> str:
    return os.path.split(path)[1]

def task_download_url(task_id: int) -> str:
    return url_for('tasks_task_download_resource', id=task_id)

def test_download_url_in(test_id: int) -> str:
    return url_for('tests_test_download_in_resource', id=test_id)

def test_download_url_out(test_id: int) -> str:
    return url_for('tests_test_download_out_resource', id=test_id)
