from endpoints.models.task_vo import TaskVO
from endpoints.models.tcase_vo import TCaseVO
from endpoints.models.user import UserVO
from helpers.file import File
from services.runner_service import RunnerService

class ResultService:
    def __init__(self) -> None:
        self.__runner_service = RunnerService()

    def run(self, user: UserVO, task: TaskVO, tests: list[TCaseVO], file: File):
        # validate start/end date, max attempts
        file_path = file.save(self.__runner_service.allowed_extensions())
        self.__runner_service.run(file_path, tests)
