from __future__ import annotations

from helpers.commons import test_download_url_in, test_download_url_out
from repository.dto.test_case import TestCaseDTO

class TCaseVO:
    def __init__(self) -> None:
        self.id = -1
        self.input_url: str | None = None
        self.output_url: str | None = None
        self.closed = False
        self.input_path: str | None = None
        self.output_path: str | None = None

    @staticmethod
    def import_from_dto(dto: TestCaseDTO, is_manager: bool) -> TCaseVO:
        vo = TCaseVO()
        vo.id = dto.id
        vo.closed = dto.closed
        if vo.closed is False or is_manager is True:
            # The manager can download the files
            vo.input_url = test_download_url_in(dto.id)
            vo.output_url = test_download_url_out(dto.id)
        return vo

    @staticmethod
    def running_context_from_dto(dto: TestCaseDTO) -> TCaseVO:
        vo = TCaseVO()
        vo.id = dto.id
        vo.closed = dto.closed
        vo.input_path = dto.input_file_path
        vo.output_path = dto.output_file_path
        return vo
