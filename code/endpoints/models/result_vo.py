from __future__ import annotations

from endpoints.models.tcase_result_vo import TCaseResultVO
from helpers.commons import latest_source_code_download_url
from repository.dto.result import ResultDTO

class ResultVO:
    def __init__(self) -> None:
        self.id = -1
        self.attempt_number = -1
        self.open_result_percentage: float = -1
        self.closed_result_percentage: float | None = -1
        self.result_percentage: float = -1
        self.source_url = ''
        self.open_results: list[TCaseResultVO] = []
        self.closed_results: list[TCaseResultVO] = []

    @staticmethod
    def import_from_dto(dto: ResultDTO, attempt_numer: int, open_results: list[TCaseResultVO], closed_results: list[TCaseResultVO]) -> ResultVO:
        len_open_tests = len(open_results)
        len_closed_tests = len(closed_results)
        vo = ResultVO()
        vo.id = dto.id
        vo.attempt_number = attempt_numer
        vo.open_result_percentage = round((dto.correct_open / len_open_tests) * 100, 2)
        vo.closed_result_percentage = round((dto.correct_closed / len_closed_tests) * 100, 2) if len_closed_tests > 0 else None
        vo.result_percentage = vo.open_result_percentage if vo.closed_result_percentage is None else round((vo.open_result_percentage * len_open_tests + vo.closed_result_percentage * len_closed_tests) / (len_open_tests + len_closed_tests), 2)
        vo.source_url = latest_source_code_download_url(dto.task_id)
        vo.open_results = open_results
        vo.closed_results = closed_results
        return vo
