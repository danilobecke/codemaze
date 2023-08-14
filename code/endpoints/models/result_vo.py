from __future__ import annotations

from endpoints.models.tcase_result_vo import TCaseResultVO
from helpers.commons import source_code_download_url
from repository.dto.result import ResultDTO

class ResultVO:
    def __init__(self) -> None:
        self.id = -1
        self.attempt_number = -1
        self.correct_open = -1
        self.correct_closed: int | None = None
        self.source_url = ''
        self.open_results: list[TCaseResultVO] = []
        self.closed_results: list[TCaseResultVO] = []

    @staticmethod
    def import_from_dto(dto: ResultDTO, attempt_numer: int, open_results: list[TCaseResultVO], closed_results: list[TCaseResultVO]) -> ResultVO:
        vo = ResultVO()
        vo.id = dto.id
        vo.attempt_number = attempt_numer
        vo.correct_open = dto.correct_open
        vo.correct_closed = dto.correct_closed if len(closed_results) > 0 else None
        vo.source_url = source_code_download_url(dto.task_id)
        vo.open_results = open_results
        vo.closed_results = closed_results
        return vo
