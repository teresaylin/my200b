from rest_framework.exceptions import APIException

class TaskAlreadyAssignedToUser(APIException):
    status_code = 400
    default_detail = 'User is already assigned to this task'

class TaskAlreadyAssignedToTaskForce(APIException):
    status_code = 400
    default_detail = 'Task force is already assigned to this task'