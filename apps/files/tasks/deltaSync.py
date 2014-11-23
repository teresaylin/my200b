from datetime import datetime
from django.utils.timezone import utc
from django.conf import settings

from ..classes import AppDropboxClient
from ..models import Config, FileAppData

def log(msg):
    print('deltaSync(): '+msg)

def deltaSync():
    # Get config singleton
    config = Config.load()

    while True:
        # Retrieve delta information from Dropbox
        log('Retrieving delta...')
        cl = AppDropboxClient()
        data = cl.delta(
            cursor=config.deltaCursor,
            path_prefix=settings.DROPBOX_BASE_PATH
        )
        
        # Delete all local file entries if 'reset' is specified
        if data['reset']:
            log("'reset' specified, clearing local data...")
            for file in FileAppData.objects.all():
                # Call delete() rather than bulk delete
                file.delete()
            
        # Process entries
        for path, metadata in data['entries']:
            # Ensure path is lowercase (it should be according to API docs)
            path = path.lower()

            # Attempt to get existing file at specified path
            try:
                file = FileAppData.objects.get(path=path)
            except FileAppData.DoesNotExist:
                file = None
                    
            if metadata:
                # File was created

                if metadata['is_dir']:
                    if file:
                        # New file is a folder, and local data exists with the same path--delete it.
                        log("File '%s' is a folder, but local data exists. Deleting local data." % path)
                        file.delete()
                    else:
                        # New file is a folder, and no local data exists--ignore it.
                        log("Ignoring folder '%s'." % path)
                else:
                    if file:
                        # New file is a file, and local data exists--ignore it.
                        log("Ignoring file '%s'. Local data exists." % path)
                    else:
                        # New file is a file, and no local data exists--create local data.
                        log("Creating file '%s'." % path)
                        file = FileAppData(path=path)
                        file.save()
            else:
                # File was deleted
                
                if file:
                    # Delete file
                    log("Deleting file '%s'." % path)
                    file.delete()
                else:
                    log("Got delete event for file '%s', but no local data exists." % path)
                    
                # Annoyingly, the Dropbox API spec doesn't guarantee it will send delete events for descendant files in a folder,
                # so delete any local data that inherits this path.
                files = FileAppData.objects.filter(path__startswith=path+'/')
                for file in files:
                    # Call delete() rather than bulk delete
                    log("Deleting descendant file '%s'." % path)
                    file.delete()

        # Update config object
        config.deltaCursor = data['cursor']
        config.lastDeltaSync = datetime.utcnow().replace(tzinfo=utc)
            
        # Can continue calling delta() if 'has_more' is True
        if data['has_more']:
            log("'has_more' is set, continuing...")
            continue
        else:
            break
        
    # Save config object
    config.save()
    
    log('Done!')