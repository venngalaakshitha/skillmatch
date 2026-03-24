import re
import PyPDF2
import logging
from typing import Optional, Set
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)


# ==============================
# DATA VALIDATION MODEL
# ==============================

class ResumeData(BaseModel):
    text: str = Field(..., min_length=1)
    skills: Set[str] = Field(default_factory=set)
    email: str = "N/A"


# ==============================
# PDF TEXT EXTRACTION
# ==============================

def extract_text_from_pdf(path: str) -> str:
    try:
        text_content = []

        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)

            if reader.is_encrypted:
                logger.error(f"Encrypted PDF: {path}")
                return ""

            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text_content.append(extracted)

        return " ".join(text_content).strip()

    except FileNotFoundError:
        logger.error(f"File not found: {path}")
        return ""

    except Exception as e:
        logger.error(f"Extraction error: {e}")
        return ""


# ==============================
# CLEAN DATA PIPELINE
# ==============================

def get_clean_resume_payload(path: str) -> Optional[ResumeData]:

    raw_text = extract_text_from_pdf(path)

    if not raw_text:
        return None

    try:
        return ResumeData(text=raw_text)
    except ValidationError as e:
        logger.error(f"Validation error: {e.json()}")
        return None


# ==============================
# KEYWORD MATCH SCORE
# ==============================

def keyword_match_score(resume_text: str, jd_text: str):

    if not jd_text:
        return 0, []

    resume_words = set(re.findall(r'\b\w+\b', resume_text.lower()))
    jd_words = set(re.findall(r'\b\w+\b', jd_text.lower()))

    common = resume_words.intersection(jd_words)

    score = int((len(common) / len(jd_words)) * 100) if jd_words else 0

    return score, list(common)[:10]


# ==============================
# MISSING SKILLS
# ==============================

def missing_skills(resume_text: str, jd_text: str):

    resume_words = set(re.findall(r'\b\w+\b', resume_text.lower()))
    jd_words = set(re.findall(r'\b\w+\b', jd_text.lower()))

    missing = jd_words - resume_words

    return list(missing)[:10]


# ==============================
# RESUME SUGGESTIONS
# ==============================

def resume_suggestions(score: int):

    suggestions = []

    if score < 40:
        suggestions.append("Add more relevant technical skills.")
        suggestions.append("Include project descriptions.")

    if score < 60:
        suggestions.append("Match keywords from the job description.")

    if score < 80:
        suggestions.append("Add measurable achievements.")

    suggestions.append("Use strong action verbs like 'developed', 'implemented', 'designed'.")

    return suggestions


# ==============================
# ATS SCORE ENGINE
# ==============================

import re

def realistic_ats_score(resume_text, job_description):

    resume_text = resume_text.lower()
    job_description = job_description.lower()

    breakdown = {}

    # -----------------------
    # 1️⃣ JD Match (30)
    # -----------------------
    if not job_description.strip():
        jd_score = 0
    else:
        resume_words = set(re.findall(r'\w+', resume_text))
        jd_words = set(re.findall(r'\w+', job_description))

        matches = resume_words.intersection(jd_words)

        jd_score = min(len(matches) * 2, 30)

    breakdown["JD Match"] = jd_score


    # -----------------------
    # 2️⃣ Skills Match (25)
    # -----------------------
    tech_keywords = [
        "python","django","flask","sql","mysql",
        "postgresql","api","rest","docker","aws",
        "git","linux","pandas","numpy","machine learning",
        "html","css","javascript","react","node"
    ]

    skill_hits = sum(1 for skill in tech_keywords if skill in resume_text)

    skills_score = min(skill_hits * 3, 25)

    breakdown["Skills Match"] = skills_score


    # -----------------------
    # 3️⃣ Resume Structure (20)
    # -----------------------
    sections = [
        "education",
        "experience",
        "skills",
        "projects",
        "certifications",
        "summary"
    ]

    section_hits = sum(1 for section in sections if section in resume_text)

    structure_score = min(section_hits * 4, 20)

    breakdown["Structure"] = structure_score


    # -----------------------
    # 4️⃣ Experience Depth (15)
    # -----------------------
    experience_words = [
        "developed",
        "implemented",
        "built",
        "designed",
        "created",
        "led",
        "managed"
    ]

    exp_hits = sum(1 for word in experience_words if word in resume_text)

    experience_score = min(exp_hits * 3, 15)

    breakdown["Experience Depth"] = experience_score


    # -----------------------
    # 5️⃣ Formatting (10)
    # -----------------------
    formatting_score = 0

    word_count = len(resume_text.split())

    if word_count > 200:
        formatting_score += 5

    if "\n" in resume_text:
        formatting_score += 5

    breakdown["Formatting"] = formatting_score


    # -----------------------
    # Final Score
    # -----------------------
    total_score = sum(breakdown.values())

    return total_score, breakdown

# ========================================
# JD MATCHING + SKILL GAP (ADD BELOW ALL EXISTING FUNCTIONS)
# ========================================

import re

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    return text


def extract_keywords(text):
    words = clean_text(text).split()

    stopwords = {
        "and", "or", "the", "is", "in", "at", "of", "for",
        "a", "to", "with", "on", "as", "by", "an"
    }

    return set([w for w in words if w not in stopwords and len(w) > 2])


def jd_match_score(resume_text, jd_text):
    if not jd_text:
        return 0, []

    resume_keywords = extract_keywords(resume_text)
    jd_keywords = extract_keywords(jd_text)

    matched = resume_keywords.intersection(jd_keywords)

    if len(jd_keywords) == 0:
        return 0, []

    score = int((len(matched) / len(jd_keywords)) * 100)

    return score, list(matched)


def skill_gap_analysis(resume_text, jd_text):
    if not jd_text:
        return []

    resume_keywords = extract_keywords(resume_text)
    jd_keywords = extract_keywords(jd_text)

    missing = jd_keywords - resume_keywords

    return list(missing)[:15]

def ai_resume_suggestions(resume_text, job_description=""):
    suggestions = []
    improved_lines = []

    lines = resume_text.split("\n")

    # Weak words to detect
    weak_words = ["worked on", "responsible for", "did", "helped", "made"]

    for line in lines:
        clean = line.strip().lower()
        if "team" in clean:
            suggestions.append("Highlight your individual contribution, not just team involvement.")

        # Detect weak phrases
        for word in weak_words:
            if word in clean:
                improved = line.lower().replace(word, "").strip().capitalize()
                improved = "Developed " + improved
                improved_lines.append((line, improved))
                suggestions.append(f"Rewrite: '{line}' → '{improved}'")
                break

    # Action verbs check
    strong_verbs = ["developed", "designed", "implemented", "engineered"]
    if not any(verb in resume_text.lower() for verb in strong_verbs):
        suggestions.append("Use strong action verbs like Developed, Designed, Implemented.")

    # Quantification check
    if "%" not in resume_text:
        suggestions.append("Add measurable results (e.g., Increased efficiency by 30%).")

    # Project presence
    if "project" not in resume_text.lower():
        suggestions.append("Add project section to showcase practical experience.")

    # JD-based suggestions
    if job_description:
        jd_words = set(job_description.lower().split())
        resume_words = set(resume_text.lower().split())

        missing = jd_words - resume_words

        if missing:
            top_missing = list(missing)[:5]
            suggestions.append(
                f"Add relevant keywords from JD: {', '.join(top_missing)}"
            )

    return suggestions, improved_lines