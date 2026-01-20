"""
Forms for file attachments.
"""
from django import forms
from django.core.exceptions import ValidationError
from .validators import validate_file_size, validate_file_extension
from .models import Attachment


class AttachmentUploadForm(forms.Form):
    """Form for uploading file attachments to tasks."""
    
    file = forms.FileField(
        label='Choose file',
        help_text='Max 10MB. Allowed: PDF, DOC, DOCX, XLS, XLSX, TXT, JPG, PNG',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.doc,.docx,.xls,.xlsx,.txt,.jpg,.jpeg,.png'
        })
    )
    
    def clean_file(self):
        """Validate uploaded file."""
        file = self.cleaned_data.get('file')
        
        if not file:
            raise ValidationError("No file provided")
        
        # Validate file size
        validate_file_size(file)
        
        # Validate file extension
        validate_file_extension(file.name)
        
        return file
