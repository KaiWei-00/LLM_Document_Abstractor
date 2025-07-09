# Project Planning: LLM_Document_Abstractor — Schema-Based Document Extraction API

## Purpose

LLM_Document_Abstractor is a **microservice API** that extracts structured data from documents based on a **schema provided by the client application**. This service allows external apps to upload files (PDF, image, DOCX, etc.) along with a data model. The API identifies the file type, extracts content, and uses LangGraph + LLM to map it to the target schema.

---

## How It Works

1. **App frontend**: Handles user input (file upload)
2. **App backend**: Sends `file + schema` to the LLM_Document_Abstractor API
3. **LLM_Document_Abstractor API**:
   - Identifies the file type
   - Parses content (PDF, OCR, etc.)
   - Uses LangGraph to extract and map data into the schema
4. **LLM_Document_Abstractor API response**: Returns extracted data in JSON format matching the schema

---

## Input Example

**POST** `/api/extract`

- `file`: uploaded document (PDF, DOCX, image, etc.)
- `schema`: JSON object with key-value pairs (string, number, date)

Example Schema:
```json
{
  "name": "string",
  "tax_id": "string",
  "total_income": "number"
}
```

---

## Output Example

```json
{
  "name": "John Tan",
  "tax_id": "TX-772199",
  "total_income": 92000
}
```

---

## Tech Stack

| Component         | Tech                                 |
|------------------|--------------------------------------|
| API Backend       | FastAPI or Express.js               |
| LangGraph Flow    | Python (LangGraph)                  |
| LLM Integration   | OpenAI / Claude (JSON output mode)  |
| File Parsing      | pdfplumber, Tesseract, python-docx  |
| Schema Mapping    | LLM-guided extraction               |
| Deployment        | Docker                              |

---

## Reusability

- Any app can define its own schema
- Any frontend can upload the file
- API is a universal document extractor with schema fitting

---

## Use Cases

- Tax form extraction
- Invoice field mapping
- Identity/KYC form parsing
- Custom field extraction per app

---

## Deliverables

- `/api/extract` endpoint
- LangGraph flow: file → text → extracted JSON
- Works out-of-the-box with any document + schema