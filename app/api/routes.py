from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import json
from typing import Dict, Any

from app.core.file_processor import identify_file_type, process_file
from app.schemas.validation import validate_schema
from app.langflow.extraction_flow import run_extraction_flow

router = APIRouter()


@router.post("/extract")
async def extract_data(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    schema: str = Form(...),
):
    """
    Extract structured data from a document based on the provided schema.
    
    Args:
        file: The document file (PDF, image, DOCX, etc.)
        schema: JSON string defining the data schema to extract
    
    Returns:
        JSON response with extracted data matching the schema
    """
    try:
        # Parse and validate schema
        try:
            schema_dict = json.loads(schema)
            validate_schema(schema_dict)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400, detail="Invalid schema format: not a valid JSON"
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Check file size (limit to 10MB)
        file_size = 0
        file_content = await file.read()
        file_size = len(file_content)
        if file_size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=400, detail="File size exceeds the 10MB limit"
            )
        
        # Reset file pointer for later processing
        await file.seek(0)
        
        # Identify file type
        file_type = identify_file_type(file)
        
        # Process file based on its type
        processed_text = await process_file(file, file_type)
        
        # Run extraction flow
        result = run_extraction_flow(processed_text, schema_dict)
        
        return JSONResponse(
            content=result,
            status_code=200
        )
    
    except HTTPException:
        raise
    except Exception as e:
        # Log the error
        print(f"Error processing request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing the request: {str(e)}"
        )
