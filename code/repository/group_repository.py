from repository.abstract_repository import AbstractRepository
from repository.dto.group import GroupDTO
from repository.dto.student_group import student_group
from repository.dto.student import StudentDTO
from helpers.exceptions import *
from sqlalchemy import insert, select, column
from sqlalchemy.exc import IntegrityError

class GroupRepository(AbstractRepository):
    def __init__(self):
        super().__init__(GroupDTO)

    def add_join_request(self, code: str, student_id: int):
        group = self._session.query(GroupDTO).filter_by(code=code, active=True).first()
        if not group:
            raise NotFound()
        try:
            stm = insert(student_group).values(student_id=student_id, group_id=group.id, approved=False)
            self._session.execute(stm)
            self._session.commit()
        except IntegrityError:
            self._session.rollback()
            raise Internal_UniqueViolation()
        except Exception as e:
            self._session.rollback()
            raise ServerError()
    
    def get_students_with_join_request(self, group_id: int) -> list[StudentDTO]:
        stm = select(column("student_id")).where(student_group.columns["group_id"] == group_id).where(student_group.columns["approved"] == False)
        result = self._session.execute(stm)
        students = list(map(lambda row: row.student_id, result.all()))
        return self._session.query(StudentDTO).filter(StudentDTO.id.in_(students)).all()