from django.contrib import admin

from .models import FileAppData

class FileAppDataAdmin(admin.ModelAdmin):
    list_display = ('path',)
admin.site.register(FileAppData, FileAppDataAdmin)