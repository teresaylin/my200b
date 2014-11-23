import os

from .common import *

# Get SECRET_KEY from environment
SECRET_KEY = os.environ['SECRET_KEY']

# Ensure debug settings are disabled
DEBUG = False
TEMPLATE_DEBUG = False
