from __future__ import annotations

from helpers.commons import test_download_url_in, test_download_url_out
from repository.dto.test_case import TestCaseDTO

class TCaseVO:
    def __init__(self):
        self.id = -1
        self.input_url = ""
        self.output_url = ""
        self.closed = False

    @staticmethod
    def import_from_dto(dto: TestCaseDTO) -> TCaseVO:
        vo = TCaseVO()
        vo.id = dto.id
        vo.input_url = test_download_url_in(dto.id)
        vo.output_url = test_download_url_out(dto.id)
        vo.closed = dto.closed
        return vo
