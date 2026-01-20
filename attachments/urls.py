"""
URL patterns for attachments app.
"""
from django.urls import path
from . import views

app_name = 'attachments'

urlpatterns = [
    # File upload
    path(
        'tasks/<int:task_pk>/attachments/upload/',
        views.AttachmentUploadView.as_view(),
        name='upload'
    ),
    
    # View attachments list
    path(
        'tasks/<int:task_pk>/attachments/',
        views.AttachmentListView.as_view(),
        name='list'
    ),
    
    # Download attachment
    path(
        'attachments/<int:pk>/download/',
        views.AttachmentDownloadView.as_view(),
        name='download'
    ),
    
    # Delete attachment
    path(
        'attachments/<int:pk>/delete/',
        views.AttachmentDeleteView.as_view(),
        name='delete'
    ),
]
