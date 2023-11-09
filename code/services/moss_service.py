from mosspy import Moss # type: ignore

from helpers.codemaze_logger import CodemazeLogger
from helpers.commons import secure_filename

class MossService:
    def __init__(self, user_id: str) -> None:
        self.__user_id = user_id

    def get_report(self, source_file_path_name_list: list[tuple[str, str]], language: str) -> str | None:
        moss = Moss(self.__user_id, language)
        if language not in moss.getLanguages():
            return None
        try:
            for path, name in source_file_path_name_list:
                moss.addFile(path, secure_filename(name))
            return str(moss.send())
        # pylint: disable=broad-exception-caught
        except Exception:
            CodemazeLogger.shared().exception('MOSS Service has failed.')
            return None
