import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env file (must be in your working directory)
load_dotenv()

# Print and check API key loading
api_key = os.getenv("GEMINI_API_KEY")
print("Loaded GEMINI_API_KEY:", api_key)

# If not loaded, try GOOGLE_API_KEY
if not api_key:
    api_key = os.getenv("GOOGLE_API_KEY")
    print("Loaded GOOGLE_API_KEY:", api_key)

if not api_key:
    raise ValueError("No Gemini/Google API key found in environment!")

# Configure Gemini SDK
genai.configure(api_key=api_key)

# List models and their supported methods
models = genai.list_models()
print("Available Gemini models and their supported methods:")
for m in models:
    print(m.name, "| supported methods:", m.supported_generation_methods)
