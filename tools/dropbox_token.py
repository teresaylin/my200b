#!/usr/bin/env python3

import sys
from dropbox.client import DropboxOAuth2FlowNoRedirect, DropboxClient
from dropbox import rest as dbrest

if __name__ == '__main__':
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import django
django.setup()
from django.conf import settings

auth_flow = DropboxOAuth2FlowNoRedirect(settings.DROPBOX_APP_KEY, settings.DROPBOX_APP_SECRET)

authorize_url = auth_flow.start()
print("1. Go to: " + authorize_url)
print("2. Click \"Allow\" (you might have to log in first).")
print("3. Copy the authorization code.")
auth_code = input("Enter the authorization code here: ").strip()

try:
    access_token, user_id = auth_flow.finish(auth_code)
except dbrest.ErrorResponse as e:
    print('Error: %s' % (e,))
    sys.exit(-1)

print('DROPBOX_ACCESS_TOKEN = "%s"' % (access_token,))