from datetime import datetime
import os
from typing import Optional, Callable

from endpoints.models.group import GroupVO
from endpoints.models.task_vo import TaskVO
from endpoints.models.user import UserVO
from helpers.commons import file_extension, secure_filename
from helpers.config import Config
from helpers.exceptions import Forbidden, ParameterValidationError
from helpers.file import File
from helpers.unwrapper import unwrap
from repository.dto.task import TaskDTO
from repository.task_repository import TaskRepository
from services.runner_service import RunnerService

class TaskService:
    def __init__(self, runner_service: RunnerService) -> None:
        self.__runner_service = runner_service
        self.__task_repository = TaskRepository()
        self.__max_task_size = float(Config.get('files.task-max-size-mb'))

    def __assert_is_manager(self, user: UserVO, group: GroupVO) -> None:
        if group.manager_id != user.id:
            raise Forbidden()

    def __assert_is_group_active(self, group: GroupVO) -> None:
        if group.active is False:
            raise Forbidden()

    def __assert_languages(self, languages: list[str]) -> None:
        allowed_languages = self.__runner_service.allowed_languages()
        if len(languages) == 0 or any(language not in allowed_languages for language in languages):
            raise ParameterValidationError('languages', str(languages), str(allowed_languages))

    def __assert_date(self, key: str, date: datetime, reference: datetime) -> None:
        if date < reference:
            raise ParameterValidationError(key, str(date), 'datetime')

    def __assert_started_task(self, user_id: int, task: TaskDTO, group: GroupVO) -> None:
        if unwrap(task.starts_on) > datetime.now().astimezone() and group.manager_id != user_id:
            raise Forbidden() # only managers can retrieve upcoming tasks

    def create_task(self, user: UserVO, group: GroupVO, name: str, max_attempts: Optional[int], languages: list[str], starts_on: Optional[datetime], ends_on: Optional[datetime], file: File) -> TaskVO:
        self.__assert_is_manager(user, group)
        self.__assert_is_group_active(group)
        self.__assert_languages(languages)
        if ends_on is not None:
            self.__assert_date('ends_on', ends_on, starts_on if starts_on else datetime.now().astimezone())
        full_path = file.save(max_file_size_mb=self.__max_task_size)
        dto = TaskDTO()
        dto.name = name
        dto.max_attempts = max_attempts
        dto.languages = languages
        dto.starts_on = starts_on
        dto.ends_on = ends_on
        dto.group_id = group.id
        dto.file_path = full_path
        stored = self.__task_repository.add(dto)
        return TaskVO.import_from_dto(stored)

    def get_task_name_path(self, task_id: int, user_groups: list[GroupVO], user_id: int) -> tuple[str, str]:
        task_dto: TaskDTO = self.__task_repository.find(task_id)
        try:
            group = next(_group for _group in user_groups if _group.id == task_dto.group_id)
            self.__assert_started_task(user_id, task_dto, group)
            path = task_dto.file_path
            return (secure_filename(task_dto.name) + file_extension(path), path)
        except StopIteration:
            # next exception
            # pylint: disable=raise-missing-from
            raise Forbidden()

    def update_task(self, user: UserVO, get_group_func: Callable[[int], GroupVO], task_id: int, name: Optional[str], max_attempts: Optional[int], languages: list[str], starts_on: Optional[datetime], ends_on: Optional[datetime], file: Optional[File]) -> TaskVO:
        dto: TaskDTO = self.__task_repository.find(task_id)
        group = get_group_func(dto.group_id)
        self.__assert_is_manager(user, group)
        self.__assert_is_group_active(group)
        if file is not None:
            new_file = file.save(max_file_size_mb=self.__max_task_size)
            os.remove(dto.file_path)
            dto.file_path = new_file
        if name is not None and name != dto.name:
            dto.name = name
        if max_attempts is not None and max_attempts != dto.max_attempts:
            dto.max_attempts = max_attempts
        if languages is not None and languages != dto.languages:
            self.__assert_languages(languages)
            dto.languages = languages
        if starts_on is not None and starts_on != dto.starts_on:
            dto.starts_on = starts_on
        if ends_on is not None and ends_on != dto.ends_on:
            self.__assert_date('ends_on', ends_on, unwrap(dto.starts_on))
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

    def get_task(self, task_id: int, user_id: int, user_groups: list[GroupVO], active_required: bool = False) -> TaskVO:
        dto = self.__task_repository.find(task_id)
        try:
            group = next(_group for _group in user_groups if _group.id == dto.group_id)
            if active_required and group.active is False:
                raise Forbidden()
            self.__assert_started_task(user_id, dto, group)
            return TaskVO.import_from_dto(dto)
        except StopIteration:
            # next exception
            # pylint: disable=raise-missing-from
            raise Forbidden()
