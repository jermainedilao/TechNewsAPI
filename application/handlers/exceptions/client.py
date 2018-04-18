# client exceptions
class Error(Exception):
    code = 400
    def __str__(self):
        return str(self.msg)


# --------------------------------
class MissingRequestParameter(Error):
    # code = 463
    def __init__(self, variable):
        self.msg = "The request is missing a parameter '" +  variable + "'."


class InvalidArgumentException(Error):
    def __init__(self, variable):
        self.msg = "Invalid argument during processing'" + (' ' + variable) + \
                   "'."


class NotAccepted(Error):
    code = 406
    def __init__(self, variable=None):
        self.msg = "The request contained an unacceptable content." + (
            (" Please check `" + variable + "`.") \
            if variable else ""
        )


class EntityNotFoundException(Error):
    code = 404
    def __init__(self, entity_id):
        self.msg = "Entity associated to '" + str(entity_id) + \
        "' does not exist."


class UnauthorizedUser(Error):
    code = 401
    def __init__(self):
        self.msg = "You are not allowed to access this endpoint."


class InvalidRequestPayload(Error):
    def __init__(self, extra=""):
        self.msg = 'The request does not have a valid request payload. ' + extra


class DataDuplication(Error):
    def __init__(self):
        self.msg = 'This request will create a duplicated data which is not ' \
                   'allowed.'


class InvalidCredentials(Error):
    def __init__(self):
        self.msg = 'The credentials you sent are invalid.'


# used for voluptuous
class InvalidData(Error):
    def __init__(self, msg, errors=None, path=None):
        self.msg = msg
        if errors:
            self.errors = errors
        if path:
            self.path = path
