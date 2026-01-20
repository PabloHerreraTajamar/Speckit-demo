"""
File validators for Task Attachment uploads.
Validates file size, extensions, and MIME types.
"""
import filetype
from django.core.exceptions import ValidationError


# Maximum file size: 10MB
MAX_FILE_SIZE = 10 * 1024 * 1024

# Allowed file extensions
ALLOWED_EXTENSIONS = [
    'pdf', 'jpg', 'jpeg', 'png', 'gif',
    'doc', 'docx', 'xls', 'xlsx',
    'txt', 'csv', 'zip'
]

# Allowed MIME types
ALLOWED_MIME_TYPES = [
    'application/pdf',
    'image/jpeg',
    'image/png',
    'image/gif',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/plain',
    'text/csv',
    'application/zip',
    'application/x-zip-compressed',
]


def validate_file_size(file):
    """
    Validate that file size does not exceed 10MB and is not empty.
    
    Args:
        file: Django UploadedFile object
        
    Raises:
        ValidationError: If file is empty or exceeds size limit
    """
    if file.size == 0:
        raise ValidationError("File is empty.")
    
    if file.size > MAX_FILE_SIZE:
        raise ValidationError(
            f"File size exceeds 10MB limit. Current size: {file.size / (1024*1024):.2f}MB"
        )


def validate_file_extension(file):
    """
    Validate that file has an allowed extension.
    
    Args:
        file: Django UploadedFile object or filename string
        
    Raises:
        ValidationError: If file extension is not allowed or missing
    """
    # Handle both file object and string
    filename = file.name if hasattr(file, 'name') else file
    
    # Check if file has an extension
    if '.' not in filename:
        raise ValidationError("File has no extension.")
    
    # Extract extension and validate
    extension = filename.rsplit('.', 1)[1].lower()
    
    if extension not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            f"File extension '.{extension}' not allowed. "
            f"Allowed extensions: {', '.join(ALLOWED_EXTENSIONS)}"
        )


def validate_mime_type(file):
    """
    Validate that file MIME type matches allowed types.
    Uses filetype library to detect actual file content type.
    
    Args:
        file: Django UploadedFile object
        
    Raises:
        ValidationError: If MIME type is not allowed
    """
    # Read file content for MIME type detection
    file_content = file.read(2048)  # Read first 2KB
    file.seek(0)  # Reset file pointer
    
    # Detect file type using filetype
    kind = filetype.guess(file_content)
    
    if kind is None:
        # Try to determine from extension for text files
        extension = file.name.rsplit('.', 1)[1].lower() if '.' in file.name else ''
        if extension in ['txt', 'csv']:
            mime_type = 'text/plain' if extension == 'txt' else 'text/csv'
        else:
            raise ValidationError("Could not determine file type.")
    else:
        mime_type = kind.mime
    
    if mime_type not in ALLOWED_MIME_TYPES:
        raise ValidationError(
            f"File type not allowed. Detected type: {mime_type}"
        )
