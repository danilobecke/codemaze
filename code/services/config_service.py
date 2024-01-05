import os

from endpoints.models.configs_vo import ConfigsVO, LanguageConfigVO
from helpers.commons import create_test_script_download_url, scripts_path
from helpers.exceptions import ServerError
from services.runner_service import RunnerService

class ConfigService:
    def __init__(self, runner_service: RunnerService) -> None:
        self.__runner_service = runner_service

    def get_configs(self) -> ConfigsVO:
        languages: list[LanguageConfigVO] = []
        for language in self.__runner_service.allowed_languages():
            language_help = self.__runner_service.help_for_language(language)
            if language_help is None:
                raise ServerError()
            languages.append(LanguageConfigVO(language, list(self.__runner_service.allowed_extensions([language])), language_help))
        return ConfigsVO(create_test_script_download_url(), languages)

    def get_name_path_create_test_script(self) -> tuple[str, str]:
        filename = 'create_test_case.py'
        path = os.path.join(scripts_path(), filename)
        return (filename, path)
