from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.simplify_document import router as simplify_router
from app.api.v1.followup import router as followup_router

app = FastAPI(title="Legal Document Demystifier Backend")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to Legal Document Demystifier"}

app.include_router(simplify_router, prefix="/api/v1")
app.include_router(followup_router)
