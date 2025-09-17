from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ✅ Import the router, not the function
from .api.v1.simplify_document import router as simplify_router

app = FastAPI(
    title="Legal Document Demystifier Backend",
    description="API for simplifying legal documents using Generative AI.",
    version="1.0.0",
)

# --- CORS Configuration ---
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
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

# ✅ Register the router properly
app.include_router(simplify_router, prefix="/api/v1")