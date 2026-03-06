# Medical Document Intelligence Backend

FastAPI backend for extracting insights from medical PDFs (blood reports, prescriptions, MRI summaries, discharge summaries). Built for internship technical task.

## Overview
- **Part 1**: Upload PDF → Extract text (pdfplumber + OCR fallback) → LLM analysis (OpenAI) or general fallback → 5 bullet points + tags (conditions, deficiencies, medicines, etc.).
- **Part 2**: Multi-PDF upload → Per-file analysis → Aggregate tags/counts → Download PDF summary report (ReportLab).
- **General Support**: Works on any blood report (Dr. Lal, Sterling, Thyrocare) – scans for B12, HbA1c, Cholesterol, etc., flags abnormals vs ref.

## Tech Stack
- FastAPI (API framework)
- pdfplumber + PyPDF2 (PDF extraction/tables)
- pytesseract (OCR fallback – optional)
- OpenAI GPT-3.5 (LLM analysis – fallback if no key)
- ReportLab (PDF generation for Part 2)
- Python 3.12+

## Setup
1. **Clone Repo**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/medical-doc-intel-backend.git
   cd medical-doc-intel-backend

## Visual reference 
![Figure 1](https://github.com/Hackerette0/medical-doc-intel-backend/blob/main/images/backendone.png) 
*Screenshot Reference: Backend testing input*

![Figure 2](https://github.com/Hackerette0/medical-doc-intel-backend/blob/main/images/backendtwo.png) 
*Screenshot Reference: Backend testing output*
