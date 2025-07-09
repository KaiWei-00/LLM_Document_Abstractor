import os
from fastapi import UploadFile, HTTPException
from typing import Literal, Optional

from app.parsers.pdf_parser import extract_text_from_pdf
from app.parsers.image_parser import extract_text_from_image
from app.parsers.docx_parser import extract_text_from_docx

# Define supported file types
FileType = Literal["pdf", "image", "docx", "unknown"]


def identify_file_type(file: UploadFile) -> FileType:
    """
    Identify the type of the uploaded file based on its extension and content.
    
    Args:
        file: The uploaded file
    
    Returns:
        FileType: The identified file type ("pdf", "image", "docx", or "unknown")
    """
    # Extract file extension
    _, extension = os.path.splitext(file.filename)
    extension = extension.lower()
    
    # Check extension
    if extension == ".pdf":
        return "pdf"
    elif extension in [".jpg", ".jpeg", ".png", ".tiff", ".bmp", ".gif"]:
        return "image"
    elif extension == ".docx":
        return "docx"
    else:
        # Could implement content-based detection for ambiguous cases
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {extension}. Please upload a PDF, image, or DOCX file."
        )


async def process_file(file: UploadFile, file_type: FileType) -> str:
    """
    Process the file based on its type and extract text content.
    
    Args:
        file: The uploaded file
        file_type: The identified file type
    
    Returns:
        str: Extracted text from the file
    """
    try:
        if file_type == "pdf":
            return await extract_text_from_pdf(file)
        elif file_type == "image":
            return await extract_text_from_image(file)
        elif file_type == "docx":
            return await extract_text_from_docx(file)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing {file_type} file: {str(e)}"
        )
