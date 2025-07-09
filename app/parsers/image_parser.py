import io
from PIL import Image
import pytesseract
from fastapi import UploadFile


async def extract_text_from_image(file: UploadFile) -> str:
    """
    Extract text from an image file using OCR (Optical Character Recognition).
    
    Args:
        file: Image file uploaded by the user
    
    Returns:
        str: Extracted text content
    
    Raises:
        Exception: If there's an error during image processing
    """
    try:
        # Read the file content
        content = await file.read()
        
        # Open the image using PIL
        with Image.open(io.BytesIO(content)) as img:
            # Use pytesseract for OCR
            text = pytesseract.image_to_string(img)
            
            # Clean up the text
            text = text.strip()
        
        # Reset file pointer for potential later use
        await file.seek(0)
        
        return text
    except Exception as e:
        # Re-raise with more context
        raise Exception(f"Failed to extract text from image: {str(e)}")
