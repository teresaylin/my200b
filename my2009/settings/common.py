"""
Django settings for my2009 project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

ALLOWED_HOSTS = []

# Add request object to template contexts
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP
TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.core.context_processors.request',
)

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',

    'apps.events',
    'apps.files',
    'apps.tasks',
    'apps.users',
    'apps.user_tracking',
    'apps.webapp',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.user_tracking.middleware.UserTrackingMiddleware',
)

ROOT_URLCONF = 'my2009.urls'

WSGI_APPLICATION = 'my2009.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

# Authentication URLs
LOGIN_URL = '/app/login'
LOGIN_REDIRECT_URL = '/app'

# REST framework setup
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
        'libs.permissions.rest.ObjectPermissions',
     ),
    'DEFAULT_FILTER_BACKENDS': (
        'libs.permissions.rest.ObjectPermissionsFilter',
        'rest_framework.filters.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter'
    ),
    'PAGINATE_BY_PARAM': 'page_size',
}

FILE_THUMBNAIL_CACHE_TIMEOUT = 5*60    # Number of seconds to cache Dropbox thumbnails
FILE_METADATA_CACHE_TIMEOUT = 60*60    # Number of seconds to cache Dropbox file metadata