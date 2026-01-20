"""
Tests for file validators in attachments app.
"""
import pytest
from django.core.exceptions import ValidationError
from attachments.validators import (
    validate_file_size,
    validate_file_extension,
    validate_mime_type,
)


class TestFileSizeValidator:
    """Tests for file size validation."""
    
    def test_valid_file_size(self):
        """Test that files under 10MB pass validation."""
        # Mock file with 5MB size
        class MockFile:
            size = 5 * 1024 * 1024  # 5MB
        
        file = MockFile()
        # Should not raise exception
        validate_file_size(file)
    
    def test_file_size_exactly_10mb(self):
        """Test that exactly 10MB file passes validation."""
        class MockFile:
            size = 10 * 1024 * 1024  # 10MB
        
        file = MockFile()
        # Should not raise exception
        validate_file_size(file)
    
    def test_file_size_exceeds_limit(self):
        """Test that files over 10MB fail validation."""
        class MockFile:
            size = 11 * 1024 * 1024  # 11MB
        
        file = MockFile()
        with pytest.raises(ValidationError) as exc_info:
            validate_file_size(file)
        
        assert "File size exceeds 10MB limit" in str(exc_info.value)
    
    def test_empty_file(self):
        """Test that empty files fail validation."""
        class MockFile:
            size = 0
        
        file = MockFile()
        with pytest.raises(ValidationError) as exc_info:
            validate_file_size(file)
        
        assert "File is empty" in str(exc_info.value)


class TestFileExtensionValidator:
    """Tests for file extension validation."""
    
    @pytest.mark.parametrize("filename", [
        "document.pdf",
        "image.jpg",
        "image.jpeg",
        "image.png",
        "image.gif",
        "document.doc",
        "document.docx",
        "spreadsheet.xls",
        "spreadsheet.xlsx",
        "notes.txt",
        "data.csv",
        "archive.zip",
    ])
    def test_valid_extensions(self, filename):
        """Test that allowed file extensions pass validation."""
        class MockFile:
            name = filename
        
        file = MockFile()
        # Should not raise exception
        validate_file_extension(file)
    
    @pytest.mark.parametrize("filename", [
        "script.exe",
        "virus.bat",
        "program.sh",
        "code.py",
        "webpage.html",
        "style.css",
        "script.js",
    ])
    def test_invalid_extensions(self, filename):
        """Test that disallowed file extensions fail validation."""
        class MockFile:
            name = filename
        
        file = MockFile()
        with pytest.raises(ValidationError) as exc_info:
            validate_file_extension(file)
        
        error_message = str(exc_info.value)
        assert "not allowed" in error_message
    
    def test_case_insensitive_validation(self):
        """Test that extension validation is case-insensitive."""
        class MockFile:
            name = "DOCUMENT.PDF"
        
        file = MockFile()
        # Should not raise exception
        validate_file_extension(file)
    
    def test_no_extension(self):
        """Test that files without extension fail validation."""
        class MockFile:
            name = "filename_without_extension"
        
        file = MockFile()
        with pytest.raises(ValidationError) as exc_info:
            validate_file_extension(file)
        
        assert "File has no extension" in str(exc_info.value)


class TestMimeTypeValidator:
    """Tests for MIME type validation."""
    
    @pytest.mark.parametrize("mime_type,extension", [
        ("application/pdf", "pdf"),
        ("image/jpeg", "jpg"),
        ("image/png", "png"),
        ("image/gif", "gif"),
        ("text/plain", "txt"),
        ("text/csv", "csv"),
        ("application/zip", "zip"),
    ])
    def test_valid_mime_types(self, mime_type, extension, mocker):
        """Test that allowed MIME types pass validation."""
        class MockFile:
            name = f"test.{extension}"
            
            def read(self, size=None):
                return b"fake file content"
            
            def seek(self, pos):
                pass
        
        file = MockFile()
        
        # Mock filetype.guess to return a mock file type
        class MockKind:
            mime = mime_type
        
        mocker.patch('filetype.guess', return_value=MockKind())
        
        # Should not raise exception
        validate_mime_type(file)
    
    @pytest.mark.parametrize("mime_type", [
        "application/x-executable",
        "application/x-sh",
        "text/html",
        "application/javascript",
        "application/x-python-code",
    ])
    def test_invalid_mime_types(self, mime_type, mocker):
        """Test that disallowed MIME types fail validation."""
        class MockFile:
            name = "test.exe"
            
            def read(self, size=None):
                return b"fake file content"
            
            def seek(self, pos):
                pass
        
        file = MockFile()
        
        # Mock filetype.guess to return a mock file type
        class MockKind:
            mime = mime_type
        
        mocker.patch('filetype.guess', return_value=MockKind())
        
        with pytest.raises(ValidationError) as exc_info:
            validate_mime_type(file)
        
        assert "File type not allowed" in str(exc_info.value)
