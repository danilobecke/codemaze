from __future__ import annotations

from helpers.commons import test_download_url_in, test_download_url_out
from repository.dto.test_case import TestCaseDTO

class TCaseVO:
    def __init__(self) -> None:
        self.id = -1
        self.input_url: str | None = None
        self.output_url: str | None = None
        self.closed = False

    @staticmethod
    def import_from_dto(dto: TestCaseDTO) -> TCaseVO:
        vo = TCaseVO()
        vo.id = dto.id
        vo.closed = dto.closed
        if vo.closed is False:
            vo.input_url = test_download_url_in(dto.id)
            vo.output_url = test_download_url_out(dto.id)
        return vo
