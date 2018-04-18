#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os


def development():
    if os.environ['SERVER_SOFTWARE'].find('Development') == 0:
        return True
    else:
        return False


CURRENT_URL = "{}://{}".format(
    str(os.environ.get('wsgi.url_scheme')),
    str(os.environ.get('HTTP_HOST')))
