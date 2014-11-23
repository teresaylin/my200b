from django.conf import settings
from rest_framework.exceptions import PermissionDenied
import posixpath

def userPathToDropboxPath(path, user):
    # Canonicalize path
    path = posixpath.normpath(posixpath.join('/', path))

    # Check first directory of path is the team name of a team the user is a member of (case insensitive)
    teamName = path.split('/', 2)[1].lower()
    if not teamName in [team.color.lower() for team in user.teams.all()]:
        raise PermissionDenied()
    
    # Prepend app base directory
    path = settings.DROPBOX_BASE_PATH + path
    
    return path

def dropboxPathToUserPath(path):
    # Verify path starts with base directory (case insensitive)
    if not path.lower().startswith(settings.DROPBOX_BASE_PATH.lower()):
        raise ValueError('Path does not start with DROPBOX_BASE_PATH')
    
    # Remove base path
    path = path[len(settings.DROPBOX_BASE_PATH):]
    
    if path == '':
        path = '/'
    
    return path

def isValidDropboxFilename(name):
    BAD_FILENAME_CHARS = list('[]/\=+<>:;",*')
    for c in File.BAD_FILENAME_CHARS:
        if c in name:
            return False

    return True