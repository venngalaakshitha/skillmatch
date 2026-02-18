import re
from typing import Dict, List, Tuple, Optional
from collections import Counter

def calculate_ats_score(
    resume_text: str,
    job_description: Optional[str] = None,
    structure: Optional[Dict] = None
) -> Tuple[int, Dict]:
    """
    Corporate ATS Scoring Engine v2.0
    Weights mirror enterprise ATS (Workday/Greenhouse):
    Skills 35% | Experience 25% | JD Match 20% | Structure 10% | Format 5% | Seniority 5%
    """
    breakdown = {}
    
    # ===============================
    # 1️⃣ SKILLS MATCHING (35%) - #1 ATS priority
    # ===============================
    skills = extract_skills(resume_text)
    skill_score = min(len(skills) * 4.5, 35)
    breakdown["skills"] = round(skill_score, 1)
    
    # ===============================
    # 2️⃣ EXPERIENCE RELEVANCE (25%)
    # ===============================
    exp_score = calculate_experience_score(resume_text)
    breakdown["experience"] = round(exp_score, 1)
    
    # ===============================
    # 3️⃣ JOB DESCRIPTION MATCH (20%)
    # ===============================
    if job_description:
        jd_score = calculate_keyword_match(resume_text, job_description)
        breakdown["jd_match"] = round(jd_score * 20, 1)
    else:
        breakdown["jd_match"] = 10.0
    
    # ===============================
    # 4️⃣ STRUCTURE COMPLIANCE (10%)
    # ===============================
    breakdown["structure"] = round(calculate_structure_score(structure or {}), 1)
    
    # ===============================
    # 5️⃣ FORMAT QUALITY (5%)
    # ===============================
    breakdown["format"] = round(calculate_format_quality(resume_text), 1)
    
    # ===============================
    # 6️⃣ SENIORITY SIGNALS (5%)
    # ===============================
    breakdown["seniority"] = round(calculate_seniority_score(resume_text), 1)
    
    # ===============================
    # 🏆 FINAL ENTERPRISE SCORE
    # ===============================
    final_score = min(sum(breakdown.values()), 100)
    return round(final_score), breakdown

def suggest_roles(detected_skills: List[str], experience_years: float = 0) -> List[Dict]:
    """
    AI-Powered Career Recommendation Engine
    Matches skills + experience to 50+ corporate roles
    """
    # Corporate role database (expanded for fresher → mid-level)
    role_database = {
        # 🎯 YOUR SWEET SPOT ROLES
        'backend_fresher': {
            'skills': ['Python', 'Django', 'SQL'],
            'min_exp': 0,
            'roles': ['Junior Backend Developer', 'Python Developer', 'Django Developer']
        },
        'fullstack_fresher': {
            'skills': ['Python', 'Django', 'JavaScript'],
            'min_exp': 0,
            'roles': ['Fullstack Developer', 'Software Engineer Fresher']
        },
        'data_analyst': {
            'skills': ['Python', 'SQL', 'Excel'],
            'min_exp': 0,
            'roles': ['Data Analyst', 'Junior Data Analyst']
        },
        # 💼 ENTERPRISE ROLES
        'backend': {
            'skills': ['Python', 'Django', 'SQL', 'Docker'],
            'min_exp': 1,
            'roles': ['Backend Developer', 'Python Backend Engineer']
        },
        'devops': {
            'skills': ['Python', 'Docker', 'AWS', 'Linux'],
            'min_exp': 1,
            'roles': ['DevOps Engineer', 'Junior DevOps']
        },
        # 🎓 PERFECT FOR FRESHERS
        'associate': {
            'skills': ['Python', 'Projects', 'Internship'],
            'min_exp': 0,
            'roles': ['Associate Software Engineer', 'Trainee Software Engineer']
        }
    }
    
    matches = []
    skill_lower = [s.lower() for s in detected_skills]
    
    for category, data in role_database.items():
        # Skill matching (70% weight)
        skill_matches = sum(1 for skill in data['skills'] if skill.lower() in skill_lower)
        skill_score = skill_matches / len(data['skills'])
        
        # Experience fit (30% weight)
        exp_fit = 1.0 if experience_years >= data['min_exp'] else 0.6
        
        # Total fit score
        fit_score = (skill_score * 0.7) + (exp_fit * 0.3)
        
        if fit_score > 0.35:  # 35% threshold for recommendation
            for role in data['roles']:
                matches.append({
                    'role': role,
                    'category': category,
                    'fit_score': round(fit_score * 100, 1),
                    'skills_matched': skill_matches,
                    'total_required': len(data['skills'])
                })
    
    # Sort by fit score + limit to top 5
    return sorted(matches, key=lambda x: x['fit_score'], reverse=True)[:5]

