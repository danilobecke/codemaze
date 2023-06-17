from typing import Self
from services.jwt_service import JWTService
from services.user_service import UserService
from endpoints.models.user import UserVO
from helpers.exceptions import *
from helpers.role import Role

class SessionService:
    shared: Self | None = None

    def __init__(self, key: str):
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

    def __get_user(self, id: int) -> UserVO:
        vo: UserVO = None
        try:
            vo = self.__user_service.get_manager(id)
        except NotFound:
            vo = self.__user_service.get_student(id)
        return vo

    def login(self, email: str, password: str) -> UserVO:
        user_id = self.__user_service.login(email, password)
        vo = self.__get_user(user_id)
        token = self.__jwt_service.create_token(user_id)
        vo.token = token
        return vo

    def validate_token(self, token: str, role: Role | None) -> UserVO:
        user_id = self.__jwt_service.decode_token(token)
        if not role:
            return self.__get_user(user_id)
        match role:
            case Role.MANAGER:
                return self.__user_service.get_manager(user_id)
            case Role.STUDENT:
                return self.__user_service.get_student(user_id)
        
    @staticmethod
    def initialize(key: str):
        if SessionService.shared is not None:
            return
        SessionService.shared = SessionService(key)