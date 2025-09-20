# filepath: backend/api/followup.py
from fastapi import APIRouter
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import google.generativeai as genai

router = APIRouter()

class FollowUpRequest(BaseModel):
    query: str
    context: str

# Load environment variables and configure Gemini
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-2.5-pro")

def generate_answer(query, context):
    prompt = f"""
You are a legal AI assistant.
Given the following context from a legal document, answer the user's follow-up question in a clear and concise way.

Context:
{context}

Question:
{query}
"""
    try:
        response = model.generate_content(prompt, generation_config=genai.types.GenerationConfig(temperature=0.2))
        return response.text
    except Exception as e:
        return f"Error generating answer: {str(e)}"

@router.post("/api/followup")
async def followup(request: FollowUpRequest):
    answer = generate_answer(request.query, request.context)
    return {"answer": answer}