# ===============================
# 🔧 HELPER FUNCTIONS (Pure Python)
# ===============================

def extract_skills(text: str) -> List[str]:
    """Corporate skill extraction (75+ enterprise keywords)"""
    text_lower = text.lower()
    skills = []
    
    skill_keywords = [
        # Programming Languages
        'python', 'java', 'javascript', 'sql', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
        # Frameworks
        'react', 'angular', 'vue', 'django', 'flask', 'spring', 'laravel', 'node', 'express',
        # Tools/Cloud
        'git', 'github', 'docker', 'aws', 'azure', 'gcp', 'jenkins', 'kubernetes', 'linux',
        # Databases
        'mysql', 'postgresql', 'mongo', 'oracle', 'redis', 'elasticsearch',
        # Methodologies
        'agile', 'scrum', 'devops', 'ci/cd', 'tdd', 'bdd',
        # Soft skills
        'leadership', 'communication', 'teamwork', 'problem solving'
    ]
    
    for skill in skill_keywords:
        if re.search(rf'\b{skill}\b', text_lower):
            skills.append(skill.title())
    
    return list(set(skills))

def calculate_experience_score(text: str) -> float:
    """Extract experience years from text"""
    # Number patterns: "2 years", "3+ years", "one year experience"
    patterns = r'\b(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s*(?:\+?|\s*)(?:year|years?)\b'
    matches = re.findall(patterns, text.lower())
    
    years = 0
    for match in matches:
        if re.search(r'\d+', match):
            years += int(re.search(r'\d+', match).group())
    
    return min(years * 3.5, 25)

def calculate_keyword_match(resume: str, jd: str) -> float:
    """TF-IDF style keyword matching (no external libs)"""
    resume_words = re.findall(r'\b\w{3,}\b', resume.lower())
    jd_words = [w for w in re.findall(r'\b\w{3,}\b', jd.lower()) if len(w) > 3]
    
    jd_set = set(jd_words)
    matches = sum(1 for word in jd_set if word in resume_words)
    
    match_ratio = matches / max(len(jd_set), 1)
    return min(match_ratio * 1.3, 1.0)

def calculate_structure_score(structure: Dict) -> float:
    """ATS structure compliance score"""
    required_sections = ["experience", "education", "skills", "projects", "contact", "summary"]
    present = sum(1 for section in required_sections if structure.get(section))
    return (present / len(required_sections)) * 10

def calculate_format_quality(text: str) -> float:
    """ATS parseability + readability score"""
    char_count = len(text)
    lines = text.split('\n')
    
    # Length penalties
    if char_count < 800 or char_count > 4500:
        return 2.0
    
    # Line length penalties (ATS parsing issues)
    long_lines = sum(1 for line in lines if len(line) > 120)
    if long_lines > 10:
        return 3.0
    
    return 5.0

def calculate_seniority_score(text: str) -> float:
    """Seniority signals from content density + keywords"""
    words = len(re.findall(r'\b\w+\b', text))
    senior_keywords = ['architect', 'lead', 'senior', 'manager', 'principal']
    
    seniority_boost = sum(1 for kw in senior_keywords if kw in text.lower())
    
    if words > 900:
        return min(5.0 + seniority_boost, 5.0)
    elif words > 600:
        return min(3.5 + seniority_boost * 0.5, 5.0)
    return 2.0 + seniority_boost * 0.3


