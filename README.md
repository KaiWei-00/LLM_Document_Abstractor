# LLM_Document_Abstractor

A microservice API that extracts structured data from documents based on a schema provided by the client application.

## Overview

This service allows external apps to upload files (PDF, image, DOCX, etc.) along with a data model. The API identifies the file type, extracts content, and uses LangGraph + LLM to map it to the target schema.

## How It Works

1. **App frontend**: Handles user input (file upload)
2. **App backend**: Sends `file + schema` to the LLM_Document_Abstractor API
3. **LLM_Document_Abstractor API**:
   - Identifies the file type
   - Parses content (PDF, OCR, etc.)
   - Uses LangGraph to extract and map data into the schema
4. **LLM_Document_Abstractor API response**: Returns extracted data in JSON format matching the schema

## Getting Started

### Prerequisites

- Python 3.9+
- OpenAI API key or other LLM provider API key

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/LLM_Document_Abstractor.git
   cd LLM_Document_Abstractor
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Create a `.env` file in the root directory
   - Add your API key: `OPENAI_API_KEY=your_api_key_here`

### Running the API

```
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## API Usage

### Extract Endpoint

**POST** `/api/extract`

#### Request

Content-Type: `multipart/form-data`

- `file`: File to extract data from (PDF, DOCX, image, etc.)
- `schema`: JSON object with key-value pairs defining the expected output structure

Example schema:
```json
{
  "name": "string",
  "tax_id": "string",
  "total_income": "number"
}
```

#### Response

```json
{
  "name": "John Tan",
  "tax_id": "TX-772199",
  "total_income": 92000
}
```

## Development

- `/app`: Core application code
- `/app/api`: API routes
- `/app/core`: Core functionality
- `/app/langflow`: LangGraph flow implementation
- `/app/parsers`: File parsing utilities
- `/tests`: Unit and integration tests
