from __future__ import annotations

from repository.dto.test_case_result import TestCaseResultDTO

class TCaseResultVO:
    def __init__(self) -> None:
        self.id: int = -1
        self.success: bool = False
        self.diff: str | None = None
        self.test_case_id: int = -1

    @staticmethod
    def import_from_dto(dto: TestCaseResultDTO) -> TCaseResultVO:
        vo = TCaseResultVO()
        vo.id = dto.id
        vo.success = dto.success
        vo.diff = dto.diff
        vo.test_case_id = dto.test_case_id
        return vo
