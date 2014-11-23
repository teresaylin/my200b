from django.conf import settings
import dropbox
from dropbox.client import format_path

class AppDropboxClient(dropbox.client.DropboxClient):

    def __init__(self, **kwargs):
        super().__init__(settings.DROPBOX_ACCESS_TOKEN)

    def preview(self, from_path, rev=None):
        """
        Generate a PDF/HTML preview of a file.
        
        Note: this functionality is missing from the Python Dropbox module as of v2.2.0.
        Please remove this function if/when it is added to the official module.
        """
        path = "/previews/%s%s" % (self.session.root, format_path(from_path))
        
        params = {}
        if rev:
            params['rev'] = rev

        url, params, headers = self.request(path, params, method='GET', content_server=True)
        return self.rest_client.request("GET", url, headers=headers, raw_response=True)