from application.libraries.helpers.dictionary_functions import wrap_json
import logging
import os
import sys
import re


class ErrorHandler:
    def init(self, request):
        self.rx = r'^(/api/v(\d{1,2})(/{0,1}\w+){0,})'
        """this regex will ensure to output json only to url's forming /api/v*/*"""

        self.tv = {}

        self.api_response = {}

        self.local = False
        if "127.0.0.1" in request.uri or "localhost" in request.uri:
            self.local = True
        self.tv["local"] = self.local

        self.tv["version"] = os.environ['CURRENT_VERSION_ID']
        if "?" in request.uri:
            self.tv["current_base_url"] = (
                request.uri[0:(request.uri.find('?'))]
            )
        else:
            self.tv["current_base_url"] = request.uri
        return self

    @classmethod
    def not_implemented(cls, request, res, exception):
        error_handler = cls().init(request)
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logging.error(
            str(exc_value),
            exc_info=(exc_type, exc_value, exc_traceback))

        if re.search(error_handler.rx, str(request.path)):
            error_handler.api_response = {
                "code": 501,
                "success": False,
                "description": (
                    'The ' +
                    request.method +
                    ' method is not supported for this endpoint.'
                )
            }
            res.headers["Content-Type"] = "application/json"
            wrap_json(res, error_handler.api_response)
        else:
            res.write("UnsupportedMethodError")

    @classmethod
    def log_exception(cls, request, res, exception):
        error_handler = cls().init(request)
        exc_type, exc_value, exc_traceback = sys.exc_info()

        error_handler.api_response = {
            "code": 500,
            "success": False,
            "description": re.sub(
                error_handler.rx, "", str(exc_value))
        }

        if re.search(error_handler.rx, str(request.path)):
            error_handler.api_response.update({
                "code": 400
            })

            if hasattr(exception, "msg"):
                error_handler.api_response.update({
                    "error_msg": exception.msg
                })

            if hasattr(exception, "path"):
                error_handler.api_response["path"] = \
                    [str(p) for p in exception.path]

            if hasattr(exception, "errors"):
                error_handler.api_response["errors"] = [
                    {
                        "msg": error.msg,
                        "path": [str(p) for p in error.path]
                    }
                    for error in exception.errors
                ]

            if hasattr(exc_type, "code"):
                logging.info("Error code: " + str(exc_type.code))
                logging.info(
                    str(exc_value),
                    exc_info=(exc_type, exc_value, exc_traceback))
                error_handler.api_response["code"] = int(exc_type.code)

            else:
                logging.error(
                    str(exc_value),
                    exc_info=(exc_type, exc_value, exc_traceback))

            if '(key=Key(\'' in error_handler.api_response['description']:
                error_handler.api_response['description'] = 'BadValueError'
            res.headers["Content-Type"] = "application/json"
            wrap_json(res, error_handler.api_response)
        else:
            logging.error(
                str(exc_value),
                exc_info=(exc_type, exc_value, exc_traceback))
            res.write("ServerError ** edit me!!")
    
    @classmethod
    def log_not_found(cls, request, res, exception):
        error_handler = cls().init(request)
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logging.error(
            str(exc_value),
            exc_info=(exc_type, exc_value, exc_traceback))

        if re.search(error_handler.rx, str(request.path)):
            error_handler.api_response = {
                "code": exc_type.code or 404,
                "success": False,
                "description": "This endpoint does not exist."
            }

            res.headers["Content-Type"] = "application/json"
            wrap_json(res, error_handler.api_response)
        else:
            res.write("EndpointNotFound")
