from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
import textract
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Get your API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

# Configure the Generative AI model
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('models/gemini-2.5-pro')  # Using gemini-pro as discussed

router = APIRouter()

class DocumentRequest(BaseModel):
    document_text: str
    user_role_goal: str = "general user"  # Default for our USP

@router.post("/simplify")
async def simplify_document(request: DocumentRequest):
    """
    Receives a legal document and simplifies it using Generative AI.
    Also identifies risks and actionable insights based on user_role_goal.
    """
    if not request.document_text:
        raise HTTPException(status_code=400, detail="Document text cannot be empty.")

    # --- Prompt Engineering (Improved USP Prompt) ---
    prompt_template = f"""
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
    # --- End Prompt Engineering ---

    try:
        # Generate content with a low temperature for factual accuracy
        response = model.generate_content(
            prompt_template,
            generation_config=genai.types.GenerationConfig(temperature=0.1)
        )
        simplified_content = response.text
        return {"simplified_document": simplified_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")


@router.post("/simplify-file")
async def simplify_document_file(
    user_role_goal: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Receive a document file, extract text, and simplify using Gemini.
    """
    try:
        # Read file bytes
        file_bytes = await file.read()

        # Save file temporarily for textract to process
        with open(file.filename, "wb") as f:
            f.write(file_bytes)

        # Extract text from the file
        extracted_text = textract.process(file.filename).decode('utf-8')

        # Remove the temporary file
        os.remove(file.filename)

    except Exception as e:
        return JSONResponse(status_code=400, content={"detail": f"File processing error: {str(e)}"})

    # --- Compose prompt ---
    prompt_template = f"""
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
        # Call Gemini API with the prompt
        response = model.generate_content(
            prompt_template,
            generation_config=genai.types.GenerationConfig(temperature=0.1)
        )
        simplified_content = response.text
        return {"simplified_document": simplified_content}

    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"AI generation failed: {str(e)}"})
