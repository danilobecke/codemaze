from datetime import datetime
import os
from typing import Optional, Callable
import uuid

from endpoints.models.group import GroupVO
from endpoints.models.task_vo import TaskVO
from endpoints.models.user import UserVO
from helpers import commons
from helpers.exceptions import Forbidden, InvalidFileExtension, InvalidFileSize
from repository.dto.task import TaskDTO
from repository.task_repository import TaskRepository

# pylint: disable=too-many-arguments
class TaskService:
    def __init__(self):
        self.__task_repository = TaskRepository()

    def __assert_is_manager(self, user: UserVO, group: GroupVO):
        if group.manager_id != user.id:
            raise Forbidden()

    def __save_file(self, filename: str, blob: bytes) -> str:
        file_extension = commons.file_extension(filename)
        if filename.strip() == '' or file_extension not in commons.ALLOWED_TEXT_EXTENSIONS:
            raise InvalidFileExtension()
        if len(blob) <= 0 or (len(blob) / (1024 * 1024)) > 1:
            raise InvalidFileSize('1 MB')
        secure_filename = str(uuid.uuid4()) + file_extension
        full_path = os.path.join(commons.storage_path(), secure_filename)
        with open(full_path, 'wb') as file:
            file.write(blob)
        return full_path

    def create_task(self, user: UserVO, group: GroupVO, name: str, max_attempts: Optional[int], starts_on: Optional[datetime], ends_on: Optional[datetime], filename: str, blob: bytes) -> TaskVO:
        self.__assert_is_manager(user, group)
        full_path = self.__save_file(filename, blob)
        dto = TaskDTO()
        dto.name = name
        dto.max_attempts = max_attempts
        dto.starts_on = starts_on
        dto.ends_on = ends_on
        dto.group_id = group.id
        dto.file_path = full_path
        stored = self.__task_repository.add(dto)
        return TaskVO.import_from_dto(stored)

    def get_task_name_path(self, task_id: int, user_groups: list[GroupVO]) -> tuple[str, str]:
        task_dto: TaskDTO = self.__task_repository.find(task_id)
        if task_dto.group_id not in list(map(lambda group: group.id, user_groups)):
            raise Forbidden()
        path = task_dto.file_path
        return (task_dto.name + commons.file_extension(path), path)

    def update_task(self, user: UserVO, get_group_func: Callable[[int], GroupVO], task_id: int, name: Optional[str], max_attempts: Optional[int], starts_on: Optional[datetime], ends_on: Optional[datetime], filename: Optional[str], blob: Optional[bytes]) -> TaskVO:
        dto: TaskDTO = self.__task_repository.find(task_id)
        self.__assert_is_manager(user, get_group_func(dto.group_id))
        if filename is not None and blob is not None:
            new_file = self.__save_file(filename, blob)
            os.remove(dto.file_path)
            dto.file_path = new_file
        if name is not None and name != dto.name:
            dto.name = name
        if max_attempts is not None and max_attempts != dto.max_attempts:
            dto.max_attempts = max_attempts
        if starts_on is not None:
            dto.starts_on = starts_on
        if ends_on is not None and ends_on != dto.ends_on:
            dto.ends_on = ends_on
        self.__task_repository.update_session()
        return TaskVO.import_from_dto(dto)
