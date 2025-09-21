# simplify_document.py
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import io
import hashlib
import re
from PIL import Image
import pytesseract
import google.generativeai as genai

# NEW: For PDF text extraction
from PyPDF2 import PdfReader

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-2.5-pro")

router = APIRouter()

# Keep context for follow-up queries (in-memory)
# NOTE: for production/stability use Redis or a DB so context survives restarts.
document_context_store = {}


class DocumentRequest(BaseModel):
    document_text: str
    user_role_goal: str = "general user"


class QueryRequest(BaseModel):
    query: str
    doc_id: str


def highlight_risks(text: str) -> str:
    """
    Highlight risky/legal words using word-boundary regex, case-insensitive.
    Skip highlighting if text already contains <span (to avoid nested spans).
    """
    if not text:
        return text

    if "<span" in text:
        # already highlighted or contains HTML — avoid double-wrapping
        return text

    risk_words = ["risk", "penalty", "termination", "deadline", "must", "shall", "obligation"]
    pattern = r"\b(" + "|".join(re.escape(w) for w in risk_words) + r")\b"

    def repl(m):
        return f"<span style='color:red;font-weight:bold'>{m.group(0)}</span>"

    return re.sub(pattern, repl, text, flags=re.IGNORECASE)


def generate_doc_id(text: str, role: str) -> str:
    """Generate a stable SHA256-based document ID."""
    combined = (text or "").strip() + "|" + (role or "")
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()


@router.post("/simplify")
async def simplify_document(request: DocumentRequest):
    if not request.document_text or not request.document_text.strip():
        raise HTTPException(status_code=400, detail="Document text cannot be empty.")

    doc_id = generate_doc_id(request.document_text, request.user_role_goal)
    print(f"[simplify] doc_id={doc_id} role={request.user_role_goal} len={len(request.document_text)}")

    prompt = f"""
Persona:
You are a highly accurate, unbiased legal AI assistant specialized in explaining legal documents to laypersons. Your goal is clarity, usefulness, and practical advice tailored to the user's role.

Task:
1. Summarize the legal document in simple, non-legal language.
2. List each key clause, explaining the plain meaning and its relevance.
3. Identify risks, obligations, or opportunities, focusing on issues relevant to the user's stated role/goal: "{request.user_role_goal}".
4. Suggest practical, actionable steps or questions without giving legal advice.

Context:
- The user's role is: "{request.user_role_goal}".
- The purpose is educational/informative only.

Format:
Simplified Summary:
[Concise summary paragraph]

Key Clauses & Meanings:
- [Bulleted list. For each clause, explain simply and tie it to risks or actions.]

Risks & Actionable Insights:
- [Bulleted list of specific potential risks and what the user could do next, relevant to their role.]

Overall Recommendations:
[Short paragraph with useful, non-advisory tips.]

IMPORTANT DISCLAIMER: Output does not constitute legal advice. Consult a qualified professional for legal decisions.

Document:
{request.document_text}
"""
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.2)
        )
        simplified = highlight_risks(response.text)
        document_context_store[doc_id] = request.document_text
        return {"doc_id": doc_id, "simplified_document": simplified}
    except Exception as e:
        print(f"[simplify] ERROR doc_id={doc_id} error={e}")
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")


@router.post("/simplify-file")
async def simplify_document_file(user_role_goal: str = Form(...), file: UploadFile = File(...)):
    try:
        content_type = file.content_type or ""
        extracted_text = ""

        if content_type.startswith("image/"):
            # OCR path
            image_bytes = await file.read()
            image = Image.open(io.BytesIO(image_bytes))
            extracted_text = pytesseract.image_to_string(image)
        elif file.filename.lower().endswith(".pdf") or content_type == "application/pdf":
            # PDF extraction path
            pdf_bytes = await file.read()
            pdf_stream = io.BytesIO(pdf_bytes)
            reader = PdfReader(pdf_stream)
            for page in reader.pages:
                extracted_text += page.extract_text() or ""

            # Print to verify extracted text from PDF
        else:
            # treat as text file
            extracted_text = (await file.read()).decode("utf-8", errors="ignore")

        if not extracted_text.strip():
            return JSONResponse(status_code=400, content={"detail": "No text could be extracted from the file."})
    except Exception as e:
        print(f"[simplify-file] File processing error: {e}")
        return JSONResponse(status_code=400, content={"detail": f"File processing error: {str(e)}"})

    doc_id = generate_doc_id(extracted_text, user_role_goal)

    prompt = f"""
Persona:
You are a highly accurate, unbiased legal AI assistant specialized in explaining legal documents to laypersons. Your goal is clarity, usefulness, and practical advice tailored to the user's role.

Task:
1. Summarize the legal document in simple, non-legal language.
2. List each key clause, explaining the plain meaning and its relevance.
3. Identify risks, obligations, or opportunities, focusing on issues relevant to the user's stated role/goal: "{user_role_goal}".
4. Suggest practical, actionable steps or questions without giving legal advice.

Context:
- The user's role is: "{user_role_goal}".
- The purpose is educational/informative only.

Format:
Simplified Summary:
[Concise summary paragraph]

Key Clauses & Meanings:
- [Bulleted list. For each clause, explain simply and tie it to risks or actions.]

Risks & Actionable Insights:
- [Bulleted list of specific potential risks and what the user could do next, relevant to their role.]

Overall Recommendations:
[Short paragraph with useful, non-advisory tips.]

IMPORTANT DISCLAIMER: Output does not constitute legal advice. Consult a qualified professional for legal decisions.

Document:
{extracted_text}
"""
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.2)
        )
        simplified = highlight_risks(response.text)
        document_context_store[doc_id] = extracted_text
        return {"doc_id": doc_id, "simplified_document": simplified}
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"AI generation failed: {str(e)}"})


@router.post("/query")
async def followup_query(request: Request, query: str = None, doc_id: str = None):
    """
    Robust follow-up endpoint:
     - accepts JSON body {"query": "...", "doc_id": "..."}
     - accepts form-data fields "query" and "doc_id" (common when frontend uses FormData)
     - accepts query params ?query=...&doc_id=...
     - recognizes alternative keys: question, q, docId, document_id, id
    """
    data = {}
    # try parse JSON
    try:
        data = await request.json()
        source = "json"
    except Exception:
        # fallback to form
        try:
            form = await request.form()
            data = dict(form)
            source = "form"
        except Exception:
            data = {}
            source = "params"

    # allow several key name variants
    q = data.get("query") or data.get("question") or data.get("q") or query
    did = data.get("doc_id") or data.get("docId") or data.get("document_id") or data.get("id") or doc_id

    print(f"[query] source={source} received query={q!r} doc_id={did!r}")

    if not did:
        raise HTTPException(status_code=400, detail="doc_id is required (as JSON body, form field, or query param).")

    doc_text = document_context_store.get(did)
    if not doc_text:
        print(f"[query] NO CONTEXT for doc_id={did}. available_keys_count={len(document_context_store)}")
        return {"answer": "No context found for this document. Please upload again."}

    prompt = f"""
Answer the following query only using the given document context.
If the answer is not in the document, respond: "This information is not mentioned in the document."

Document:
{doc_text}

User query: {q}
"""

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.2)
        )
        answer = highlight_risks(response.text)
        print(f"[query] doc_id={did} answer_len={len(answer)}")
        return {"answer": answer}
    except Exception as e:
        print(f"[query] ERROR doc_id={did} error={e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")
