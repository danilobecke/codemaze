from sqlalchemy import insert, select, update, delete, and_
from sqlalchemy.exc import IntegrityError

from helpers.exceptions import NotFound, Internal_UniqueViolation, ServerError
from helpers.role import Role
from repository.abstract_repository import AbstractRepository
from repository.dto.group_dto import GroupDTO
from repository.dto.student import StudentDTO
from repository.dto.student_group import student_group

# pylint: disable=singleton-comparison
class GroupRepository(AbstractRepository[GroupDTO]):
    def __init__(self) -> None:
        super().__init__(GroupDTO)

    def get_group_by_code(self, code: str) -> GroupDTO:
        group = self._session.scalars(select(GroupDTO).where(GroupDTO.code == code)).first()
        if not group:
            raise NotFound()
        return group

    def add_join_request(self, group_id: int, student_id: int) -> None:
        try:
            stm = insert(student_group).values(student_id=student_id, group_id=group_id, approved=False)
            self._session.execute(stm)
            self._session.commit()
        except IntegrityError as e:
            self._session.rollback()
            raise Internal_UniqueViolation() from e
        except Exception as e:
            self._session.rollback()
            raise ServerError() from e

    def get_students_with_join_request(self, group_id: int, approved: bool = False) -> list[StudentDTO]:
        stm = select(StudentDTO)\
            .join(student_group, StudentDTO.id == student_group.columns['student_id'])\
            .where(and_(student_group.columns['group_id'] == group_id, student_group.columns['approved'] == approved))
        if approved:
            stm = stm.order_by(StudentDTO.name)
        else:
            stm = stm.order_by(student_group.columns['created_at'])
        return list(self._session.scalars(stm).all())

    def __find_opened_join_request(self, group_id: int, student_id: int) -> None:
        stm = select(student_group)\
            .where(student_group.columns['group_id'] == group_id)\
            .where(student_group.columns['student_id'] == student_id)\
            .where(student_group.columns['approved'] == False)
        result = self._session.execute(stm)
        if len(result.all()) == 0:
            raise NotFound()

    def approve_join_request(self, group_id: int, student_id: int) -> None:
        self.__find_opened_join_request(group_id, student_id)
        try:
            stm = update(student_group)\
                .where(student_group.columns['group_id'] == group_id)\
                .where(student_group.columns['student_id'] == student_id)\
                .where(student_group.columns['approved'] == False)\
                .values(approved=True)
            self._session.execute(stm)
            self._session.commit()
        except Exception as e:
            self._session.rollback()
            raise ServerError() from e

    def remove_join_request(self, group_id: int, student_id: int) -> None:
        self.__find_opened_join_request(group_id, student_id)
        try:
            stm = delete(student_group)\
                .where(student_group.columns['group_id'] == group_id)\
                .where(student_group.columns['student_id'] == student_id)\
                .where(student_group.columns['approved'] == False)
            self._session.execute(stm)
            self._session.commit()
        except Exception as e:
            self._session.rollback()
            raise ServerError() from e

    def get_groups_for_user(self, id: int, role: Role) -> list[GroupDTO]:
        result: list[GroupDTO] = []
        match role:
            case Role.MANAGER:
                result = list(self._session.scalars(select(GroupDTO).where(GroupDTO.manager_id == id).order_by(GroupDTO.created_at)).all())
            case Role.STUDENT:
                stm = select(GroupDTO)\
                    .join(student_group, GroupDTO.id == student_group.columns['group_id'])\
                    .join(StudentDTO, StudentDTO.id == student_group.columns['student_id'])\
                    .where(and_(StudentDTO.id == id, student_group.columns['approved'] == True))\
                    .order_by(student_group.columns['updated_at'])
                result = list(self._session.scalars(stm).all())
        return result
