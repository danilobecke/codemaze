class InvalidFileExtension(Exception):
    def __init__(self):
        super().__init__("The given file extension is not supported.")

class InvalidFileSize(Exception):
    def __init__(self, max_allowed: str):
        super().__init__(f"The given file size is invalid. The maximum allowed is {max_allowed}.")

class NotFound(Exception):
    def __init__(self):
        super().__init__("The given id couldn't find any object of the given resource.")

class Forbidden(Exception):
    def __init__(self):
        super().__init__("Unable to access.")

class ServerError(Exception):
    def __init__(self):
        super().__init__("Something went wrong.")

class Unauthorized(Exception):
    def __init__(self):
        super().__init__("Log in to an authorized account to gain access to this resource.")

class Internal_UniqueViolation(Exception):
    "Raised when the unique constraint was violated on the database."

class Conflict(Exception):
    def __init__(self):
        super().__init__("This request was made already.")

class ParameterValidationError(Exception):
    def __init__(self, key: str, value: str, type: str) -> None:
        super().__init__(f"{key}: {value} is not a valid {type}")
