class InvalidID(Exception):
    def __init__(self):
        super().__init__("The given id is invalid.")

# class InvalidJSON(Exception):
#     "Raised when the given JSON is not valid for the current context."

# class InvalidFileExtension(Exception):
#     "Raised when the given file extension is not supported."

# class InvalidFileSize(Exception):
#     "Raied when the given file size is invalid."

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