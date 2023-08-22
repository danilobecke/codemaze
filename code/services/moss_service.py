from mosspy import Moss

class MossService:
    def __init__(self, user_id: int) -> None:
        self.__user_id = user_id

    def get_report(self, source_file_path_name_list: list[tuple[str, str]], language: str, output_list: list[str]):
        moss = Moss(self.__user_id, language)
        if language not in moss.getLanguages():
            return
        for path, name in source_file_path_name_list:
            moss.addFile(path, name)
        output_list.append(moss.send())
