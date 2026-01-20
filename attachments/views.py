"""
Views for file attachments.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import View, ListView
from django.views.generic.edit import FormView, DeleteView
from django.http import HttpResponseForbidden, HttpResponseRedirect, FileResponse
from django.urls import reverse_lazy, reverse
from django.core.exceptions import ValidationError
from tasks.models import Task
from .models import Attachment
from .forms import AttachmentUploadForm
from .storage import AzureBlobStorage
import logging

logger = logging.getLogger(__name__)


class AttachmentUploadView(LoginRequiredMixin, FormView):
    """View for uploading file attachments to tasks."""
    
    template_name = 'attachments/upload.html'
    form_class = AttachmentUploadForm
    
    def setup(self, request, *args, **kwargs):
        """Initialize attributes for the view."""
        super().setup(request, *args, **kwargs)
        self.task = get_object_or_404(Task, pk=self.kwargs['task_pk'])
    
    def dispatch(self, request, *args, **kwargs):
        """Check ownership before processing request."""
        # Call parent dispatch first - LoginRequiredMixin will handle authentication
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
            
        # If authenticated, verify task ownership
        if self.task.owner != request.user:
            return HttpResponseForbidden("You don't have permission to add attachments to this task.")
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        """Add task to context."""
        context = super().get_context_data(**kwargs)
        context['task'] = self.task
        context['attachment_count'] = Attachment.objects.filter(task=self.task).count()
        context['max_attachments'] = 5
        return context
    
    def form_valid(self, form):
        """Process valid form - upload file and create attachment record."""
        try:
            # Check attachment count limit (max 5)
            existing_count = Attachment.objects.filter(task=self.task).count()
            if existing_count >= 5:
                messages.error(self.request, "Maximum 5 attachments per task. Please delete an existing attachment first.")
                return self.form_invalid(form)
            
            file = form.cleaned_data['file']
            
            # Initialize storage backend
            storage = AzureBlobStorage()
            
            # Generate unique blob name
            blob_name = storage.generate_blob_name(self.task.id, file.name)
            
            # Save file to Azure Blob Storage
            storage.save(blob_name, file)
            
            # Create attachment record with metadata
            attachment = Attachment.objects.create(
                task=self.task,
                file_name=file.name,
                blob_name=blob_name,
                file_size=file.size,
                content_type=file.content_type
            )
            
            logger.info(f"File uploaded: {file.name} ({file.size} bytes) for task {self.task.id}")
            messages.success(self.request, f"File '{file.name}' uploaded successfully!")
            
            return redirect('tasks:detail', pk=self.task.pk)
        
        except Exception as e:
            logger.error(f"File upload failed: {str(e)}")
            messages.error(self.request, f"Upload failed: {str(e)}")
            return self.form_invalid(form)
    
    def get_success_url(self):
        """Redirect to task detail page."""
        return reverse('tasks:detail', kwargs={'pk': self.task.pk})


class AttachmentListView(LoginRequiredMixin, ListView):
    """View for listing attachments for a task."""
    
    model = Attachment
    template_name = 'attachments/list.html'
    context_object_name = 'attachments'
    
    def get_queryset(self):
        """Get attachments for the specific task owned by current user."""
        self.task = get_object_or_404(Task, pk=self.kwargs['task_pk'])
        
        # Verify task ownership
        if self.task.owner != self.request.user:
            return Attachment.objects.none()
        
        return Attachment.objects.filter(task=self.task).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        """Add task to context."""
        context = super().get_context_data(**kwargs)
        context['task'] = self.task
        return context


class AttachmentDownloadView(LoginRequiredMixin, View):
    """View for downloading file attachments."""
    
    def get(self, request, *args, **kwargs):
        """Generate signed URL and redirect or stream file."""
        attachment = get_object_or_404(Attachment, pk=self.kwargs['pk'])
        
        # Verify ownership via task
        if attachment.task.owner != request.user:
            return HttpResponseForbidden("You don't have permission to download this attachment.")
        
        try:
            # Initialize storage backend
            storage = AzureBlobStorage()
            
            # Check if blob exists
            if not storage.exists(attachment.blob_name):
                messages.error(request, "File not found in storage.")
                return redirect('tasks:detail', pk=attachment.task.pk)
            
            # Generate signed URL (1-hour expiration)
            download_url = storage.get_signed_url(attachment.blob_name)
            
            # Redirect to signed URL
            return HttpResponseRedirect(download_url)
        
        except Exception as e:
            logger.error(f"Download failed for attachment {attachment.id}: {str(e)}")
            messages.error(request, "Download failed. Please try again.")
            return redirect('tasks:detail', pk=attachment.task.pk)


class AttachmentDeleteView(LoginRequiredMixin, DeleteView):
    """View for deleting file attachments."""
    
    model = Attachment
    template_name = 'attachments/delete_confirm.html'
    context_object_name = 'attachment'
    
    def dispatch(self, request, *args, **kwargs):
        """Check ownership before processing request."""
        # Call parent dispatch first - LoginRequiredMixin will handle authentication
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
            
        attachment = self.get_object()
        
        # Verify ownership via task
        if attachment.task.owner != request.user:
            return HttpResponseForbidden("You don't have permission to delete this attachment.")
        
        return super().dispatch(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        """Delete attachment - signal will handle blob deletion."""
        attachment = self.get_object()
        task_pk = attachment.task.pk
        
        # Delete attachment record from database
        # Signal will automatically delete blob from storage
        attachment.delete()
        
        messages.success(request, "Attachment deleted successfully.")
        return redirect('tasks:detail', pk=task_pk)
    
    def get_success_url(self):
        """Redirect to task detail page."""
        return reverse('tasks:detail', kwargs={'pk': self.object.task.pk})

