from __future__ import annotations
from datetime import datetime

from endpoints.models.all_tests_vo import AllTestsVO
from endpoints.models.tcase_vo import TCaseVO
from helpers.commons import task_download_url
from repository.dto.task import TaskDTO

class TaskVO:
    def __init__(self) -> None:
        self.id = -1
        self.name = ""
        self.max_attempts: int | None = None
        self.languages: list[str] = []
        self.starts_on: datetime | None = datetime.now()
        self.ends_on: datetime | None = None
        self.file_url = ""
        self.group_id = -1
        self.open_tests: list[TCaseVO] | None = None
        self.closed_tests: list[TCaseVO] | None = None

    @staticmethod
    def import_from_dto(dto: TaskDTO) -> TaskVO:
        vo = TaskVO()
        vo.id = dto.id
        vo.name = dto.name
        vo.max_attempts = dto.max_attempts
        vo.languages = dto.languages
        vo.starts_on = dto.starts_on
        vo.ends_on = dto.ends_on
        vo.file_url = task_download_url(dto.id)
        vo.group_id = dto.group_id
        return vo

    def appending_tests(self, tests: AllTestsVO) -> TaskVO:
        self.open_tests = tests.open_tests
        self.closed_tests = tests.closed_tests
        return self
