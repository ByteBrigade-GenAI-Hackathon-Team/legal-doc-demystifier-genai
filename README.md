# Legal Document Demystifier

## Overview
The Legal Document Demystifier simplifies complex legal documents by transforming dense legal jargon and lengthy clauses into clear, understandable language tailored to different user roles. It proactively highlights risks, obligations, and hidden costs, and offers actionable insights to empower users to make informed decisions with confidence.

This project supports various document formats including PDFs, Word docs, images (via OCR), and plain text. Users can upload documents or paste text, specify their role (e.g., tenant, freelancer), and receive customized, easy-to-understand summaries along with risk warnings and practical next steps. Additionally, users can ask unlimited follow-up questions grounded in their document’s context.

---

## Features
- Multi-format document input: PDF, DOCX, images, and text
- OCR integration via Tesseract for image-based text extraction
- AI-powered simplification using Google Gemini language model
- Role-based tailored analysis highlighting key risks and obligations
- Interactive follow-up Q&A for continuous legal understanding
- Proactive highlighting of risks and actionable recommendations
- Secure handling of API keys and user information with environment variables

---

## Technologies Used

### Frontend
- React.js for dynamic user interface
- JavaScript, HTML5, CSS3 for responsive design

### Backend
- FastAPI for building high-performance API endpoints
- Python as the core programming language
- PyTesseract and Tesseract OCR for image text extraction
- pdfplumber for PDF text extraction
- python-docx for Word document processing
- Pillow for image processing
- Google Gemini API for natural language understanding and summarization
- python-dotenv for secure environment variable management

### Deployment & DevOps
- Google Cloud Platform (GCP) for hosting and scaling
- Google App Engine for app deployment
- Git and GitHub for source control and collaboration

---

## Setup & Installation

### Prerequisites
- Python 3.9+
- Node.js and npm
- Tesseract OCR installed and configured (ensure executable path is correctly set)
- Google Cloud SDK installed

### Installation Steps
1. Clone the repository
git clone https://github.com/yourusername/legal-doc-demystifier.git
cd legal-doc-demystifier/backend

2. Create and activate Python virtual environment
python -m venv venv
source venv/bin/activate # Unix/macOS
.\.venv\Scripts\activate # Windows

3. Install backend dependencies
pip install -r requirements.txt

4. Install frontend dependencies
cd ../frontend
npm install

5. Set Tesseract executable path in backend (`simplify_document.py`)
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'Your_tesseract_path_here'

6. Create `.env` file in backend directory with your Google Gemini API key:
GEMINI_API_KEY=your_api_key_here

7. Run backend server
uvicorn main:app --reload

8. Run frontend server
npm start

---

## Usage
- Access frontend UI and input or upload your legal document.
- Specify your role or area of concern to tailor the analysis.
- Receive a simplified summary, highlighted risks, and actionable next steps.
- Ask follow-up questions about your document to clarify any doubts.
- Use insights to make informed, confident decisions.

---

## Disclaimer
This tool is for educational purposes only and does not constitute legal advice. For official advice or decisions, consult a qualified legal professional.

---

## Contact
For queries or collaboration, contact [nilotpalarya65@gmail.com].

---

