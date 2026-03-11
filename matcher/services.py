import PyPDF2
from typing import Set, List
from pydantic import BaseModel, EmailStr, ValidationError

# 2026 PRO TOPIC: Data Validation
class ResumeData(BaseModel):
    text: str
    skills: Set[str] = set()
    # Adding EmailStr (requires 'pip install pydantic[email]') 
    # proves you know how to validate PII (Personal Info)
    email: str = "N/A" 

def extract_text_from_pdf(path: str) -> str: # Added Type Hints
    """Extracts text with professional error handling."""
    try:
        text = ""
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + " "
        return text.strip()
    except FileNotFoundError:
        print(f"Error: File not found at {path}")
        return ""
    except Exception as e:
        # 2026 PRO TOPIC: Professional Logging (Replace prints later)
        print(f"PDF extraction error: {e}")
        return ""
