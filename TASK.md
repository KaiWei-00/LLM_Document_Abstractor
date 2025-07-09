# Task List: LLM_Document_Abstractor — Microservice for Schema-Based Document Extraction

---

## 🧱 API Setup

- [x] Create `/api/extract` endpoint
- [x] Accept `multipart/form-data`: file + schema
- [x] Validate file and schema presence

---

## 🧠 LangGraph Flow

- [x] Node: Identify file type (pdf, image, docx)
- [x] Node: Parse content accordingly
    - PDF → `pdfplumber`
    - Image → `Tesseract`
    - DOCX → `python-docx`
- [x] Node: Call LLM with parsed text + schema
- [x] Node: Validate output JSON matches schema
- [x] Node: Return extracted result

---

## 🧪 LLM Integration

- [x] Use OpenAI / Claude with JSON schema prompt
- [x] Force output to match types (e.g., string, number)
- [x] Handle missing or partial data gracefully

---

## 🧰 Utility Logic

- [x] File type detection logic
- [x] Text pre-cleaning and truncation
- [x] Error handling: bad file, bad schema, LLM failure

---

## 🧪 Testing

- [ ] Test: extract from PDF to schema
- [ ] Test: extract from image (OCR) to schema
- [ ] Test: extract from DOCX to schema
- [ ] Test: bad/malformed schema
- [ ] Test: missing fields fallback

---

## 🚀 Deployment

- [ ] Dockerize FastAPI + LangGraph app
- [ ] Enable logging for all extraction jobs
- [ ] Deploy to cloud (Render, Railway, etc.)

---

## ✅ Completed on 2025-07-09

- API Setup - Complete with FastAPI routes
- LangGraph Flow - Complete with extraction nodes and flow implementation
- LLM Integration - Complete with OpenAI integration and JSON handling
- Utility Logic - Complete with file processing and error handling