import re
import logging
from typing import Optional, Set, List, Tuple, Dict

import PyPDF2
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)


# =========================================
# DATA VALIDATION MODEL
# =========================================

class ResumeData(BaseModel):
    text: str = Field(..., min_length=1)
    skills: Set[str] = Field(default_factory=set)
    email: str = "N/A"


# =========================================
# CONSTANTS
# =========================================

STOPWORDS = {
    "and", "or", "the", "is", "in", "at", "of", "for", "a", "to", "with",
    "on", "as", "by", "an", "be", "this", "that", "from", "are", "was",
    "were", "it", "will", "your", "you", "their", "our", "we", "they"
}

TECH_KEYWORDS = [
    "python", "java", "c", "c++", "sql", "mysql", "postgresql",
    "html", "css", "javascript", "react", "node", "django", "flask",
    "api", "rest", "docker", "aws", "git", "github", "linux",
    "pandas", "numpy", "machine learning", "data analysis",
    "excel", "power bi", "tableau"
]

SOFT_SKILLS = [
    "communication", "teamwork", "leadership", "adaptability",
    "problem solving", "organizational skills", "initiative",
    "time management", "critical thinking"
]

RESUME_SECTIONS = [
    "summary", "objective", "education", "skills",
    "projects", "experience", "internship", "certifications",
    "achievements", "languages"
]

ACTION_VERBS = [
    "developed", "designed", "implemented", "built",
    "created", "led", "managed", "engineered", "optimized"
]


# =========================================
# TEXT CLEANING
# =========================================

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s@.+#-]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_keywords(text: str) -> Set[str]:
    cleaned = clean_text(text)
    words = cleaned.split()
    return {w for w in words if w not in STOPWORDS and len(w) > 2}


# =========================================
# PDF TEXT EXTRACTION
# =========================================

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

        return "\n".join(text_content).strip()

    except FileNotFoundError:
        logger.error(f"File not found: {path}")
        return ""

    except Exception as e:
        logger.error(f"Extraction error: {e}")
        return ""


def get_clean_resume_payload(path: str) -> Optional[ResumeData]:
    raw_text = extract_text_from_pdf(path)

    if not raw_text:
        return None

    try:
        return ResumeData(text=clean_text(raw_text))
    except ValidationError as e:
        logger.error(f"Validation error: {e.json()}")
        return None


# =========================================
# SKILL EXTRACTION
# =========================================

def extract_technical_skills(resume_text: str) -> List[str]:
    text = clean_text(resume_text)
    return [skill for skill in TECH_KEYWORDS if skill in text]


def extract_soft_skills(resume_text: str) -> List[str]:
    text = clean_text(resume_text)
    return [skill for skill in SOFT_SKILLS if skill in text]


# =========================================
# JD MATCHING
# =========================================

def jd_match_score(resume_text: str, jd_text: str) -> Tuple[int, List[str]]:
    if not jd_text or not jd_text.strip():
        return 0, []

    resume_keywords = extract_keywords(resume_text)
    jd_keywords = extract_keywords(jd_text)

    if not jd_keywords:
        return 0, []

    matched = resume_keywords.intersection(jd_keywords)
    score = int((len(matched) / len(jd_keywords)) * 100)

    return score, sorted(list(matched))[:20]


def keyword_match_score(resume_text: str, jd_text: str) -> Tuple[int, List[str]]:
    return jd_match_score(resume_text, jd_text)


def missing_skills(resume_text: str, jd_text: str) -> List[str]:
    if not jd_text or not jd_text.strip():
        return []

    resume_keywords = extract_keywords(resume_text)
    jd_keywords = extract_keywords(jd_text)

    missing = jd_keywords - resume_keywords
    return sorted(list(missing))[:15]


def skill_gap_analysis(resume_text: str, jd_text: str) -> List[str]:
    return missing_skills(resume_text, jd_text)


# =========================================
# ATS SCORE ENGINE
# =========================================

