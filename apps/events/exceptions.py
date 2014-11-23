from rest_framework.exceptions import APIException

class EventEndPrecedesStart(APIException):
    status_code = 400
    default_detail = 'End time precedes start time'

class EventAlreadyHasAttendee(APIException):
    status_code = 400
    default_detail = 'User is already an attendee'