# ⚡ ChallengeHire
### AI-Based Job Recruitment Management System with Real-World Challenge Assessment

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-black.svg)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/Database-MySQL%20%7C%20SQLite-orange.svg)](https://www.mysql.com/)
[![AI-Powered](https://img.shields.io/badge/AI-Skill%20Matching%20%26%20Rubrics-purple.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()

---

## 📌 1. Project Overview

**ChallengeHire** is a modern, full-stack recruitment platform designed to eliminate the flaws of traditional resume-screening. Instead of relying on keyword-stuffed CVs, companies recruit candidates based on **practical skills, repository deliverables, live previews, and automated rubric assessments**.

### 🌟 Core Value Proposition:
- **For Students & Candidates**: Build a verified proof-of-work portfolio. Tackle authentic coding tasks (database schemas, REST APIs, responsive UIs), receive transparent AI-assisted rubric feedback, identify skill gaps for dream jobs, and get directly shortlisted by engineering teams.
- **For Recruiters & Hiring Managers**: Eliminate resume spam. Review GitHub repositories, live demo deployments, automated rubric scores, and compare candidates side-by-side using multi-dimensional radar charts.

---

## 🏗️ 2. Technology Stack & Architecture

| Layer | Technologies Used |
| :--- | :--- |
| **Frontend** | HTML5 (Semantic), Modern CSS3 (CSS Variables, Flexbox/Grid, Dark Navy `#0f172a` & Purple `#7c3aed`), Vanilla JavaScript (ES6+), Chart.js (Radar & Funnel Charts) |
| **Backend** | Python Flask (Blueprints architecture, Jinja2 templating, secure session management, role-based decorators) |
| **Database** | **MySQL** (Primary relational DBMS, 3NF normalized schema, foreign keys, indexes, CASCADE triggers) + Automated **SQLite** fallback for frictionless zero-config local testing |
| **AI Engine** | Python-based Weighted Skill Similarity Matcher, Challenge & Career Path Recommender, Heuristic Rubric Evaluator, and optional Google Gemini 1.5 API integration |
| **Security** | Werkzeug password hashing (Scrypt/PBKDF2), SQL injection prevention via parameterized ORM queries, role-based route guards, duplicate application constraints |

---

## 🗄️ 3. Relational Database Design (18 Tables in 3NF)

The database schema is strictly normalized and enforces referential integrity:

```mermaid
erDiagram
    USERS ||--o| STUDENT_PROFILES : has
    USERS ||--o| RECRUITER_PROFILES : has
    USERS ||--o{ NOTIFICATIONS : receives
    COMPANIES ||--o{ RECRUITER_PROFILES : employs
    COMPANIES ||--o{ JOBS : offers
    RECRUITER_PROFILES ||--o{ JOBS : posts
    RECRUITER_PROFILES ||--o{ CHALLENGES : creates
    JOBS ||--o{ JOB_REQUIRED_SKILLS : requires
    SKILLS ||--o{ JOB_REQUIRED_SKILLS : categorized_in
    SKILLS ||--o{ STUDENT_SKILLS : possessed_by
    STUDENT_PROFILES ||--o{ STUDENT_SKILLS : masters
    CHALLENGES ||--o{ CHALLENGE_REQUIRED_SKILLS : tests
    SKILLS ||--o{ CHALLENGE_REQUIRED_SKILLS : verified_in
    STUDENT_PROFILES ||--o{ APPLICATIONS : submits
    JOBS ||--o{ APPLICATIONS : receives
    STUDENT_PROFILES ||--o{ SUBMISSIONS : builds
    CHALLENGES ||--o{ SUBMISSIONS : answers
    SUBMISSIONS ||--o| EVALUATION_RESULTS : scored_in
    CHALLENGES ||--o{ ASSESSMENTS : includes
    ASSESSMENTS ||--o{ QUESTIONS : contains
    STUDENT_PROFILES ||--o{ ASSESSMENT_ATTEMPTS : attempts
    ASSESSMENTS ||--o{ ASSESSMENT_ATTEMPTS : records
    RECRUITER_PROFILES ||--o{ RECRUITER_REVIEWS : writes
    STUDENT_PROFILES ||--o{ RECRUITER_REVIEWS : reviewed_in
    STUDENT_PROFILES ||--o{ AI_RECOMMENDATIONS : guided_by
```

### Table Catalog:
1. `users`: Core authentication table with email, password hash, role (`student`, `recruiter`, `admin`), active status.
2. `companies`: Partner technology companies, logo URL, location, and industry domain.
3. `student_profiles`: Candidate credentials, college/university, graduation year, degree, portfolio & GitHub links.
4. `recruiter_profiles`: Recruiter identity, official corporate email, designation, phone, linked company.
5. `skills`: Normalized skill taxonomy categorized by backend, frontend, database, devops, and AI/ML.
6. `student_skills`: Many-to-many relationship tracking proficiency levels and verified status.
7. `jobs`: Active recruitment openings, experience level, salary range, remote flag, and associated practical challenge.
8. `job_required_skills`: Weighted skill requirements marked as mandatory or optional.
9. `challenges`: Practical coding challenges with problem statement, instructions, max score, time limit, and rubric criteria.
10. `challenge_required_skills`: Technologies evaluated by each practical challenge.
11. `applications`: Candidate job applications with unique constraint `UNIQUE(job_id, student_id)` to prevent duplicates, and status tracking (`Applied`, `Assessment Pending`, `Under Review`, `Shortlisted`, `Selected`, `Rejected`).
12. `submissions`: Candidate challenge submissions with GitHub repository URL, live deployment URL, project archive file, and technical approach writeup.
13. `assessments`: Objective tests linked to practical challenges.
14. `questions`: Multiple-choice and coding questions with points.
15. `assessment_attempts`: Quiz scores and pass/fail records.
16. `evaluation_results`: Multi-point rubric breakdowns (Code Quality /30, Functionality /40, UI/UX /30), total score, AI notes, and recruiter comments.
17. `ai_recommendations`: Intelligent challenge and job suggestions with explainable rationales.
18. `recruiter_reviews`: Formal recruiter interview decisions, 1-5 star ratings, and review notes.
19. `notifications`: Real-time user notification events with unread tracking.

---

## 🤖 4. AI Engine Features

### A. Skill Matching & Job Fit Calculation
- Compares student verified/declared competencies with job requirements.
- Employs weighted scoring: mandatory skills carry higher multipliers; verified challenge badges award verification bonuses.
- Returns clear percentage (0-100%), fit category (`Strong Match`, `Moderate Fit`, `High Skill Gap`), and lists matched vs. missing skills.

### B. AI Challenge & Job Recommendation
- Analyzes candidate skill graphs and previous submission scores.
- Recommends challenges targeting the candidate's "sweet spot" (re-enforcing known tools while learning 1-2 new skills).
- Recommends challenges that specifically resolve skill gaps for jobs the student wants to apply for.

### C. Automated Submission Rubric Evaluation
- Inspects repository deliverables, live demo URL validity, and structural technical keywords in the candidate's explanation.
- Computes fair, deterministic scores across Code Architecture (/30), Functionality (/40), and UI/UX & Documentation (/30).
- If `GEMINI_API_KEY` is provided in `.env`, connects to Google Gemini for deep natural language technical feedback.
- If no API key is present, falls back gracefully to the rule-based heuristic rubric.

### D. Skill Gap Action Planner
- Identifies missing skills for any target opening.
- Dynamically queries available practical challenges that teach and test those missing skills, giving students a 1-click roadmap to bridge the gap.

### E. Recruiter Candidate Comparison Engine
- Renders an interactive Chart.js Radar Chart comparing 2 to 3 applicants across 5 axes:
  `Skill Match`, `Challenge Score`, `Code Quality`, `Functionality`, `Project Evidence`.
- Provides explainable comparative takeaways highlighting standout candidates.

---

## 🚀 5. Installation & Execution Guide

### Option 1: Quickstart (Zero Configuration with SQLite Fallback)
The application comes pre-configured to run out of the box using an automated SQLite fallback if MySQL is not currently running.

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/ChallengeHire.git
   cd ChallengeHire
   ```

2. **Create and activate a virtual environment**:
   ```bash
   # Windows (PowerShell) 
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python run.py
   ```
   Open your browser to: **http://127.0.0.1:5000**

---

### Option 2: Setup with MySQL Database (Production & DBMS Submission)

1. **Start your MySQL server** (e.g., MySQL Workbench, XAMPP, or Docker).
2. **Execute the SQL schema & seed scripts**:
   ```bash
   mysql -u root -p < database/schema.sql
   mysql -u root -p < database/seed_data.sql
   ```
3. **Configure your `.env` file**:
   ```env
   SECRET_KEY=dev-challengehire-secret-key-2025
   DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/challengehire_db
   USE_SQLITE_FALLBACK=false
   GEMINI_API_KEY=your_optional_gemini_api_key_here
   ```
4. **Launch ChallengeHire**:
   ```bash
   python run.py
   ```

---

## 🔑 6. Pre-Seeded Demonstration Accounts

For effortless evaluation, the database includes pre-seeded accounts. Every account has the default password: **`password123`**

| Role | Name | Email | Features to Test |
| :--- | :--- | :--- | :--- |
| **Student** | Alex Rivera | `alex.rivera@student.edu` | Full-stack profile, 94/100 challenge submission, applied jobs tracker, AI recommendations |
| **Student** | Samantha Chen | `samantha.chen@student.edu` | Frontend UI profile, 92/100 responsive job board challenge, portfolio links |
| **Recruiter** | Sarah Jenkins | `sarah.jenkins@nexatech.com` | NexaTech hiring lead: review submissions, grade rubrics, update candidate status, compare candidates |
| **Recruiter** | Marcus Vance | `marcus.vance@pulseai.io` | PulseAI director: post new openings, create AI challenges |

> **Pro Tip**: Use the **"1-Click Fill"** buttons on the [Login Page](http://127.0.0.1:5000/login) to log into any test account instantly.

---

## 🧪 7. Running Automated Test Cases

The test suite validates authentication, role-based protection, database integrity, duplicate application prevention, and AI matching:

```bash
python -m unittest tests/test_challengehire.py
```

---

## 🌐 8. Adding into GitHub for Live Demo

To publish this project to GitHub and deploy a live demo:

### Step 1: Initialize Git & Commit Code
```bash
git init
git add .
git commit -m "Initial commit: Complete ChallengeHire Full-Stack Platform"
```

### Step 2: Push to Your GitHub Repository
```bash
git branch -M main
git remote add origin https://github.com/<your-github-username>/ChallengeHire.git
git push -u origin main
```

### Step 3: Deploy Free Live Demo (Render / Railway / PythonAnywhere)
1. **On Render (Recommended)**:
   - Go to [render.com](https://render.com) and create a **New Web Service**.
   - Connect your GitHub repository `ChallengeHire`.
   - Set **Build Command**: `pip install -r requirements.txt`
   - Set **Start Command**: `python run.py` (or `gunicorn app:app`)
   - Add environment variable `PORT=5000`.
   - Your live URL will be active within minutes!

---

## 📄 9. Project Deliverables Checklist

- [x] Full-stack Python Flask backend with blueprints (`main`, `auth`, `student`, `recruiter`, `api`)
- [x] Normalized 3NF MySQL relational database schema (`database/schema.sql`)
- [x] Realistic seed dataset with 6 jobs, 5 challenges, 6 users, submissions, and rubric evaluations (`database/seed_data.sql`)
- [x] AI Skill Matching, Challenge Recommendation, Heuristic Rubric Scoring, and Gap Analysis (`ai/`)
- [x] Recruiter Candidate Comparison with interactive Radar Chart
- [x] Premium dark navy & purple responsive UI with clean cards, badges, and modals
- [x] Automated test cases (`tests/test_challengehire.py`)
- [x] Zero-friction SQLite fallback for local running out-of-the-box

---
*Built with passion for meritocratic, practical engineering recruitment.*
