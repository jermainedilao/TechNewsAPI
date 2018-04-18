#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
import json
import jinja2
import webapp2
import logging
import datetime

from application.config import constants
from application.config import settings


jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader('application/frontend/templates/'),
    autoescape=True, trim_blocks=True,
    extensions=['jinja2.ext.with_'])
jinja_env.globals['uri_for'] = webapp2.uri_for


class BaseHandler(webapp2.RequestHandler):
    def __init__(self, request=None, response=None):
        self.initialize(request, response)

        self.tv = {}
        self.tv["version"] = os.environ['CURRENT_VERSION_ID']
        self.session = None
        self.custom_code = None
        self.cookie_session = None
        self.user = None
        self.api_response = {}
        self.current_uri = os.environ['PATH_INFO']
        self.ip_address = os.environ.get('REMOTE_ADDR')
        self.http_user_agent = os.environ.get('HTTP_USER_AGENT')
        self.now = datetime.datetime.now()
        self.now_adjusted = self.now + datetime.timedelta(hours=8)

    def render(self, template_path=None, force=False):
        cache_control = 'no-cache, no-store, must-revalidate'
        self.response.headers['Cache-Control'] = cache_control
        self.response.headers['Pragma'] = 'no-cache'
        self.response.headers['Expires'] = '0'
        self.response.headers['X-Frame-Options'] = 'DENY'

        self.tv['CURRENT_URI'] = self.current_uri
        self.tv['NAVBAR'] = True
        self.tv['FOOTER'] = True
        self.tv['BASE_URL'] = self.request.application_url
        self.tv['user'] = self.user
        self.tv['current_timestamp'] = time.mktime(self.now.timetuple())
        self.tv['current_url'] = self.request.uri
        self.tv['constants'] = constants
        self.tv['settings'] = settings
        self.tv['ph_time'] = datetime.datetime.now()
        self.tv['ph_time'] += datetime.timedelta(hours=8)

        template = jinja_env.get_template(template_path)
        self.response.out.write(template.render(self.tv))

    def api_render(self):
        self.response.headers['Content-Type'] = 'application/json'

        if self.custom_code and self.custom_code != 200:
            logging.debug('code: {}'.format(self.custom_code))
            self.response.set_status(self.custom_code)
        elif 'code' in self.api_response and self.api_response['code'] != 200:
            logging.debug('code: {}'.format(str(self.api_response['code'])))
            self.response.set_status(self.api_response['code'])

        try:
            logging.info('API Response >> ')
            logging.info(self.api_response)
        except Exception:
            logging.exception('error logging api_response')

        self.response.out.write(json.dumps(self.api_response))

    def get_arg(self, arg, default=None):
        if default:
            result = self.request.get(arg, default)
        else:
            result = self.request.get(arg)

        try:
            if result.startswith('"') and result.endswith('"'):
                # Decode with unicode-escape to get Py2 unicode/Py3 str, but interpreted
                # incorrectly as latin-1
                result = result.encode('utf8')
                badlatin = result.decode('unicode-escape')

                # Encode back as latin-1 to get back the raw bytes (it's a 1-1 encoding),
                # then decode them properly as utf-8
                result = badlatin.encode('latin-1').decode('utf-8')
        except AttributeError:
            return None
        except:
            logging.exception('error in decoding argument')

        try:
            if result.startswith('"') and result.endswith('"'):
                result = result[1:-1]
        except AttributeError:
            return None
        except:
            logging.exception('error in retrieving argument 2')
        return result
