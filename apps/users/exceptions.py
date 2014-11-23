from rest_framework.exceptions import APIException

class UserNotFound(APIException):
    status_code = 404
    default_detail = 'User not found'

class UserAlreadyHasRole(APIException):
    status_code = 400
    default_detail = 'User already has role'

class TaskForceNotFound(APIException):
    status_code = 404
    default_detail = 'Task force not found'

class RoleNotFound(APIException):
    status_code = 404
    default_detail = 'Role not found'

class TeamNotFound(APIException):
    status_code = 404
    default_detail = 'Team not found'

class CommentThreadNotFound(APIException):
    status_code = 404
    default_detail = 'Thread not found'