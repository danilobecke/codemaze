from sqlalchemy import select, and_

from helpers.exceptions import NotFound, ServerError
from helpers.role import Role
from repository.abstract_repository import AbstractRepository
from repository.dto.group_dto import GroupDTO
from repository.dto.student_group import StudentGroupDTO
from repository.dto.user_dto import UserDTO

# pylint: disable=singleton-comparison
class StudentGroupRepository(AbstractRepository[StudentGroupDTO]):
    def __init__(self) -> None:
        super().__init__(StudentGroupDTO)

    def get_students_with_join_request(self, group_id: int, approved: bool = False) -> list[UserDTO]:
        stm = select(UserDTO)\
            .join(StudentGroupDTO, UserDTO.id == StudentGroupDTO.student_id)\
            .where(and_(StudentGroupDTO.group_id == group_id, StudentGroupDTO.approved == approved))\
            .order_by(UserDTO.name)
        return list(self._session.scalars(stm).all())

    def __find_opened_join_request(self, group_id: int, student_id: int) -> StudentGroupDTO:
        stm = select(StudentGroupDTO)\
            .where(StudentGroupDTO.group_id == group_id)\
            .where(StudentGroupDTO.student_id == student_id)\
            .where(StudentGroupDTO.approved == False)
        model = self._session.scalars(stm).first()
        if not model:
            raise NotFound()
        return model

    def approve_join_request(self, group_id: int, student_id: int) -> None:
        model = self.__find_opened_join_request(group_id, student_id)
        try:
            model.approved = True
            self.update_session()
        except Exception as e:
            self._session.rollback()
            raise ServerError() from e

    def remove_join_request(self, group_id: int, student_id: int) -> None:
        model = self.__find_opened_join_request(group_id, student_id)
        try:
            self._session.delete(model)
            self.update_session()
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
                    .join(StudentGroupDTO, GroupDTO.id == StudentGroupDTO.group_id)\
                    .join(UserDTO, UserDTO.id == StudentGroupDTO.student_id)\
                    .where(and_(UserDTO.id == id, StudentGroupDTO.approved == True))\
                    .order_by(GroupDTO.name)
                result = list(self._session.scalars(stm).all())
        return result
