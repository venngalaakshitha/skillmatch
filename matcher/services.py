import PyPDF2
import logging
from typing import Set, Optional
from pydantic import BaseModel, Field, ValidationError

# 1. LOGIC: PROFESSIONAL LOGGING (Industry Standard)
# In a real job, you don't use 'print' because you can't see it on a server.
logger = logging.getLogger(__name__)

class ResumeData(BaseModel):
    # Field(...) ensures the text isn't just an empty string
    text: str = Field(..., min_length=1)
    skills: Set[str] = Field(default_factory=set)
    email: str = "N/A"

def extract_text_from_pdf(path: str) -> str:
    """
    Logic: The Safety Net.
    Imagination: A conveyor belt that stops if the item is broken.
    """
    try:
        text_content = []
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            # 2026 PRO TIP: Check if the PDF is encrypted/locked
            if reader.is_encrypted:
                logger.error(f"Access Denied: PDF at {path} is encrypted.")
                return ""
                
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text_content.append(extracted)
        
        return " ".join(text_content).strip()

    except FileNotFoundError:
        logger.error(f"IO Error: File missing at {path}")
        return ""
    except Exception as e:
        logger.error(f"Critical Extraction Failure: {e}")
        return ""

# 2. LOGIC: THE SERVICE LAYER (The "Manager")
# This is what your views.py should actually call.
def get_clean_resume_payload(path: str) -> Optional[ResumeData]:
    """
    Logic: Ensures only VALIDATED data reaches your Matcher.
    If it returns None, your View knows to show an error to the user.
    """
    raw_text = extract_text_from_pdf(path)
    
    if not raw_text:
        return None

    try:
        # We wrap the text in our Pydantic 'Blueprint'
        return ResumeData(text=raw_text)
    except ValidationError as e:
        logger.error(f"Data Schema Mismatch: {e.json()}")
        return None
