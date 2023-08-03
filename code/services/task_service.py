from datetime import datetime
import os
from typing import Optional, Callable

from endpoints.models.group import GroupVO
from endpoints.models.task_vo import TaskVO
from endpoints.models.user import UserVO
from helpers import commons
from helpers.exceptions import Forbidden
from helpers.file import File
from helpers.unwrapper import unwrap
from repository.dto.task import TaskDTO
from repository.task_repository import TaskRepository

class TaskService:
    def __init__(self) -> None:
        self.__task_repository = TaskRepository()

    def __assert_is_manager(self, user: UserVO, group: GroupVO) -> None:
        if group.manager_id != user.id:
            raise Forbidden()

    def create_task(self, user: UserVO, group: GroupVO, name: str, max_attempts: Optional[int], starts_on: Optional[datetime], ends_on: Optional[datetime], file: File) -> TaskVO:
        self.__assert_is_manager(user, group)
        full_path = file.save()
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

    def update_task(self, user: UserVO, get_group_func: Callable[[int], GroupVO], task_id: int, name: Optional[str], max_attempts: Optional[int], starts_on: Optional[datetime], ends_on: Optional[datetime], file: Optional[File]) -> TaskVO:
        dto: TaskDTO = self.__task_repository.find(task_id)
        self.__assert_is_manager(user, get_group_func(dto.group_id))
        if file is not None:
            new_file = file.save()
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

    def get_tasks(self, user_id: int, group: GroupVO, user_groups: list[GroupVO]) -> list[TaskVO]:
        group_id = group.id
        if any(group_id == _group.id for _group in user_groups) is False:
            raise Forbidden()
        started_only = user_id != group.manager_id # only managers can retrieve upcoming tasks
        dtos = self.__task_repository.get_tasks(group_id, started_only)
        return list(map(lambda dto: TaskVO.import_from_dto(dto), dtos))

    def get_task(self, task_id: int, user_id: int, user_groups: list[GroupVO]) -> TaskVO:
        dto = self.__task_repository.find(task_id)
        try:
            group = next(filter(lambda _group: _group.id == dto.group_id, user_groups))
            if unwrap(dto.starts_on) > datetime.now().astimezone() and group.manager_id != user_id:
                raise Forbidden() # only managers can retrieve upcoming tasks
            return TaskVO.import_from_dto(dto)
        except StopIteration:
            # next exception
            # pylint: disable=raise-missing-from
            raise Forbidden()
