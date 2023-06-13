class InvalidID(Exception):
    "The given id is invalid."

# class InvalidJSON(Exception):
#     "Raised when the given JSON is not valid for the current context."

# class InvalidFileExtension(Exception):
#     "Raised when the given file extension is not supported."

# class InvalidFileSize(Exception):
#     "Raied when the given file size is invalid."

class NotFound(Exception):
    "The given id couldn't find any object of the given model."