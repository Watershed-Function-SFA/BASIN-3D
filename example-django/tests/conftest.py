import os
import sys

import django
configured = False

def configure():

    global configured
    if not configured:
        sys.path.append('{}/../../example-django'.format(os.path.dirname(__file__)))
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mybroker.settings")
        django.setup()
        configured=True


configure()