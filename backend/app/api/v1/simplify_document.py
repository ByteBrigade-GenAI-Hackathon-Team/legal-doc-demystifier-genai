from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import io
from PIL import Image
import pytesseract
import google.generativeai as genai
import pdfplumber
from docx import Document

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-2.5-pro")

router = APIRouter()

# Keep context for follow-up queries
document_context_store = {}

class DocumentRequest(BaseModel):
    document_text: str
    user_role_goal: str = "general user"

class QueryRequest(BaseModel):
    query: str
    doc_id: str

def highlight_risks(text: str) -> str:
    """
    Simple heuristic: mark 'risk', 'penalty', 'termination', 'deadline', 'must', 'shall'
    """
    risk_words = ["risk", "penalty", "termination", "deadline", "must", "shall", "obligation"]
    for word in risk_words:
        text = text.replace(
            word, f"<span style='color:red;font-weight:bold'>{word}</span>"
        ).replace(
            word.capitalize(), f"<span style='color:red;font-weight:bold'>{word.capitalize()}</span>"
        )
    return text

@router.post("/simplify")
async def simplify_document(request: DocumentRequest):
    if not request.document_text.strip():
        raise HTTPException(status_code=400, detail="Document text cannot be empty.")

    doc_id = str(hash(request.document_text + request.user_role_goal))

    prompt = f"""
You are a legal AI assistant.
Simplify the following document for the role: {request.user_role_goal}.
Highlight important risks, obligations, deadlines.

Document:
{request.document_text}
"""

    try:
        response = model.generate_content(prompt, generation_config=genai.types.GenerationConfig(temperature=0.2))
        simplified = highlight_risks(response.text)
        document_context_store[doc_id] = request.document_text
        return {"doc_id": doc_id, "simplified_document": simplified}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

@router.post("/simplify-file")
async def simplify_document_file(user_role_goal: str = Form(...), file: UploadFile = File(...)):
    try:
        content_type = file.content_type
        extracted_text = ""
        file_bytes = await file.read()

        if content_type.startswith("image/"):
            image = Image.open(io.BytesIO(file_bytes))
            extracted_text = pytesseract.image_to_string(image)
        elif content_type == "application/pdf":
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                extracted_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        elif content_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"] or file.filename.endswith(".docx"):
            doc = Document(io.BytesIO(file_bytes))
            extracted_text = "\n".join([para.text for para in doc.paragraphs])
        elif content_type.startswith("text/") or file.filename.endswith(".txt"):
            extracted_text = file_bytes.decode("utf-8", errors="ignore")
        else:
            extracted_text = "Unsupported file type. Please upload an image, PDF, Word (.docx), or text file."

    except Exception as e:
        return JSONResponse(status_code=400, content={"detail": f"File processing error: {str(e)}"})

    doc_id = str(hash(extracted_text + user_role_goal))

    prompt = f"""
You are a legal AI assistant.
Simplify the following document for the role: {user_role_goal}.
Highlight important risks, obligations, deadlines.

Document:
{extracted_text}
"""
    try:
        response = model.generate_content(prompt, generation_config=genai.types.GenerationConfig(temperature=0.2))
        simplified = highlight_risks(response.text)
        document_context_store[doc_id] = extracted_text
        return {"doc_id": doc_id, "simplified_document": simplified}
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"AI generation failed: {str(e)}"})

@router.post("/query")
async def followup_query(request: QueryRequest):
    doc_text = document_context_store.get(request.doc_id)
    if not doc_text:
        return {"answer": "No context found for this document. Please upload again."}

    prompt = f"""
Answer the following query only using the given document context.
If the answer is not in the document, respond: "This information is not mentioned in the document."

Document:
{doc_text}

User query: {request.query}
"""

    try:
        response = model.generate_content(prompt, generation_config=genai.types.GenerationConfig(temperature=0.2))
        answer = highlight_risks(response.text)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")
