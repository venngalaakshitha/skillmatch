# Minimum words for ATS readability
MIN_WORD_COUNT = 120

# ======================
# SECTION HEADERS
# ======================

SKILLS_HEADERS = [
    "skills", "technical skills", "skill set",
    "key skills", "competencies", "tech stack"
]

EXPERIENCE_HEADERS = [
    "experience", "work experience",
    "professional experience", "internship", "employment"
]

EDUCATION_HEADERS = [
    "education", "academics",
    "educational background", "qualifications"
]

PROJECT_HEADERS = [
    "projects", "project work",
    "academic projects", "personal projects"
]

# ======================
# SKILLS
# ======================

COMMON_SKILLS = [
    "python", "django", "sql", "mysql",
    "html", "css", "javascript",
    "git", "java", "c++"
]

INFERRED_SKILLS = [
    "machine learning", "data science",
    "artificial intelligence"
]

# 🔴 REQUIRED for imports (your crash fix)
SKILL_KEYWORDS = COMMON_SKILLS

# ======================
# ROLE → SKILL MAP
# ======================

ROLE_SKILL_MAP = {
    "Backend Developer": ["python", "django", "sql"],
    "Frontend Developer": ["html", "css", "javascript"],
    "Software Engineer": ["python", "java", "git"],
}
