from datetime import datetime
import os
from typing import Optional
import uuid

from endpoints.models.group import GroupVO
from endpoints.models.task_vo import TaskVO
from endpoints.models.user import UserVO
from helpers import commons
from helpers.exceptions import Forbidden, InvalidFileExtension, InvalidFileSize
from repository.dto.task import TaskDTO
from repository.task_repository import TaskRepository

class TaskService:
    def __init__(self):
        self.__task_repository = TaskRepository()

    def create_task(self, user: UserVO, group: GroupVO, name: str, max_attempts: Optional[int], starts_on: Optional[datetime], ends_on: Optional[datetime], filename: str, blob: bytes):
        if group.manager_id != user.id:
            raise Forbidden()
        file_extension = commons.file_extension(filename)
        if filename.strip() == '' or file_extension not in commons.ALLOWED_TEXT_EXTENSIONS:
            raise InvalidFileExtension()
        if len(blob) <= 0 or (len(blob) / (1024 * 1024)) > 1:
            raise InvalidFileSize('1 MB')
        secure_filename = str(uuid.uuid4()) + file_extension
        full_path = os.path.join(commons.STORAGE_PATH, secure_filename)
        with open(full_path, 'wb') as file:
            file.write(blob)
        dto = TaskDTO()
        dto.name = name
        dto.max_attempts = max_attempts
        dto.starts_on = starts_on
        dto.ends_on = ends_on
        dto.group_id = group.id
        dto.file_path = full_path
        stored = self.__task_repository.add(dto)
        return TaskVO.import_from_dto(stored)
