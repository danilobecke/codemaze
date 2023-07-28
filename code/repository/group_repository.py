from sqlalchemy import insert, select, update, delete
from sqlalchemy.exc import IntegrityError

from helpers.exceptions import NotFound, Internal_UniqueViolation, ServerError
from helpers.role import Role
from repository.abstract_repository import AbstractRepository
from repository.dto.group_dto import GroupDTO
from repository.dto.student import StudentDTO
from repository.dto.student_group import student_group

# pylint: disable=singleton-comparison
class GroupRepository(AbstractRepository):
    def __init__(self) -> None:
        super().__init__(GroupDTO)

    def add_join_request(self, code: str, student_id: int) -> None:
        group = self._session.query(GroupDTO).filter_by(code=code, active=True).first()
        if not group:
            raise NotFound()
        try:
            stm = insert(student_group).values(student_id=student_id, group_id=group.id, approved=False)
            self._session.execute(stm)
            self._session.commit()
        except IntegrityError as e:
            self._session.rollback()
            raise Internal_UniqueViolation() from e
        except Exception as e:
            self._session.rollback()
            raise ServerError() from e

    def get_students_with_join_request(self, group_id: int, approved: bool = False) -> list[StudentDTO]:
        stm = select(student_group.columns).where(student_group.columns["group_id"] == group_id).where(student_group.columns["approved"] == approved)
        join_requests = self._session.execute(stm)
        students = list(map(lambda row: row.student_id, join_requests.all()))
        result: list[StudentDTO] = self._session.query(StudentDTO).filter(StudentDTO.id.in_(students)).all()
        return result

    def __find_opened_join_request(self, group_id: int, student_id: int) -> None:
        stm = select(student_group.columns).where(student_group.columns["group_id"] == group_id).where(student_group.columns["student_id"] == student_id).where(student_group.columns["approved"] == False)
        result = self._session.execute(stm)
        if len(result.all()) == 0:
            raise NotFound()

    def approve_join_request(self, group_id: int, student_id: int) -> None:
        self.__find_opened_join_request(group_id, student_id)
        try:
            stm = update(student_group).where(student_group.columns["group_id"] == group_id).where(student_group.columns["student_id"] == student_id).where(student_group.columns["approved"] == False).values(approved=True)
            self._session.execute(stm)
            self._session.commit()
        except Exception as e:
            self._session.rollback()
            raise ServerError() from e

    def remove_join_request(self, group_id: int, student_id: int) -> None:
        self.__find_opened_join_request(group_id, student_id)
        try:
            stm = delete(student_group).where(student_group.columns["group_id"] == group_id).where(student_group.columns["student_id"] == student_id).where(student_group.columns["approved"] == False)
            self._session.execute(stm)
            self._session.commit()
        except Exception as e:
            self._session.rollback()
            raise ServerError() from e

    def get_groups_for_user(self, id: int, role: Role) -> list[GroupDTO]:
        result: list[GroupDTO] = []
        match role:
            case Role.MANAGER:
                result = self._session.query(GroupDTO).filter_by(manager_id=id).all()
            case Role.STUDENT:
                stm = select(student_group.columns).where(student_group.columns["student_id"] == id).where(student_group.columns["approved"] == True)
                join_requests = self._session.execute(stm)
                groups = list(map(lambda row: row.group_id, join_requests.all()))
                result = self._session.query(GroupDTO).filter(GroupDTO.id.in_(groups)).all()
        return result