def realistic_ats_score(resume_text: str, job_description: str) -> Tuple[int, Dict[str, int]]:
    resume_text = clean_text(resume_text)
    job_description = clean_text(job_description)

    breakdown = {}

    # 1. JD Match (30)
    jd_score, _ = jd_match_score(resume_text, job_description)
    breakdown["JD Match"] = min(int(jd_score * 0.30), 30)

    # 2. Skills Match (25)
    tech_skills_found = extract_technical_skills(resume_text)
    skills_score = min(len(tech_skills_found) * 3, 25)
    breakdown["Skills Match"] = skills_score

    # 3. Resume Structure (20)
    section_hits = sum(1 for section in RESUME_SECTIONS if section in resume_text)
    structure_score = min(section_hits * 3, 20)
    breakdown["Structure"] = structure_score

    # 4. Experience / Action Depth (15)
    action_hits = sum(1 for word in ACTION_VERBS if word in resume_text)
    experience_score = min(action_hits * 3, 15)
    breakdown["Experience Depth"] = experience_score

    # 5. Formatting / Content Richness (10)
    formatting_score = 0
    word_count = len(resume_text.split())

    if word_count > 150:
        formatting_score += 5
    if word_count > 250:
        formatting_score += 3
    if len(re.findall(r'\b\d+%|\b\d+\b', resume_text)) > 3:
        formatting_score += 2

    breakdown["Formatting"] = min(formatting_score, 10)

    total_score = sum(breakdown.values())
    return total_score, breakdown


