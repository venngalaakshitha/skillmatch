import re
from .constants import (
    SKILLS_HEADERS, EXPERIENCE_HEADERS,
    EDUCATION_HEADERS, PROJECT_HEADERS,
    MIN_WORD_COUNT
)

def analyze_structure(text: str):
    lower = text.lower()

    def has_section(headers):
        return any(h in lower for h in headers)

    word_count = len(text.split())

    return {
        "has_skills": has_section(SKILLS_HEADERS),
        "has_experience": has_section(EXPERIENCE_HEADERS),
        "has_education": has_section(EDUCATION_HEADERS),
        "has_projects": has_section(PROJECT_HEADERS),
        "is_readable": word_count >= MIN_WORD_COUNT,
        "word_count": word_count,
    }
