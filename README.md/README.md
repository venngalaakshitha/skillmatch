# SkillMatch – ATS Resume Analyzer

SkillMatch is a Django-based web application designed to evaluate resumes using ATS-style analysis.  
The system processes uploaded resumes, extracts relevant information, calculates an ATS score, and provides improvement suggestions.

This project demonstrates practical skills in **Python, Django, backend logic, and UI design**.

---

## Features

- User authentication (Login / Signup)
- Resume upload functionality
- Resume text extraction
- Skill detection
- ATS score calculation
- Suggested job role generation
- Resume analysis history
- Resume detail view with recommendations

---

## ATS Evaluation Criteria

Resumes are analyzed based on:

- Resume structure and sections
- Skills presence
- Keyword matching
- Experience indicators
- Technical depth
- Formatting quality

---

## Technology Stack

Backend:
- Python
- Django

Frontend:
- HTML5
- Bootstrap 5

Libraries:
- PyPDF2
- python-docx

Database:
- SQLite

---

## Installation & Setup

```bash
git clone https://github.com/venngalaakshitha/skillmatch.git
cd skillmatch

python -m venv venv
venv\Scripts\activate   # Windows

pip install -r requirements.txt

python manage.py migrate
python manage.py runserver

Learning Outcomes

This project highlights:

Django project architecture

Authentication system implementation

File upload handling

Resume parsing logic

ATS-style scoring algorithm

UI/UX design with Bootstrap

Debugging and error handling

Future Enhancements

Advanced NLP-based skill extraction

Resume vs Job Description matching

PDF report generation

Recruiter analytics dashboard

Author

Akshitha Vengala
Python & Django Developer

GitHub: https://github.com/venngalaakshitha
