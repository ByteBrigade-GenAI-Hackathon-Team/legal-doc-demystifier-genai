from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Import the Google Generative AI SDK
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Get your API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

# Configure the Generative AI model
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro') # Using gemini-pro as discussed

router = APIRouter()

class DocumentRequest(BaseModel):
    document_text: str
    user_role_goal: str = "general user" # Default for our USP

@router.post("/simplify")
async def simplify_document(request: DocumentRequest):
    """
    Receives a legal document and simplifies it using Generative AI.
    Also identifies risks and actionable insights based on user_role_goal.
    """
    if not request.document_text:
        raise HTTPException(status_code=400, detail="Document text cannot be empty.")

    # --- Prompt Engineering (Your USP Integration) ---
    prompt_template = f"""
    You are an AI assistant specializing in simplifying complex legal documents for a layperson. Your primary goal is to make legal information understandable and actionable, not to provide legal advice.

    The user's role/goal is: {request.user_role_goal}.

    Your output must be easy to understand, using simple, non-legal language. Break down the text into key points or clauses. For each key clause, if applicable, also identify potential risks or obligations relevant to the user's role/goal and suggest clear, actionable steps. Do not use jargon or technical legal terms without immediately explaining them.

    Here is the legal document to simplify:
    {request.document_text}

    Please provide:
    1. A concise, clear summary of the document.
    2. A point-by-point breakdown of the most important clauses. For each point, clearly state any potential risks or obligations, and suggest actionable next steps.
    3. A concluding summary of the overall risks and recommended actions.

    IMPORTANT DISCLAIMER: This information is for educational and informational purposes only and does not constitute legal advice. Please consult with a qualified legal professional for any legal concerns.
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