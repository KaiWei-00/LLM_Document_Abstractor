import pytest
from fastapi import UploadFile
from unittest.mock import AsyncMock, MagicMock, patch
import io

from app.parsers.pdf_parser import extract_text_from_pdf


@pytest.fixture
def mock_pdf_file():
    """Create a mock PDF file for testing."""
    # Create a mock UploadFile object
    file_mock = AsyncMock(spec=UploadFile)
    file_mock.filename = "test.pdf"
    
    # Mock the read and seek methods
    file_mock.read.return_value = b"mock pdf content"
    file_mock.seek.return_value = None
    
    return file_mock


@patch('pdfplumber.open')
async def test_extract_text_from_pdf_success(mock_pdf_open, mock_pdf_file):
    """Test successful text extraction from PDF."""
    # Set up the mock PDF object and pages
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "This is test content from the PDF."
    
    mock_pdf = MagicMock()
    mock_pdf.pages = [mock_page]
    mock_pdf.__enter__.return_value = mock_pdf
    
    mock_pdf_open.return_value = mock_pdf
    
    # Call the function
    result = await extract_text_from_pdf(mock_pdf_file)
    
    # Verify expectations
    mock_pdf_file.read.assert_called_once()
    mock_pdf_file.seek.assert_called_once_with(0)
    mock_pdf_open.assert_called_once()
    mock_page.extract_text.assert_called_once()
    
    assert "This is test content from the PDF." in result
    assert result.strip() == "This is test content from the PDF."


@patch('pdfplumber.open')
async def test_extract_text_from_pdf_empty_page(mock_pdf_open, mock_pdf_file):
    """Test extraction from PDF with empty page."""
    # Set up the mock PDF object with page that returns None (empty)
    mock_page = MagicMock()
    mock_page.extract_text.return_value = None
    
    mock_pdf = MagicMock()
    mock_pdf.pages = [mock_page]
    mock_pdf.__enter__.return_value = mock_pdf
    
    mock_pdf_open.return_value = mock_pdf
    
    # Call the function
    result = await extract_text_from_pdf(mock_pdf_file)
    
    # Verify result is an empty string after stripping
    assert result == ""


@patch('pdfplumber.open')
async def test_extract_text_from_pdf_exception(mock_pdf_open, mock_pdf_file):
    """Test handling of exception during PDF extraction."""
    # Make pdfplumber.open raise an exception
    mock_pdf_open.side_effect = Exception("PDF processing error")
    
    # Check that the exception is properly propagated
    with pytest.raises(Exception) as excinfo:
        await extract_text_from_pdf(mock_pdf_file)
    
    assert "Failed to extract text from PDF" in str(excinfo.value)
    assert "PDF processing error" in str(excinfo.value)
