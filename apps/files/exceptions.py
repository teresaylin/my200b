from rest_framework.exceptions import APIException

class DropboxError(APIException):
    status_code = 400
    default_detail = 'Dropbox error'

class InvalidPath(APIException):
    status_code = 400
    default_detail = 'Invalid path'

class FileNotFound(APIException):
    status_code = 404
    default_detail = 'File not found'

class FileAlreadyExists(APIException):
    status_code = 400
    default_detail = 'File already exists'