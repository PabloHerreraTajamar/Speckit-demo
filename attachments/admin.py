from django.contrib import admin
from .models import Attachment


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    """Admin interface for Attachment model."""
    
    list_display = ('file_name', 'task', 'file_size', 'content_type', 'created_at')
    list_filter = ('content_type', 'created_at')
    search_fields = ('file_name', 'task__title', 'blob_name')
    readonly_fields = ('created_at', 'file_size', 'content_type', 'blob_name')
    
    fieldsets = (
        ('File Information', {
            'fields': ('file_name', 'content_type', 'file_size')
        }),
        ('Storage', {
            'fields': ('blob_name',)
        }),
        ('Association', {
            'fields': ('task',)
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )

