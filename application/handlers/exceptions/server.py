# server exceptions
class Error(Exception):
    code = 500

    def __init__(self, msg=""):
        self.msg = msg

    def __str__(self):
        return str(self.msg)


# --------------------------------
class InvalidVariable(Error):
    code = 501

    def __init__(self):
        self.msg = 'The server encountered some unexpected values, this is a '
        'server error, please report emmediately to the webmaster.'


class ExhaustedRetries(Error):
    code = 500

    def __init__(self):
        self.msg = 'The process exhausted the maximum attempts or retries it ' \
                   'can make. This is a server error, please report ' \
                   'immediately.'
