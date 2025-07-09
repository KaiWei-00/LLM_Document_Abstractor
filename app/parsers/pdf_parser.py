import io
import pdfplumber
from fastapi import UploadFile


async def extract_text_from_pdf(file: UploadFile) -> str:
    """
    Extract text content from a PDF file.
    
    Args:
        file: PDF file uploaded by the user
    
    Returns:
        str: Extracted text content
    
    Raises:
        Exception: If there's an error during PDF processing
    """
    try:
        # Read the file content
        content = await file.read()
        
        # Use a file-like object for pdfplumber
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            # Extract text from each page and join
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n\n"
            
            # Clean up the text
            text = text.strip()
            
        # Reset file pointer for potential later use
        await file.seek(0)
        
        return text
    except Exception as e:
        # Re-raise with more context
        raise Exception(f"Failed to extract text from PDF: {str(e)}")
