from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Required for React frontend to talk to backend

# Import your simplification logic
from .api.v1.simplify_document import simplify_legal_document_endpoint

app = FastAPI(
    title="Legal Document Demystifier Backend",
    description="API for simplifying legal documents using Generative AI.",
    version="1.0.0",
)

# --- CORS Configuration ---
# This is crucial for your React frontend to be able to make requests to this FastAPI backend.
# In a real production app, you'd restrict origins more strictly.
origins = [
    "http://localhost:3000",  # Default React development server port
    "http://localhost:8000",  # If your React app is on a different port or served directly by backend
    # Add your Google Cloud App Engine frontend URL here once deployed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- END CORS Configuration ---


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Legal Document Demystifier Backend!"}

# Include your specific endpoint for document simplification
app.include_router(simplify_legal_document_endpoint, prefix="/api/v1")