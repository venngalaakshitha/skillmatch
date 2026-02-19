# 🚀 SkillMatch – ATS Resume Analyzer

SkillMatch is a Django-based web application that simulates how an Applicant Tracking System (ATS) evaluates resumes.  
The system allows users to log in, upload resumes (PDF/DOCX), extract text, detect skills, calculate an ATS-style score, and view analysis history.

This project demonstrates practical backend engineering, resume processing, scoring logic, and corporate UI design.

---

## ✅ Live Features

- Corporate Login / Signup
- Resume Upload (PDF / DOCX)
- Resume Text Extraction (PyPDF2 / python-docx)
- Skill Detection (Python / Django / SQL + multiple skills)
- ATS Scoring Algorithm (6 evaluation criteria)
- Suggested Role Generation
- Resume Analysis History
- PDF Report Download
- Resume Delete Functionality

---

## ⚡ Quick Setup

```bash
git clone https://github.com/venngalaakshitha/skillmatch.git
cd skillmatch

python -m venv venv
venv\Scripts\activate     # Windows

pip install django PyPDF2 python-docx

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
Open:

http://127.0.0.1:8000/login/
🔐 Demo Credentials
Username: admin
Password: admin123
(Or create your own superuser)

🛠️ Technology Stack
Backend

Python

Django 4.2

Resume Processing

PyPDF2 (PDF parsing)

python-docx (DOCX parsing)

Frontend

HTML5

Bootstrap 5

Font Awesome

Database

SQLite

Authentication

Django Authentication System

🧠 How SkillMatch Works
User logs in

Uploads resume (PDF/DOCX) + optional Job Description

PyPDF2 / python-docx extracts resume text

Skill detection logic identifies technologies

ATS scoring algorithm evaluates resume quality

System suggests relevant job role

Results stored in Resume model

Displayed in analysis history dashboard

📊 ATS Scoring Criteria
SkillMatch evaluates resumes using:

Structure (15%) → Resume sections (Summary, Skills, Experience)

Skills (25%) → Technical skills detected

JD Match (25%) → Keyword matching

Experience (15%) → Experience indicators

Technical Depth (10%) → Tools & technologies

Formatting (10%) → ATS compatibility signals

📂 Project Structure
skillmatch/
├── core/                # Django settings
├── matcher/
│   ├── views.py         # Login + ATS analysis
│   ├── models.py        # Resume model
│   └── templates/
│       ├── login.html
│       ├── upload.html
│       └── history.html
├── manage.py
└── requirements.txt
🎯 Skills Demonstrated
Django authentication system

File upload handling

PDF/DOCX text extraction

Resume parsing logic

Skill detection algorithm

ATS scoring system design

Bootstrap corporate UI

Database CRUD operations

Debugging & validation

🚀 Future Enhancements
Advanced NLP-based skill extraction

Resume vs Job Description semantic matching

Visual keyword highlighting

Enhanced PDF report generation

Recruiter analytics dashboard

👩‍💻 Author
Akshitha Vengala
Python & Django Developer

GitHub: https://github.com/venngalaakshitha
