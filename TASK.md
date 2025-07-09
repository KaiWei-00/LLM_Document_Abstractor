# Task List: LLM_Document_Abstractor — Microservice for Schema-Based Document Extraction

---

## 🧱 API Setup

- [ ] Create `/api/extract` endpoint
- [ ] Accept `multipart/form-data`: file + schema
- [ ] Validate file and schema presence

---

## 🧠 LangGraph Flow

- [ ] Node: Identify file type (pdf, image, docx)
- [ ] Node: Parse content accordingly
    - PDF → `pdfplumber`
    - Image → `Tesseract`
    - DOCX → `python-docx`
- [ ] Node: Call LLM with parsed text + schema
- [ ] Node: Validate output JSON matches schema
- [ ] Node: Return extracted result

---

## 🧪 LLM Integration

- [ ] Use OpenAI / Claude with JSON schema prompt
- [ ] Force output to match types (e.g., string, number)
- [ ] Handle missing or partial data gracefully

---

## 🧰 Utility Logic

- [ ] File type detection logic
- [ ] Text pre-cleaning and truncation
- [ ] Error handling: bad file, bad schema, LLM failure

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