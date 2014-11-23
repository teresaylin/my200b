from django.conf.urls import patterns, include, url

from .views import *

urlpatterns = patterns('',
    url(r'^create-folder/$', CreateFolderView.as_view(), name='create-folder'),
    url(r'^delete/$', DeleteView.as_view(), name='delete'),
    url(r'^download(?P<path>/.+)$', DownloadView.as_view(), name='download'),
    url(r'^metadata(?P<path>/.+)$', MetadataView.as_view(), name='metadata'),
    url(r'^previews(?P<path>/.+)$', PreviewView.as_view(), name='preview'),
    url(r'^search(?P<path>/.+)$', SearchView.as_view(), name='search'),
    url(r'^thumbnails(?P<path>/.+)/(?P<size>[a-z][a-z]?)\.(?P<format>[a-z]+)$', ThumbnailView.as_view(), name='thumbnail'),
    url(r'^upload/$', UploadView.as_view(), name='upload'),

    url(r'^dropbox-webhook/$', DropboxWebhookView.as_view(), name='dropbox-webhook'),
)
