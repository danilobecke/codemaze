from repository.abstract_repository import AbstractRepository
from repository.dto.group import GroupDTO
from repository.dto.student_group import student_group
from helpers.exceptions import *
from sqlalchemy import insert
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