import os

from flask import url_for

ALLOWED_TEXT_EXTENSIONS = { '.txt', '.pdf', '.doc', '.docx', '.md', '.in', '.out' }
STORAGE_PATH = os.path.join(os.path.realpath(os.path.curdir), 'files')

def file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1]

def file_name(path: str) -> str:
    return os.path.split(path)[1]

def task_download_url(group_id: int, task_id: int) -> str:
    return url_for('groups_task_download_resource', group_id=group_id, id=task_id)
