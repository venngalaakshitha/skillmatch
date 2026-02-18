# SkillMatch – ATS Resume Analyzer

SkillMatch is a Django-based ATS (Applicant Tracking System) Resume Analyzer
that helps job seekers evaluate how well their resume matches ATS systems
and job descriptions.

---

## 🚀 Features

- User authentication (Login / Logout)
- Resume upload (PDF)
- ATS structure analysis
- ATS score generation
- Skill extraction (explicit & inferred)
- Role recommendation
- Resume history per user
- Resume deletion
- Job Description (JD) match percentage
- Missing keyword detection
- Downloadable ATS analysis PDF report

---

## 🧠 How It Works

1. User uploads a resume (PDF)
2. Text is extracted from the resume
3. Resume structure is analyzed for ATS compatibility
4. Skills are extracted from resume content
5. ATS score is calculated based on structure and skills
6. (Optional) Job Description is compared with resume
7. User can download a detailed ATS report as PDF

---

## 🛠️ Tech Stack

- **Backend**: Django 4.x
- **Frontend**: HTML, CSS (Django Templates)
- **PDF Generation**: ReportLab
- **Database**: SQLite (default)
- **Authentication**: Django Auth
- **Language**: Python 3.10+

---

## 📂 Project Structure

