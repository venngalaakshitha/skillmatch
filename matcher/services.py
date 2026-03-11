import re
import PyPDF2
import logging
from typing import Set, Optional
from pydantic import BaseModel, Field, ValidationError
from .models import Resume

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

def process_resume_and_save(resume_id: int) -> bool:
    """
    LOGIC: The Coordinator. 
    It fetches the DB record, runs the 'Conveyor Belt' (extraction), 
    and saves the results back to the database.
    """
    try:
        # 1. Fetch from Database
        resume = Resume.objects.get(id=resume_id)
        
        # 2. Use your "Manager" logic to get clean data
        data = get_clean_resume_payload(resume.file.path)
        
        if not data:
            logger.error(f"Failed to process Resume ID {resume_id}")
            return False
            
        # 3. Update Database (The Persistence layer)
        resume.extracted_text = data.text
        resume.save()
        
        return True

    except Resume.DoesNotExist:
        logger.error(f"Database Error: Resume {resume_id} not found.")
        return False

def realistic_ats_score(resume_text: str, jd_text: str):
    """
    LOGIC: Multi-factor Scoring Engine.
    IMAGINATION: A judge with a checklist looking for specific 'Green Flags'.
    """
    text = resume_text.upper()
    jd = jd_text.upper()
    score = 0
    breakdown = {}

    # 1. JD KEYWORD MATCH (25 pts) - O(1) Set Logic
    resume_words = set(re.findall(r'\b[A-Z]{3,}\b', text))
    jd_words = set(re.findall(r'\b[A-Z]{3,}\b', jd))
    
    if jd_words:
        matched = jd_words & resume_words
        keyword_score = min((len(matched) / len(jd_words)) * 25, 25)
    else:
        keyword_score = 10 # Neutral default
    score += keyword_score
    breakdown['JD Match'] = round(keyword_score, 1)

    # 2. STRUCTURE DETECTION (15 pts)
    # Pro Logic: Checking for standard ATS sections
    sections = ['EXPERIENCE', 'PROJECTS', 'EDUCATION', 'SKILLS', 'SUMMARY']
    found_sections = sum(1 for sec in sections if sec in text)
    structure_score = min(found_sections * 3, 15)
    score += structure_score
    breakdown['Structure'] = structure_score

    # 3. TECHNICAL DEPTH (10 pts)
    # Pro Logic: Checking for 'High-Stake' tools
    tech_stack = {'DJANGO', 'DOCKER', 'AWS', 'POSTGRESQL', 'REDIS', 'API'}
    tech_hits = tech_stack & resume_words
    tech_score = min(len(tech_hits) * 2, 10)
    score += tech_score
    breakdown['Tech Depth'] = tech_score

    # 4. FORMATTING & LENGTH (50 pts - Default Base)
    # Most ATS give a base score for a readable length
    base_score = 40 if 300 < len(resume_text) < 5000 else 20
    score += base_score
    breakdown['Formatting'] = base_score

    return min(100, round(score)), breakdown

    
    