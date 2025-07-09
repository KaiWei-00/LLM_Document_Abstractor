import pytest
from fastapi import UploadFile
from unittest.mock import AsyncMock, MagicMock, patch
import io

from app.parsers.image_parser import extract_text_from_image


@pytest.fixture
def mock_image_file():
    """Create a mock image file for testing."""
    # Create a mock UploadFile object
    file_mock = AsyncMock(spec=UploadFile)
    file_mock.filename = "test.jpg"
    
    # Mock the read and seek methods
    file_mock.read.return_value = b"mock image content"
    file_mock.seek.return_value = None
    
    return file_mock


@patch('PIL.Image.open')
@patch('pytesseract.image_to_string')
async def test_extract_text_from_image_success(mock_ocr, mock_image_open, mock_image_file):
    """Test successful text extraction from image using OCR."""
    # Set up the mocks
    mock_image = MagicMock()
    mock_image.__enter__.return_value = mock_image
    mock_image_open.return_value = mock_image
    
    # Set OCR return value
    mock_ocr.return_value = "Text extracted from image using OCR"
    
    # Call the function
    result = await extract_text_from_image(mock_image_file)
    
    # Verify expectations
    mock_image_file.read.assert_called_once()
    mock_image_file.seek.assert_called_once_with(0)
    mock_image_open.assert_called_once()
    mock_ocr.assert_called_once_with(mock_image)
    
    assert result == "Text extracted from image using OCR"


@patch('PIL.Image.open')
@patch('pytesseract.image_to_string')
async def test_extract_text_from_image_empty_result(mock_ocr, mock_image_open, mock_image_file):
    """Test handling of empty OCR result."""
    # Set up the mocks
    mock_image = MagicMock()
    mock_image.__enter__.return_value = mock_image
    mock_image_open.return_value = mock_image
    
    # Set OCR to return whitespace
    mock_ocr.return_value = "   \n  \t  "
    
    # Call the function
    result = await extract_text_from_image(mock_image_file)
    
    # Verify result is an empty string after stripping
    assert result == ""


@patch('PIL.Image.open')
async def test_extract_text_from_image_exception(mock_image_open, mock_image_file):
    """Test handling of exception during image processing."""
    # Make PIL.Image.open raise an exception
    mock_image_open.side_effect = Exception("Image processing error")
    
    # Check that the exception is properly propagated
    with pytest.raises(Exception) as excinfo:
        await extract_text_from_image(mock_image_file)
    
    assert "Failed to extract text from image" in str(excinfo.value)
    assert "Image processing error" in str(excinfo.value)
