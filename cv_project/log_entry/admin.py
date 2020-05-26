from django.contrib import admin

from .models import LogEntry


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ['id', 'timestamp', 'result']

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False
