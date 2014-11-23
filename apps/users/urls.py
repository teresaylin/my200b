from django.conf.urls import patterns, url
from rest_framework import routers

from users import views

urlpatterns = patterns('',
    #url(r'^$', views.IndexView.as_view(), name='index'),
    #url(r'^(?P<pk>\d+)/taskForce/$', views.TaskForceView.as_view(), name='taskForce'),
    #url(r'^(?P<pk>\d+)/userProfile/$', views.UserProfileView.as_view(), name='userProfile'),
)