import logging
import json
import urlparse
import urllib
import re
from application.libraries.helpers.exception_functions import api_assert_param
from application.handlers.exceptions.client import InvalidArgumentException
from application.handlers.exceptions.client import MissingRequestParameter


def wrap_json(user_response, api_response, callback=False):
    """Creates a wrapped json response for the controller.

    Note:
        This function will right away write to the stdout response.

    Args:
        user_response (HttpResponse): The reponse object for the user.

        response (dict): The dictionary containing the data to be written to
            the response stdout.

        callback (def): a callback function, but currently not used.

    Examples:
        >>> wrap_json(response, self.api_resonse)
        # will wrap the data inside the self.tv dictionary
    """
    if "code" in api_response:
        try:
            response_code = int(api_response['code'])
            user_response.set_status(
                response_code, "Error")
        except:
            logging.exception("Cannot set Status Code Header")
    user_response.headers['Content-Type'] = "application/json"
    response_text = json.dumps(api_response, False, False)
    user_response.out.write(response_text)
    logging.debug("RESPONSE:")
    logging.debug(response_text)
    return


def add_url_params(uri, params={}, remove=[], doseq=True):
    """Adds the params to the uri

    Args:
        params (dict): the parameters
    """

    url_parts = list(urlparse.urlparse(uri))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(params)
    for rem in remove:
        if rem in query.keys():
            del query[rem]

    url_parts[4] = urllib.urlencode(query, doseq = doseq)

    return urlparse.urlunparse(url_parts)


def flatten_dict(dictionary):
    """Flattens a dictionary, removes the list attribute of value
    if len(val) is only 1

    Args:
        dictionary (dict) : the dictionary to flatten

    Example:
        >>> flatten_dict({
        ...     'a': {'x': 2, 'v': [1, 2], 'f': [3]},
        ...     'c': [5],
        ...     'b': [1, 2, 3, 4]
        ... })
        {'a': {'x': 2, 'z': 1, 'v': [1, 2], 'f': 3}, 'c': 5, 'b': [1, 2, 3, 4]}
    """
    out = {}

    for key, value in dictionary.iteritems():
        is_list = re.match(r'\w+\[\]', key)
        if type(value) is dict and not is_list:
            out[key] = flatten_dict(value)
        elif type(value) is list and len(value) == 1 and not is_list:
            out[key] = value[0]
        else:
            out[key] = value

    return out


def flatten_form_data(form_data):
    # out = {}
    # for key, value in form_data.dict_of_lists().iteritems():
    #     if key not in form_data.getall("list_field"):
    #         out[key] = form_data.get(key)

    # for field in form_data.getall("list_field"):
    #     out[field] = form_data.getall(field)

    out = json.loads(form_data.get("fields"))

    for _file in form_data.getall("file"):
        out[_file] = form_data.get(_file)

    for _file in form_data.getall("files"):
        out[_file] = form_data.getall(_file)

    return out


def check_parameters(params={}):
    """Decorate endpoints with this to check your required parameters

    Args:
        params (dict): The dictionary containing the required parameters schema
            in this format `{'param': type|choices|or}` where `or` is the same
            format

    Raises:
        MissingRequestParameter : If the parameter does not exist in the request
        InvalidArgumentException : if the type of the parameter could not be
            parsed or if the value of the parameter does not exist in the
            choices provded as the parameters value

    Notes:
        This will will raise an API exception so excepting response will be in
        JSON.
        For the parameter types, only python default types are allowed, giving
        unknown types will result in Server error.
        Use only on 1-level deep dictionary. Giving deeper ones will
        result in an unexpected behaviour. Just make it simple.

        You can create you own checker, please see below.
        Create a checker with the params (webapp2.RequestHandler, name, value)
        and return True to skip the other checkers after it.

    Todo:
        refactor to use voluptuous

    Examples:
        >>> check_parameters({'cmd':str,'image':file,'type': ['aType','bType']})
        >>> check_parameters({'cmd':str,'_or':{'aval':str,'bval':int}})
        >>> check_parameters({'cmd':str,'multi':'aVal,bVal,cVal'})
        # will fail if no atleast one is present in multi, separated by comma
    """
    """processors"""
    def single_choices(self, name, val):
        if type(val) is list:
            if self.request.get(name) not in val:
                raise InvalidArgumentException(name)
            return True

    def multi_choices(self, name, val):
        if type(val) is str:
            # arrange the required and submitted values
            arg = self.request.get(name).split(',')
            val = val.split(',')
            val.sort()
            arg.sort()
            if not set(arg) <= set(val):
                raise InvalidArgumentException(name)
            self.params[name] = arg
            return True

    def file_data(self, name, val):
        try:
            if val is file:
                value = self.request.POST.get(name)
                api_assert_param(
                    str(value.__class__) == "cgi.FieldStorage",
                    name
                )
                self.params[name] = value
                return True
        except:
            raise InvalidArgumentException(name)

    def default(self, name, val):
        try:
            logging.info(name)
            logging.info(val)
            self.params[name] = val(self.request.get(name))
        except:
            raise InvalidArgumentException(name)
        return True

    """the main process"""
    __processors__ = [single_choices, multi_choices, file_data, default]

    def process(self, req_params):
        for name, val in req_params.iteritems():
            if name == '_or':
                # TODO: needs to fix this part
                process(val)
                continue
            if name not in self.request.arguments():
                raise MissingRequestParameter(name)
            # iterate over processors
            for processor in __processors__:
                if processor(self, name, val):
                    break
        logging.info(self.params)

    def decorate(fn):
        def wrap(self, *args, **kwargs):
            self.params = {}
            process(self, params)
            return fn(self, *args, **kwargs)
        return wrap
    return decorate
