import os
import sys

path = '/home/kunjladani22/supertech_mobila57462'

if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'PROJECT_NAME.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()