# =========================================
# RESUME DIAGNOSIS ENGINE
# =========================================
def diagnose_resume(resume_text: str) -> Dict[str, object]:
    original_text = resume_text or ""
    text = clean_text(resume_text)

    found_tech = extract_technical_skills(text)
    found_soft = extract_soft_skills(text)

    has_projects = "project" in text or "projects" in text
    has_certifications = "certification" in text or "certifications" in text
    has_experience = "experience" in text or "internship" in text or "intern" in text
    has_education = "education" in text or "college" in text or "b.tech" in text or "degree" in text
    has_email = "@" in text
    has_phone = bool(re.search(r'\b\d{10}\b', text))
    has_linkedin = "linkedin" in text
    has_github = "github" in text

    word_count = len(text.split())
    action_hits = sum(1 for word in ACTION_VERBS if word in text)
    has_numbers = bool(re.search(r'\b\d+%?\b', text))
    line_count = len([line for line in original_text.splitlines() if line.strip()])
    section_hits = sum(1 for section in RESUME_SECTIONS if section in text)

    diagnosis = {
        "overall_strength": "Weak",
        "ats_readability": "Poor",
        "strengths": [],
        "weaknesses": [],
        "missing_sections": [],
        "suggestions": [],
        "critical_red_flags": [],
        "moderate_red_flags": [],
        "positive_signals": [],
        "verdict": "Weak Resume Profile",
        "technical_skills_found": found_tech,
        "soft_skills_found": found_soft,
        "risk_level": "Low",
        "readable": True,
        "warnings": [],
        "word_count": word_count,
        "section_hits": section_hits,
        "line_count": line_count,
    }

    # ATS Readability
    if word_count > 150:
        diagnosis["ats_readability"] = "Moderate"
    if word_count > 250 and len(found_tech) >= 3:
        diagnosis["ats_readability"] = "Good"

    # Missing Sections
    if not has_projects:
        diagnosis["missing_sections"].append("Projects")
    if not has_certifications:
        diagnosis["missing_sections"].append("Certifications")
    if not has_experience:
        diagnosis["missing_sections"].append("Internship / Experience")
    if not has_linkedin:
        diagnosis["missing_sections"].append("LinkedIn")
    if not has_github:
        diagnosis["missing_sections"].append("GitHub")
    if len(found_tech) == 0:
        diagnosis["missing_sections"].append("Technical Skills")

    # Positive Signals
    if has_email and has_phone:
        diagnosis["positive_signals"].append("Basic contact details are present.")
    if has_education:
        diagnosis["positive_signals"].append("Education section is present.")
    if len(found_soft) >= 2:
        diagnosis["positive_signals"].append("Resume demonstrates some soft-skill visibility.")
    if len(found_tech) >= 3:
        diagnosis["positive_signals"].append("Technical skill stack is reasonably visible.")
    if has_projects:
        diagnosis["positive_signals"].append("Project evidence is present.")
    if has_linkedin or has_github:
        diagnosis["positive_signals"].append("Professional profile / portfolio presence detected.")
    if has_numbers:
        diagnosis["positive_signals"].append("Resume includes quantified or measurable information.")
    if action_hits >= 2:
        diagnosis["positive_signals"].append("Resume uses action-oriented execution language.")

    # Critical Red Flags
    if len(found_tech) == 0:
        diagnosis["critical_red_flags"].append("No recognizable technical skill stack detected.")
    if not has_projects:
        diagnosis["critical_red_flags"].append("No project evidence found to support practical capability.")
    if word_count < 120:
        diagnosis["critical_red_flags"].append("Resume content is too thin for competitive ATS screening.")
    if action_hits == 0:
        diagnosis["critical_red_flags"].append("Resume lacks strong action-oriented language and appears passive.")
    if not has_numbers:
        diagnosis["critical_red_flags"].append("No measurable achievements, metrics, or quantified outcomes detected.")
    if not has_email:
        diagnosis["critical_red_flags"].append("Primary contact email was not detected.")
    if not has_education:
        diagnosis["critical_red_flags"].append("Education section is missing.")

    # Moderate Red Flags
    if 0 < len(found_tech) < 3:
        diagnosis["moderate_red_flags"].append("Technical skill footprint is too narrow.")
    if not has_certifications:
        diagnosis["moderate_red_flags"].append("No certifications section detected.")
    if not has_experience:
        diagnosis["moderate_red_flags"].append("No internship or experience evidence found.")
    if not has_linkedin and not has_github:
        diagnosis["moderate_red_flags"].append("No professional portfolio or profile links detected.")
    if not any(role in text for role in [
        "developer", "engineer", "analyst", "designer", "backend",
        "frontend", "full stack", "software"
    ]):
        diagnosis["moderate_red_flags"].append("Resume lacks clear professional role positioning.")

    diagnosis["strengths"] = diagnosis["positive_signals"][:]
    diagnosis["weaknesses"] = diagnosis["critical_red_flags"] + diagnosis["moderate_red_flags"]

    # Overall Score
    score = 0
    score += len(found_tech) * 2
    score += len(found_soft)
    score += 3 if has_projects else 0
    score += 2 if has_certifications else 0
    score += 2 if has_experience else 0
    score += 1 if has_linkedin else 0
    score += 1 if has_github else 0
    score += 2 if has_education else 0
    score += 2 if has_numbers else 0
    score += 2 if action_hits >= 2 else 0

    if score >= 14:
        diagnosis["overall_strength"] = "Strong"
        diagnosis["ats_readability"] = "Good"
    elif score >= 8:
        diagnosis["overall_strength"] = "Average"
        if diagnosis["ats_readability"] == "Poor":
            diagnosis["ats_readability"] = "Moderate"
    else:
        diagnosis["overall_strength"] = "Weak"

    # Verdict
    critical_count = len(diagnosis["critical_red_flags"])
    moderate_count = len(diagnosis["moderate_red_flags"])

    if critical_count >= 5:
        diagnosis["verdict"] = "High Rejection Risk — resume is currently not competitive for most screening pipelines."
    elif critical_count >= 3:
        diagnosis["verdict"] = "Weak Resume Profile — significant improvement is required before serious applications."
    elif moderate_count >= 4:
        diagnosis["verdict"] = "Moderate Resume Quality — functional, but not yet recruiter-strong."
    else:
        diagnosis["verdict"] = "Reasonably Competitive Resume — acceptable baseline with room for refinement."

    # Suggestions
    if len(found_tech) < 3:
        diagnosis["suggestions"].append("Strengthen the resume with more role-relevant technical skills.")
    if not has_projects:
        diagnosis["suggestions"].append("Add project-based proof of capability to improve credibility.")
    if not has_certifications:
        diagnosis["suggestions"].append("Include certifications if they support your target role.")
    if not has_experience:
        diagnosis["suggestions"].append("Add internship, training, freelance, or hands-on practical exposure.")
    if not has_linkedin:
        diagnosis["suggestions"].append("Add your LinkedIn profile for professional visibility.")
    if not has_github:
        diagnosis["suggestions"].append("Include GitHub if applying for technical or development roles.")
    if not has_numbers:
        diagnosis["suggestions"].append("Add quantified impact, metrics, or outcomes wherever possible.")
    if action_hits == 0:
        diagnosis["suggestions"].append("Rewrite bullet points using stronger execution-oriented action verbs.")

    # ATS Risk / Canva-like warning logic
    if word_count < 80:
        diagnosis["warnings"].append("Very little readable text was extracted from the resume.")
    if section_hits < 2:
        diagnosis["warnings"].append("Standard resume sections were not clearly detected.")
    if line_count < 8:
        diagnosis["warnings"].append("Resume appears poorly structured after extraction.")
    if len(found_tech) == 0:
        diagnosis["warnings"].append("No clear technical keywords were detected.")
    if word_count < 120 and section_hits < 3:
        diagnosis["warnings"].append("This resume may be using a visual or template-heavy format that ATS tools struggle to parse.")

    if len(diagnosis["warnings"]) >= 4:
        diagnosis["risk_level"] = "High"
        diagnosis["readable"] = False
    elif len(diagnosis["warnings"]) >= 2:
        diagnosis["risk_level"] = "Moderate"
        diagnosis["readable"] = False
    else:
        diagnosis["risk_level"] = "Low"
        diagnosis["readable"] = True

    return diagnosis


