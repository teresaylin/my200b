from django.contrib import admin

from .models import UserTracking

class UserTrackingAdmin(admin.ModelAdmin):
    list_display = ('user', 'lastSeen')
admin.site.register(UserTracking, UserTrackingAdmin)