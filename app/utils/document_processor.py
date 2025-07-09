"""
Document processing utilities for identifying file types and extracting text content.
"""
from typing import Dict, Any, Tuple, BinaryIO, Optional
import os
import tempfile
import mimetypes
from pathlib import Path
import io

# Import file type specific parsers
try:
    import pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

try:
    import pytesseract
    from PIL import Image
    OCR_SUPPORT = True
except ImportError:
    OCR_SUPPORT = False

try:
    import docx
    DOCX_SUPPORT = True
except ImportError:
    DOCX_SUPPORT = False


class UnsupportedFileTypeError(Exception):
    """Raised when file type is not supported."""
    pass


class ExtractionError(Exception):
    """Raised when text extraction fails."""
    pass


def identify_file_type(file: BinaryIO) -> str:
    """
    Identify the type of the uploaded file.
    
    Args:
        file: File-like object
        
    Returns:
        str: File type ("pdf", "image", "docx", "txt", etc.)
        
    Raises:
        UnsupportedFileTypeError: If file type cannot be determined or is not supported
    """
    # Store current position to restore it later
    current_pos = file.tell()
    
    # Read first few bytes to detect file signature
    header = file.read(8)
    file.seek(current_pos)  # Reset position
    
    # Get filename if available
    filename = getattr(file, 'filename', None)
    if filename:
        # Use mimetypes to guess based on filename
        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type:
            if mime_type == 'application/pdf':
                return 'pdf'
            elif mime_type.startswith('image/'):
                return 'image'
            elif mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                return 'docx'
            elif mime_type == 'text/plain':
                return 'txt'
    
    # Check file signatures as fallback
    # PDF signature check
    if header.startswith(b'%PDF'):
        return 'pdf'
    # DOCX is a ZIP file with specific contents
    if header.startswith(b'PK\x03\x04'):
        return 'docx'  # This is approximate, as other Office formats are also ZIP-based
    # Common image formats
    if header.startswith(b'\xFF\xD8\xFF'):  # JPEG
        return 'image'
    if header.startswith(b'\x89PNG\r\n\x1A\n'):  # PNG
        return 'image'
    if header.startswith(b'GIF87a') or header.startswith(b'GIF89a'):  # GIF
        return 'image'
    if header.startswith(b'\x42\x4D'):  # BMP
        return 'image'
    # Text file - check if mostly ASCII
    file.seek(current_pos)
    sample = file.read(1024)
    file.seek(current_pos)
    if isinstance(sample, bytes) and all(b > 8 and b < 127 for b in sample if b != 10 and b != 13):
        return 'txt'
    
    raise UnsupportedFileTypeError("File type not supported or cannot be determined")


def extract_text_from_pdf(file: BinaryIO) -> str:
    """
    Extract text from a PDF file.
    
    Args:
        file: PDF file object
        
    Returns:
        str: Extracted text content
        
    Raises:
        ExtractionError: If text extraction fails
    """
    if not PDF_SUPPORT:
        raise ExtractionError("PDF extraction not supported. Please install pdfplumber package.")
    
    try:
        # Create a temp file to work with pdfplumber
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file.read())
            temp_path = temp_file.name
        
        # Extract text from all pages
        text = []
        with pdfplumber.open(temp_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text.append(page_text)
        
        # Clean up temp file
        os.unlink(temp_path)
        
        return "\n".join(text)
    except Exception as e:
        raise ExtractionError(f"Failed to extract text from PDF: {str(e)}")


def extract_text_from_image(file: BinaryIO) -> str:
    """
    Extract text from an image using OCR.
    
    Args:
        file: Image file object
        
    Returns:
        str: Extracted text content
        
    Raises:
        ExtractionError: If OCR fails
    """
    if not OCR_SUPPORT:
        raise ExtractionError("OCR not supported. Please install pytesseract and Pillow packages.")
    
    try:
        # Load the image
        image = Image.open(io.BytesIO(file.read()))
        
        # Perform OCR
        text = pytesseract.image_to_string(image)
        
        return text
    except Exception as e:
        raise ExtractionError(f"Failed to extract text using OCR: {str(e)}")


def extract_text_from_docx(file: BinaryIO) -> str:
    """
    Extract text from a DOCX file.
    
    Args:
        file: DOCX file object
        
    Returns:
        str: Extracted text content
        
    Raises:
        ExtractionError: If text extraction fails
    """
    if not DOCX_SUPPORT:
        raise ExtractionError("DOCX extraction not supported. Please install python-docx package.")
    
    try:
        # Create a temp file to work with python-docx
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file.read())
            temp_path = temp_file.name
        
        # Extract text using python-docx
        doc = docx.Document(temp_path)
        paragraphs = [p.text for p in doc.paragraphs]
        
        # Clean up temp file
        os.unlink(temp_path)
        
        return "\n".join(paragraphs)
    except Exception as e:
        raise ExtractionError(f"Failed to extract text from DOCX: {str(e)}")


def extract_text_from_txt(file: BinaryIO) -> str:
    """
    Extract text from a plain text file.
    
    Args:
        file: Text file object
        
    Returns:
        str: Extracted text content
        
    Raises:
        ExtractionError: If text extraction fails
    """
    try:
        content = file.read()
        if isinstance(content, bytes):
            # Try common encodings
            for encoding in ['utf-8', 'latin-1', 'ascii']:
                try:
                    return content.decode(encoding)
                except UnicodeDecodeError:
                    continue
            
            # Fallback to a more lenient encoding
            return content.decode('utf-8', errors='replace')
        else:
            return content
    except Exception as e:
        raise ExtractionError(f"Failed to extract text from text file: {str(e)}")


def extract_text_from_file(file: BinaryIO) -> Tuple[str, str]:
    """
    Extract text content from a file based on its type.
    
    Args:
        file: File object to extract text from
        
    Returns:
        Tuple[str, str]: Tuple containing (file_type, extracted_text)
        
    Raises:
        UnsupportedFileTypeError: If file type is not supported
        ExtractionError: If text extraction fails
    """
    # Save current position
    current_pos = file.tell()
    
    try:
        # Identify file type
        file_type = identify_file_type(file)
        
        # Reset position
        file.seek(current_pos)
        
        # Extract text based on file type
        if file_type == 'pdf':
            text = extract_text_from_pdf(file)
        elif file_type == 'image':
            text = extract_text_from_image(file)
        elif file_type == 'docx':
            text = extract_text_from_docx(file)
        elif file_type == 'txt':
            text = extract_text_from_txt(file)
        else:
            raise UnsupportedFileTypeError(f"Extraction for {file_type} files is not supported")
        
        return file_type, text
    except (UnsupportedFileTypeError, ExtractionError) as e:
        # Re-raise the original exception
        raise
    except Exception as e:
        # Wrap other exceptions
        raise ExtractionError(f"Failed to extract text from file: {str(e)}")
    finally:
        # Attempt to reset file position
        try:
            file.seek(current_pos)
        except:
            pass  # If we can't reset, it's likely the file has been closed
