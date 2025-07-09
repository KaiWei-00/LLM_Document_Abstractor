import pytest
from fastapi import UploadFile, HTTPException
from unittest.mock import AsyncMock, patch, MagicMock

from app.core.file_processor import identify_file_type, process_file


@pytest.fixture
def mock_pdf_file():
    """Create a mock PDF file for testing."""
    file_mock = AsyncMock(spec=UploadFile)
    file_mock.filename = "test.pdf"
    return file_mock


@pytest.fixture
def mock_image_file():
    """Create a mock image file for testing."""
    file_mock = AsyncMock(spec=UploadFile)
    file_mock.filename = "test.jpg"
    return file_mock


@pytest.fixture
def mock_docx_file():
    """Create a mock DOCX file for testing."""
    file_mock = AsyncMock(spec=UploadFile)
    file_mock.filename = "test.docx"
    return file_mock


@pytest.fixture
def mock_unsupported_file():
    """Create a mock unsupported file for testing."""
    file_mock = AsyncMock(spec=UploadFile)
    file_mock.filename = "test.txt"
    return file_mock


def test_identify_file_type_pdf(mock_pdf_file):
    """Test file type identification for PDF files."""
    file_type = identify_file_type(mock_pdf_file)
    assert file_type == "pdf"


def test_identify_file_type_image(mock_image_file):
    """Test file type identification for image files."""
    file_type = identify_file_type(mock_image_file)
    assert file_type == "image"
    
    # Test other image extensions
    for ext in [".jpeg", ".png", ".tiff", ".bmp", ".gif"]:
        file = AsyncMock(spec=UploadFile)
        file.filename = f"test{ext}"
        assert identify_file_type(file) == "image"


def test_identify_file_type_docx(mock_docx_file):
    """Test file type identification for DOCX files."""
    file_type = identify_file_type(mock_docx_file)
    assert file_type == "docx"


def test_identify_file_type_unsupported(mock_unsupported_file):
    """Test file type identification for unsupported file types."""
    with pytest.raises(HTTPException) as excinfo:
        identify_file_type(mock_unsupported_file)
    
    assert excinfo.value.status_code == 400
    assert "Unsupported file type" in str(excinfo.value.detail)


@patch('app.parsers.pdf_parser.extract_text_from_pdf')
async def test_process_file_pdf(mock_pdf_parser, mock_pdf_file):
    """Test file processing for PDF files."""
    mock_pdf_parser.return_value = "Extracted text from PDF"
    
    result = await process_file(mock_pdf_file, "pdf")
    
    mock_pdf_parser.assert_called_once_with(mock_pdf_file)
    assert result == "Extracted text from PDF"


@patch('app.parsers.image_parser.extract_text_from_image')
async def test_process_file_image(mock_image_parser, mock_image_file):
    """Test file processing for image files."""
    mock_image_parser.return_value = "Extracted text from image using OCR"
    
    result = await process_file(mock_image_file, "image")
    
    mock_image_parser.assert_called_once_with(mock_image_file)
    assert result == "Extracted text from image using OCR"


@patch('app.parsers.docx_parser.extract_text_from_docx')
async def test_process_file_docx(mock_docx_parser, mock_docx_file):
    """Test file processing for DOCX files."""
    mock_docx_parser.return_value = "Extracted text from DOCX"
    
    result = await process_file(mock_docx_file, "docx")
    
    mock_docx_parser.assert_called_once_with(mock_docx_file)
    assert result == "Extracted text from DOCX"


async def test_process_file_unsupported():
    """Test processing of unsupported file type."""
    file = AsyncMock(spec=UploadFile)
    
    with pytest.raises(HTTPException) as excinfo:
        await process_file(file, "unknown")
    
    assert excinfo.value.status_code == 500
    assert "Unsupported file type" in str(excinfo.value.detail)


@patch('app.parsers.pdf_parser.extract_text_from_pdf')
async def test_process_file_exception(mock_pdf_parser, mock_pdf_file):
    """Test handling of exception during file processing."""
    # Make parser raise an exception
    mock_pdf_parser.side_effect = Exception("Parsing error")
    
    with pytest.raises(HTTPException) as excinfo:
        await process_file(mock_pdf_file, "pdf")
    
    assert excinfo.value.status_code == 500
    assert "Error processing pdf file" in str(excinfo.value.detail)
    assert "Parsing error" in str(excinfo.value.detail)