# =========================================
# GENERAL SUGGESTIONS
# =========================================

def resume_suggestions(score: int) -> List[str]:
    suggestions = []

    if score < 40:
        suggestions.append("Add more relevant technical skills.")
        suggestions.append("Include project descriptions.")

    if score < 60:
        suggestions.append("Tailor your resume using keywords from the job description.")

    if score < 80:
        suggestions.append("Add measurable achievements and outcomes.")

    suggestions.append("Use strong action verbs like 'developed', 'implemented', 'designed'.")

    return suggestions


# =========================================
# AI-LIKE REWRITE SUGGESTIONS
# =========================================

def ai_resume_suggestions(resume_text: str, job_description: str = "") -> Tuple[List[str], List[Tuple[str, str]]]:
    suggestions = []
    improved_lines = []

    lines = resume_text.split("\n")
    weak_words = ["worked on", "responsible for", "did", "helped", "made"]

    for line in lines:
        clean_line = line.strip().lower()

        if not clean_line:
            continue

        if "team" in clean_line:
            suggestions.append("Highlight your individual contribution, not just team involvement.")

        for word in weak_words:
            if word in clean_line:
                rewritten = re.sub(word, "", line, flags=re.IGNORECASE).strip()
                if rewritten:
                    improved = f"Developed {rewritten[0].lower() + rewritten[1:]}" if len(rewritten) > 1 else f"Developed {rewritten}"
                    improved_lines.append((line, improved))
                    suggestions.append(f"Rewrite: '{line}' → '{improved}'")
                break

    if not any(verb in resume_text.lower() for verb in ACTION_VERBS):
        suggestions.append("Use strong action verbs like Developed, Designed, Implemented.")

    if "%" not in resume_text:
        suggestions.append("Add measurable results (e.g., improved efficiency by 30%).")

    if "project" not in resume_text.lower():
        suggestions.append("Add a project section to showcase practical experience.")

    if job_description:
        missing = missing_skills(resume_text, job_description)
        if missing:
            suggestions.append(f"Add relevant keywords from JD: {', '.join(missing[:5])}")

    return suggestions, improved_lines

# =========================================
# ATS READABILITY / TEMPLATE WARNING
# =========================================

def detect_ats_template_risk(resume_text: str) -> dict:
    """
    Detect whether resume may be poorly readable by ATS due to template-heavy formatting.
    """
    original_text = resume_text or ""
    text = clean_text(original_text)

    warnings = []
    risk_level = "Low"
    readable = True

    word_count = len(text.split())
    line_count = len([line for line in original_text.splitlines() if line.strip()])
    section_hits = sum(1 for section in RESUME_SECTIONS if section in text)

    # Heuristic 1: Too little extracted text
    if word_count < 80:
        warnings.append("Very little readable text was extracted from the resume.")
    
    # Heuristic 2: Missing standard resume structure
    if section_hits < 2:
        warnings.append("Standard resume sections (like Skills, Projects, Education, Experience) were not clearly detected.")

    # Heuristic 3: Looks too compressed / extraction-poor
    if line_count < 8:
        warnings.append("Resume appears poorly structured after extraction, which may indicate ATS readability issues.")

    # Heuristic 4: Too few technical/career signals
    tech_found = extract_technical_skills(text)
    if len(tech_found) == 0:
        warnings.append("No clear technical keywords were detected. This may be due to either weak content or unreadable formatting.")

    # Heuristic 5: Suspiciously low content richness
    if word_count < 120 and section_hits < 3:
        warnings.append("This resume may be using a visual/template-heavy format that ATS tools struggle to parse.")

    # Final risk scoring
    if len(warnings) >= 4:
        risk_level = "High"
        readable = False
    elif len(warnings) >= 2:
        risk_level = "Moderate"
        readable = False
    else:
        risk_level = "Low"
        readable = True

    return {
        "risk_level": risk_level,
        "readable": readable,
        "warnings": warnings,
        "word_count": word_count,
        "section_hits": section_hits,
    }