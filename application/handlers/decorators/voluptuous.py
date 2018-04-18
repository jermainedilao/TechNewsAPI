import logging
import json
from application.libraries.helpers.dictionary_functions import flatten_dict
from application.libraries.helpers.dictionary_functions import flatten_form_data
from application.handlers.exceptions.client import UnauthorizedUser
from application.handlers.exceptions.client import InvalidRequestPayload
from application.libraries.voluptuous.voluptuous import Schema, REMOVE_EXTRA


def allowed_roles(roles=[]):
    def decorate(fn):
        def wrap(self, *args, **kwargs):
            if self.user.role not in roles:
                raise UnauthorizedUser()
            return fn(self, *args, **kwargs)
        return wrap
    return decorate


def validate_json_body(schema=None, required=False, extra=REMOVE_EXTRA):
    def decorate(fn):
        def wrap(self, *args, **kwargs):
            self.json_body = {}
            schema_validator = Schema(schema, required=required, extra=extra)
            try:
                content_type = self.request.headers.get('Content-Type')
                if content_type != "application/json":
                    raise Exception('Invalid Content-Type.')
            except:
                raise InvalidRequestPayload()
            self.json_body = schema_validator(json.loads(self.request.body))
            return fn(self, *args, **kwargs)
        return wrap
    return decorate


def validate_form_data(
        schema=None, required=False, extra=REMOVE_EXTRA):
    def decorate(fn):
        def wrap(self, *args, **kwargs):
            self.form_data = {}
            schema_validator = Schema(schema, required=required, extra=extra)
            self.form_data = schema_validator(
                flatten_dict(self.request.POST.dict_of_lists())
            )
            return fn(self, *args, **kwargs)
        return wrap
    return decorate


def validate_form_data_level(schema=None, required=False, extra=REMOVE_EXTRA):
    def decorate(fn):
        def wrap(self, *args, **kwargs):
            schema_validator = Schema(schema, required=required, extra=extra)
            schema_validator(
                flatten_dict(self.request.POST.dict_of_lists())
            )
            return fn(self, *args, **kwargs)
        return wrap
    return decorate


def validate_data_schema_form(fn):
    def wrap(self, *args, **kwargs):
        self.form_data = {}
        schema_validator = Schema(
            self.schema.pattern,
            required=self.schema.required,
            extra=self.schema.extra
        )
        test = flatten_dict(self.request.POST.dict_of_lists())
        logging.critical(test)
        self.form_data = schema_validator(
            test
        )
        return fn(self, *args, **kwargs)
    return wrap


def validate_data_schema_json(fn):
    def wrap(self, *args, **kwargs):
        self.json_body = {}
        schema_validator = Schema(
            self.schema.pattern,
            required=self.schema.required,
            extra=self.schema.extra
        )
        self.json_body = schema_validator(json.loads(self.request.body))
        return fn(self, *args, **kwargs)
    return wrap


def validate_json_body_form_data(schema, required=False, extra=REMOVE_EXTRA):
    def decorate(fn):
        def wrap(self, *args, **kwargs):
            self.form_data = {}
            schema_validator = Schema(schema, required=required, extra=extra)
            # try:
            #     content_type = self.request.headers.get('Content-Type')
            #     if "multipart/form-data" not in content_type:
            #         raise Exception('Invalid Content-Type.')
            # except Exception, e:
            #     raise InvalidRequestPayload()
            self.form_data = schema_validator(
                flatten_form_data(self.request.POST)
            )
            return fn(self, *args, **kwargs)
        return wrap
    return decorate
