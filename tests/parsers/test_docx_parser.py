import pytest
from fastapi import UploadFile
from unittest.mock import AsyncMock, MagicMock, patch
import io

from app.parsers.docx_parser import extract_text_from_docx


@pytest.fixture
def mock_docx_file():
    """Create a mock DOCX file for testing."""
    # Create a mock UploadFile object
    file_mock = AsyncMock(spec=UploadFile)
    file_mock.filename = "test.docx"
    
    # Mock the read and seek methods
    file_mock.read.return_value = b"mock docx content"
    file_mock.seek.return_value = None
    
    return file_mock


@patch('docx.Document')
async def test_extract_text_from_docx_success(mock_document, mock_docx_file):
    """Test successful text extraction from DOCX."""
    # Create mock Document with paragraphs and tables
    mock_doc = MagicMock()
    
    # Mock paragraphs
    paragraph1 = MagicMock()
    paragraph1.text = "This is paragraph 1."
    paragraph2 = MagicMock()
    paragraph2.text = "This is paragraph 2."
    mock_doc.paragraphs = [paragraph1, paragraph2]
    
    # Mock tables
    mock_cell1 = MagicMock()
    mock_cell1.text = "Cell 1"
    mock_cell2 = MagicMock()
    mock_cell2.text = "Cell 2"
    
    mock_row = MagicMock()
    mock_row.cells = [mock_cell1, mock_cell2]
    
    mock_table = MagicMock()
    mock_table.rows = [mock_row]
    
    mock_doc.tables = [mock_table]
    
    # Set up the mock Document constructor
    mock_document.return_value = mock_doc
    
    # Call the function
    result = await extract_text_from_docx(mock_docx_file)
    
    # Verify expectations
    mock_docx_file.read.assert_called_once()
    mock_docx_file.seek.assert_called_once_with(0)
    mock_document.assert_called_once_with(io.BytesIO(b"mock docx content"))
    
    # Check that paragraphs and table content are included
    assert "This is paragraph 1." in result
    assert "This is paragraph 2." in result
    assert "Cell 1" in result
    assert "Cell 2" in result


@patch('docx.Document')
async def test_extract_text_from_docx_empty_document(mock_document, mock_docx_file):
    """Test extraction from empty DOCX document."""
    # Create mock empty Document
    mock_doc = MagicMock()
    mock_doc.paragraphs = []
    mock_doc.tables = []
    
    # Set up the mock Document constructor
    mock_document.return_value = mock_doc
    
    # Call the function
    result = await extract_text_from_docx(mock_docx_file)
    
    # Verify result is an empty string after stripping
    assert result == ""


@patch('docx.Document')
async def test_extract_text_from_docx_exception(mock_document, mock_docx_file):
    """Test handling of exception during DOCX extraction."""
    # Make Document constructor raise an exception
    mock_document.side_effect = Exception("DOCX processing error")
    
    # Check that the exception is properly propagated
    with pytest.raises(Exception) as excinfo:
        await extract_text_from_docx(mock_docx_file)
    
    assert "Failed to extract text from DOCX" in str(excinfo.value)
    assert "DOCX processing error" in str(excinfo.value)
