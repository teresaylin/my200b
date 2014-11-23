from .common import *

WSGI_APPLICATION = 'my2009.wsgi-dev.application'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '_=-e4r)kiwe7vbif+64_bi$%$w1@jhwuz7+ac+ccn&2+tjvi=r'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}

