import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'iluminare.settings_pro'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

path = '/srv/iluminare/src/'
if path not in sys.path:
    sys.path.append(path)

