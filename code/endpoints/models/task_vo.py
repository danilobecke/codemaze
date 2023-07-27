from __future__ import annotations
from datetime import datetime

from helpers.commons import task_download_url
from repository.dto.task import TaskDTO

class TaskVO:
    def __init__(self) -> None:
        self.id = -1
        self.name = ""
        self.max_attempts: int | None = None
        self.starts_on: datetime | None = datetime.now()
        self.ends_on: datetime | None = None
        self.file_url = ""
        self.group_id = -1

    @staticmethod
    def import_from_dto(dto: TaskDTO) -> TaskVO:
        vo = TaskVO()
        vo.id = dto.id
        vo.name = dto.name
        vo.max_attempts = dto.max_attempts
        vo.starts_on = dto.starts_on
        vo.ends_on = dto.ends_on
        vo.file_url = task_download_url(dto.id)
        vo.group_id = dto.group_id
        return vo
