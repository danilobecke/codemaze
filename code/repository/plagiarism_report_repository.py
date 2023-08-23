from sqlalchemy import select

from repository.abstract_repository import AbstractRepository
from repository.dto.plagiarism_report_dto import PlagiarismReportDTO

class PlagiarismReportRepository(AbstractRepository[PlagiarismReportDTO]):
    def __init__(self) -> None:
        super().__init__(PlagiarismReportDTO)

    def get_reports_for_task(self, task_id: int) -> list[PlagiarismReportDTO]:
        stm = select(PlagiarismReportDTO).where(PlagiarismReportDTO.task_id == task_id).order_by(PlagiarismReportDTO.created_at)
        return list(self._session.scalars(stm).all())
