from __future__ import annotations

from endpoints.models.user import UserVO
from helpers.role import Role
from services.jwt_service import JWTService
from services.user_service import UserService

class SessionService:
    shared: SessionService | None = None

    def __init__(self, key: str) -> None:
        self.__jwt_service = JWTService(key)
        self.__user_service = UserService()

    def create_user(self, email: str, name: str, password: str, role: Role) -> UserVO:
        match role:
            case Role.MANAGER:
                vo = self.__user_service.create_manager(name=name, email=email, password=password)
                vo.token = self.__jwt_service.create_token(vo.id)
                return vo
            case Role.STUDENT:
                vo = self.__user_service.create_student(name=name, email=email, password=password)
                vo.token = self.__jwt_service.create_token(vo.id)
                return vo

    def login(self, email: str, password: str) -> UserVO:
        user_id = self.__user_service.login(email, password)
        vo = self.__user_service.get_user_with_role(user_id, None)
        token = self.__jwt_service.create_token(user_id)
        vo.token = token
        return vo

    def validate_token(self, token: str, role: Role | None) -> UserVO:
        user_id = self.__jwt_service.decode_token(token)
        return self.__user_service.get_user_with_role(user_id, role)

    @staticmethod
    def initialize(key: str) -> None:
        if SessionService.shared is not None:
            return
        SessionService.shared = SessionService(key)
