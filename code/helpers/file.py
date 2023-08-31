import os
import uuid

from helpers import commons
from helpers.exceptions import InvalidFileExtension, InvalidFileSize

class File:
    def __init__(self, filename: str, blob: bytes):
        self.filename = filename
        self.blob = blob

    # pylint: disable=dangerous-default-value
    def save(self, allowed_extensions: set[str] = commons.ALLOWED_TEXT_EXTENSIONS, max_file_size_mb: float = 1) -> str:
        file_extension = commons.file_extension(self.filename)
        if self.filename.strip() == '' or file_extension not in allowed_extensions:
            raise InvalidFileExtension(allowed_extensions)
        if len(self.blob) <= 0 or (len(self.blob) / (1024 * 1024)) > max_file_size_mb:
            raise InvalidFileSize(f'{max_file_size_mb} MB')
        secure_filename = str(uuid.uuid4()) + file_extension
        full_path = os.path.join(commons.storage_path(), secure_filename)
        with open(full_path, 'wb') as file:
            file.write(self.blob)
            return full_path
