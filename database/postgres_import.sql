-- ========================================================
-- ChallengeHire - PostgreSQL Relational Database Schema & Seed Data
-- Compatible with Render PostgreSQL, Supabase, Neon, Railway Postgres, etc.
-- ========================================================

-- Safely drop existing tables with cascade
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS recruiter_reviews CASCADE;
DROP TABLE IF EXISTS ai_recommendations CASCADE;
DROP TABLE IF EXISTS evaluation_results CASCADE;
DROP TABLE IF EXISTS assessment_attempts CASCADE;
DROP TABLE IF EXISTS questions CASCADE;
DROP TABLE IF EXISTS assessments CASCADE;
DROP TABLE IF EXISTS submissions CASCADE;
DROP TABLE IF EXISTS applications CASCADE;
DROP TABLE IF EXISTS challenge_required_skills CASCADE;
DROP TABLE IF EXISTS challenges CASCADE;
DROP TABLE IF EXISTS job_required_skills CASCADE;
DROP TABLE IF EXISTS jobs CASCADE;
DROP TABLE IF EXISTS student_skills CASCADE;
DROP TABLE IF EXISTS skills CASCADE;
DROP TABLE IF EXISTS recruiter_profiles CASCADE;
DROP TABLE IF EXISTS student_profiles CASCADE;
DROP TABLE IF EXISTS companies CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- 1. Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(191) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'student' CHECK (role IN ('student', 'recruiter', 'admin')),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_user_role ON users(role);

-- 2. Companies Table
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    website VARCHAR(255),
    description TEXT,
    logo_url VARCHAR(255),
    location VARCHAR(255) NOT NULL,
    industry VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_company_name ON companies(name);

-- 3. Student Profiles Table
CREATE TABLE student_profiles (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    full_name VARCHAR(150) NOT NULL,
    college_name VARCHAR(255) NOT NULL,
    graduation_year INT,
    degree VARCHAR(100),
    bio TEXT,
    github_url VARCHAR(255),
    portfolio_url VARCHAR(255),
    linkedin_url VARCHAR(255),
    resume_filename VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_student_name ON student_profiles(full_name);
CREATE INDEX idx_student_college ON student_profiles(college_name);

-- 4. Recruiter Profiles Table
CREATE TABLE recruiter_profiles (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    company_id INT NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    full_name VARCHAR(150) NOT NULL,
    official_email VARCHAR(191) NOT NULL,
    designation VARCHAR(100) NOT NULL,
    phone VARCHAR(30),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_recruiter_name ON recruiter_profiles(full_name);

-- 5. Skills Table
CREATE TABLE skills (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50) NOT NULL DEFAULT 'general' CHECK (category IN ('frontend', 'backend', 'database', 'devops', 'ai_ml', 'mobile', 'general'))
);
CREATE INDEX idx_skill_name ON skills(name);
CREATE INDEX idx_skill_category ON skills(category);

-- 6. Student Skills Table
CREATE TABLE student_skills (
    id SERIAL PRIMARY KEY,
    student_id INT NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    skill_id INT NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    proficiency_level VARCHAR(20) NOT NULL DEFAULT 'intermediate' CHECK (proficiency_level IN ('beginner', 'intermediate', 'advanced')),
    verified BOOLEAN NOT NULL DEFAULT FALSE,
    score_earned INT DEFAULT 0,
    CONSTRAINT uq_student_skill UNIQUE (student_id, skill_id)
);

-- 7. Challenges Table
CREATE TABLE challenges (
    id SERIAL PRIMARY KEY,
    recruiter_id INT REFERENCES recruiter_profiles(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    problem_statement TEXT NOT NULL,
    instructions TEXT NOT NULL,
    difficulty_level VARCHAR(20) NOT NULL DEFAULT 'intermediate' CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),
    max_score INT NOT NULL DEFAULT 100,
    time_limit_minutes INT DEFAULT 180,
    submission_deadline TIMESTAMP,
    evaluation_criteria TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived', 'draft')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_challenge_difficulty ON challenges(difficulty_level);
CREATE INDEX idx_challenge_status ON challenges(status);

-- 8. Challenge Required Skills Table
CREATE TABLE challenge_required_skills (
    id SERIAL PRIMARY KEY,
    challenge_id INT NOT NULL REFERENCES challenges(id) ON DELETE CASCADE,
    skill_id INT NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    CONSTRAINT uq_challenge_skill UNIQUE (challenge_id, skill_id)
);

-- 9. Jobs Table
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    recruiter_id INT NOT NULL REFERENCES recruiter_profiles(id) ON DELETE CASCADE,
    company_id INT NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    experience_level VARCHAR(20) NOT NULL DEFAULT 'entry' CHECK (experience_level IN ('entry', 'mid', 'senior')),
    employment_type VARCHAR(20) NOT NULL DEFAULT 'full_time' CHECK (employment_type IN ('full_time', 'internship', 'part_time', 'contract')),
    location VARCHAR(150) NOT NULL,
    is_remote BOOLEAN NOT NULL DEFAULT FALSE,
    salary_min NUMERIC(12, 2),
    salary_max NUMERIC(12, 2),
    currency VARCHAR(10) DEFAULT 'USD',
    deadline DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'closed', 'draft')),
    associated_challenge_id INT REFERENCES challenges(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_job_status ON jobs(status);
CREATE INDEX idx_job_exp ON jobs(experience_level);
CREATE INDEX idx_job_remote ON jobs(is_remote);

-- 10. Job Required Skills Table
CREATE TABLE job_required_skills (
    id SERIAL PRIMARY KEY,
    job_id INT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    skill_id INT NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    is_mandatory BOOLEAN NOT NULL DEFAULT TRUE,
    weight INT NOT NULL DEFAULT 1,
    CONSTRAINT uq_job_skill UNIQUE (job_id, skill_id)
);

-- 11. Applications Table
CREATE TABLE applications (
    id SERIAL PRIMARY KEY,
    job_id INT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    student_id INT NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    status VARCHAR(30) NOT NULL DEFAULT 'Applied' CHECK (status IN ('Applied', 'Assessment Pending', 'Under Review', 'Shortlisted', 'Rejected', 'Selected')),
    cover_letter TEXT,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_job_student UNIQUE (job_id, student_id)
);
CREATE INDEX idx_app_status ON applications(status);

-- 12. Submissions Table
CREATE TABLE submissions (
    id SERIAL PRIMARY KEY,
    challenge_id INT NOT NULL REFERENCES challenges(id) ON DELETE CASCADE,
    student_id INT NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    application_id INT REFERENCES applications(id) ON DELETE SET NULL,
    github_repo_url VARCHAR(255),
    live_demo_url VARCHAR(255),
    project_file VARCHAR(255),
    explanation TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'submitted' CHECK (status IN ('submitted', 'evaluating', 'evaluated')),
    score INT DEFAULT 0,
    feedback TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_sub_status ON submissions(status);

-- 13. Assessments Table
CREATE TABLE assessments (
    id SERIAL PRIMARY KEY,
    challenge_id INT REFERENCES challenges(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    pass_percentage INT NOT NULL DEFAULT 60,
    duration_minutes INT NOT NULL DEFAULT 30,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 14. Questions Table
CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    assessment_id INT NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    question_type VARCHAR(20) NOT NULL DEFAULT 'mcq' CHECK (question_type IN ('mcq', 'code_snippet', 'short_answer')),
    options_json TEXT,
    correct_answer TEXT NOT NULL,
    points INT NOT NULL DEFAULT 10
);

-- 15. Assessment Attempts Table
CREATE TABLE assessment_attempts (
    id SERIAL PRIMARY KEY,
    assessment_id INT NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    student_id INT NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    score INT NOT NULL DEFAULT 0,
    max_score INT NOT NULL DEFAULT 100,
    passed BOOLEAN NOT NULL DEFAULT FALSE,
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 16. Evaluation Results Table
CREATE TABLE evaluation_results (
    id SERIAL PRIMARY KEY,
    submission_id INT NOT NULL UNIQUE REFERENCES submissions(id) ON DELETE CASCADE,
    code_quality_score INT NOT NULL DEFAULT 0,
    functionality_score INT NOT NULL DEFAULT 0,
    ui_ux_score INT NOT NULL DEFAULT 0,
    total_score INT NOT NULL DEFAULT 0,
    max_score INT NOT NULL DEFAULT 100,
    ai_suggested_score INT,
    ai_feedback TEXT,
    recruiter_comments TEXT,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 17. AI Recommendations Table
CREATE TABLE ai_recommendations (
    id SERIAL PRIMARY KEY,
    student_id INT NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    recommendation_type VARCHAR(20) NOT NULL CHECK (recommendation_type IN ('challenge', 'skill_gap', 'job')),
    target_id INT NOT NULL,
    score_or_fit FLOAT NOT NULL DEFAULT 0.0,
    rationale TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_air_type ON ai_recommendations(recommendation_type);

-- 18. Recruiter Reviews Table
CREATE TABLE recruiter_reviews (
    id SERIAL PRIMARY KEY,
    recruiter_id INT NOT NULL REFERENCES recruiter_profiles(id) ON DELETE CASCADE,
    student_id INT NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    application_id INT REFERENCES applications(id) ON DELETE SET NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review_notes TEXT NOT NULL,
    decision VARCHAR(20) NOT NULL DEFAULT 'further_review' CHECK (decision IN ('shortlist', 'reject', 'hire', 'further_review')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 19. Notifications Table
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    link VARCHAR(255),
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_notif_user_read ON notifications(user_id, is_read);

-- ========================================================
-- INSERT SEED DATA FOR POSTGRESQL
-- ========================================================

-- Skills
INSERT INTO skills (name, category) VALUES
('Python', 'backend'), ('Flask', 'backend'), ('Django', 'backend'),
('JavaScript', 'frontend'), ('React', 'frontend'), ('HTML5', 'frontend'),
('CSS3', 'frontend'), ('Node.js', 'backend'), ('MySQL', 'database'),
('PostgreSQL', 'database'), ('REST APIs', 'backend'), ('Docker', 'devops'),
('Git', 'devops'), ('Machine Learning', 'ai_ml'), ('TensorFlow', 'ai_ml'),
('AWS', 'devops'), ('UI/UX Design', 'frontend'), ('Cybersecurity', 'backend');

-- Users (Password: password123)
INSERT INTO users (id, email, password_hash, role, is_active) VALUES
(1, 'sarah.jenkins@nexatech.com', 'scrypt:32768:8:1$7tS5v8lG8g6DfgkL$a6ee71f28876c1fe6a1a45ce3766eb51dcfebda9cf41d8eeb545ff033878b46571542f7c02b545d134b2fa7fe01f2be52ad39ecfc463eefce7c688d0b2fbb1c3', 'recruiter', TRUE),
(2, 'marcus.vance@pulseai.io', 'scrypt:32768:8:1$7tS5v8lG8g6DfgkL$a6ee71f28876c1fe6a1a45ce3766eb51dcfebda9cf41d8eeb545ff033878b46571542f7c02b545d134b2fa7fe01f2be52ad39ecfc463eefce7c688d0b2fbb1c3', 'recruiter', TRUE),
(3, 'priya.sharma@quantumpay.com', 'scrypt:32768:8:1$7tS5v8lG8g6DfgkL$a6ee71f28876c1fe6a1a45ce3766eb51dcfebda9cf41d8eeb545ff033878b46571542f7c02b545d134b2fa7fe01f2be52ad39ecfc463eefce7c688d0b2fbb1c3', 'recruiter', TRUE),
(4, 'alex.rivera@student.edu', 'scrypt:32768:8:1$7tS5v8lG8g6DfgkL$a6ee71f28876c1fe6a1a45ce3766eb51dcfebda9cf41d8eeb545ff033878b46571542f7c02b545d134b2fa7fe01f2be52ad39ecfc463eefce7c688d0b2fbb1c3', 'student', TRUE),
(5, 'samantha.chen@student.edu', 'scrypt:32768:8:1$7tS5v8lG8g6DfgkL$a6ee71f28876c1fe6a1a45ce3766eb51dcfebda9cf41d8eeb545ff033878b46571542f7c02b545d134b2fa7fe01f2be52ad39ecfc463eefce7c688d0b2fbb1c3', 'student', TRUE),
(6, 'david.oconnor@student.edu', 'scrypt:32768:8:1$7tS5v8lG8g6DfgkL$a6ee71f28876c1fe6a1a45ce3766eb51dcfebda9cf41d8eeb545ff033878b46571542f7c02b545d134b2fa7fe01f2be52ad39ecfc463eefce7c688d0b2fbb1c3', 'student', TRUE);

-- Advance sequence for users
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));

-- Companies
INSERT INTO companies (id, name, website, description, logo_url, location, industry) VALUES
(1, 'NexaTech Solutions', 'https://nexatech.example.com', 'Cloud enterprise software.', '/static/img/company1.png', 'San Francisco, CA / Remote', 'Cloud & SaaS'),
(2, 'PulseAI Innovations', 'https://pulseai.example.io', 'Next-gen AI agents.', '/static/img/company2.png', 'New York, NY / Hybrid', 'Artificial Intelligence'),
(3, 'QuantumPay FinTech', 'https://quantumpay.example.com', 'Cross-border payment infrastructure.', '/static/img/company3.png', 'London, UK / Remote', 'Financial Technology');

SELECT setval('companies_id_seq', (SELECT MAX(id) FROM companies));

-- Recruiter Profiles
INSERT INTO recruiter_profiles (id, user_id, company_id, full_name, official_email, designation, phone) VALUES
(1, 1, 1, 'Sarah Jenkins', 'sarah.jenkins@nexatech.com', 'Lead Talent Partner', '+1-415-555-0192'),
(2, 2, 2, 'Marcus Vance', 'marcus.vance@pulseai.io', 'Director of Recruitment', '+1-212-555-0143'),
(3, 3, 3, 'Priya Sharma', 'priya.sharma@quantumpay.com', 'Senior Recruiter', '+44-20-7946-0912');

SELECT setval('recruiter_profiles_id_seq', (SELECT MAX(id) FROM recruiter_profiles));

-- Student Profiles
INSERT INTO student_profiles (id, user_id, full_name, college_name, graduation_year, degree, bio, github_url, portfolio_url) VALUES
(1, 4, 'Alex Rivera', 'Stanford University', 2025, 'B.S. Computer Science', 'Full-stack software developer.', 'https://github.com/alexrivera-demo', 'https://alexrivera.dev'),
(2, 5, 'Samantha Chen', 'UC Berkeley', 2025, 'B.S. EECS', 'Frontend developer focused on UI/UX.', 'https://github.com/samchen-code', 'https://samchen.design'),
(3, 6, 'David O Connor', 'Georgia Tech', 2024, 'M.S. Computer Science', 'Backend database systems engineer.', 'https://github.com/davidoc-tech', 'https://davidoconnor.io');

SELECT setval('student_profiles_id_seq', (SELECT MAX(id) FROM student_profiles));

-- Student Skills
INSERT INTO student_skills (student_id, skill_id, proficiency_level, verified, score_earned) VALUES
(1, 1, 'advanced', TRUE, 92), (1, 2, 'advanced', TRUE, 88), (1, 4, 'intermediate', TRUE, 85),
(1, 6, 'advanced', TRUE, 90), (1, 7, 'advanced', TRUE, 90), (1, 9, 'advanced', TRUE, 87), (1, 11, 'advanced', TRUE, 91),
(2, 4, 'advanced', TRUE, 95), (2, 5, 'advanced', TRUE, 94), (2, 6, 'advanced', TRUE, 96), (2, 7, 'advanced', TRUE, 95), (2, 17, 'advanced', TRUE, 92),
(3, 1, 'advanced', TRUE, 94), (3, 9, 'advanced', TRUE, 95), (3, 10, 'advanced', TRUE, 90), (3, 12, 'intermediate', TRUE, 82), (3, 13, 'advanced', TRUE, 89);

-- Challenges
INSERT INTO challenges (id, recruiter_id, title, problem_statement, instructions, difficulty_level, max_score, evaluation_criteria, status, submission_deadline) VALUES
(1, 1, 'Full-Stack Student Attendance & Portal System', 'Build an attendance tracker with relational database.', 'Implement normalized tables and REST APIs.', 'intermediate', 100, 'Architecture (30%), Queries (30%), UI (20%), Docs (20%)', 'active', CURRENT_TIMESTAMP + INTERVAL '14 days'),
(2, 2, 'AI Skill Matcher & Recommendation Engine', 'Extract skills and compute similarity against jobs.', 'Expose /match-skills endpoint with explainable breakdown.', 'advanced', 100, 'Accuracy (35%), API (35%), Tests (15%), Docs (15%)', 'active', CURRENT_TIMESTAMP + INTERVAL '21 days'),
(3, 3, 'High-Throughput Payment Ledger', 'Double-entry transaction processing service.', 'Guarantee ACID safety and prevent negative balances.', 'advanced', 100, 'ACID Safety (40%), Error Handling (30%), Clean Code (30%)', 'active', CURRENT_TIMESTAMP + INTERVAL '10 days'),
(4, 1, 'Modern Responsive Job Board Frontend', 'Build accessible responsive job catalog UI.', 'Semantic HTML5, CSS Grid/Flexbox, Vanilla JS.', 'beginner', 100, 'Polish (35%), Responsiveness (35%), Filtering (30%)', 'active', CURRENT_TIMESTAMP + INTERVAL '18 days'),
(5, 2, 'Automated CI/CD Pipeline & Docker', 'Containerize a Flask + MySQL app.', 'Write Dockerfile and compose with healthchecks.', 'intermediate', 100, 'Docker Security (35%), Compose (35%), CI/CD (30%)', 'active', CURRENT_TIMESTAMP + INTERVAL '15 days');

SELECT setval('challenges_id_seq', (SELECT MAX(id) FROM challenges));

-- Challenge Skills
INSERT INTO challenge_required_skills (challenge_id, skill_id) VALUES
(1, 1), (1, 2), (1, 6), (1, 7), (1, 9),
(2, 1), (2, 2), (2, 11), (2, 14),
(3, 1), (3, 9), (3, 10), (3, 18),
(4, 4), (4, 6), (4, 7), (4, 17),
(5, 12), (5, 13), (5, 1), (5, 9);

-- Jobs
INSERT INTO jobs (id, recruiter_id, company_id, title, description, experience_level, employment_type, location, is_remote, salary_min, salary_max, status, associated_challenge_id, deadline) VALUES
(1, 1, 1, 'Junior Full-Stack Web Developer', 'Build cloud applications and APIs.', 'entry', 'full_time', 'San Francisco, CA', TRUE, 78000, 98000, 'active', 1, CURRENT_DATE + INTERVAL '30 days'),
(2, 2, 2, 'Backend Python & AI Integration Engineer', 'Connect LLMs with relational database pipelines.', 'mid', 'full_time', 'New York, NY', FALSE, 95000, 125000, 'active', 2, CURRENT_DATE + INTERVAL '25 days'),
(3, 3, 3, 'FinTech Backend API & Systems Engineer', 'ACID-compliant transaction systems.', 'mid', 'full_time', 'London, UK', TRUE, 90000, 115000, 'active', 3, CURRENT_DATE + INTERVAL '20 days'),
(4, 1, 1, 'Frontend UI/UX Web Engineer', 'Fast responsive web experiences.', 'entry', 'full_time', 'San Francisco, CA', TRUE, 72000, 90000, 'active', 4, CURRENT_DATE + INTERVAL '28 days'),
(5, 2, 2, 'AI & Machine Learning Engineering Intern', 'Recommendation algorithms and NLP.', 'entry', 'internship', 'New York, NY', TRUE, 45000, 60000, 'active', 2, CURRENT_DATE + INTERVAL '35 days'),
(6, 1, 1, 'Cloud Infrastructure & DevOps Engineer', 'Manage Kubernetes and Docker deployments.', 'mid', 'full_time', 'Austin, TX', FALSE, 105000, 135000, 'active', 5, CURRENT_DATE + INTERVAL '40 days');

SELECT setval('jobs_id_seq', (SELECT MAX(id) FROM jobs));

-- Job Required Skills
INSERT INTO job_required_skills (job_id, skill_id, is_mandatory, weight) VALUES
(1, 1, TRUE, 3), (1, 2, TRUE, 3), (1, 4, TRUE, 2), (1, 9, TRUE, 3),
(2, 1, TRUE, 3), (2, 11, TRUE, 3), (2, 14, TRUE, 2), (2, 9, TRUE, 2),
(3, 1, TRUE, 3), (3, 9, TRUE, 3), (3, 10, TRUE, 2), (3, 18, TRUE, 2),
(4, 4, TRUE, 3), (4, 6, TRUE, 3), (4, 7, TRUE, 3), (4, 17, TRUE, 2),
(5, 1, TRUE, 3), (5, 14, TRUE, 3), (5, 15, FALSE, 2),
(6, 12, TRUE, 3), (6, 13, TRUE, 2), (6, 16, TRUE, 3);

-- Applications
INSERT INTO applications (id, job_id, student_id, status, cover_letter, applied_at) VALUES
(1, 1, 1, 'Shortlisted', 'Strong background in Flask and relational database design.', CURRENT_TIMESTAMP - INTERVAL '5 days'),
(2, 4, 2, 'Under Review', 'Specialized in responsive vanilla JS interfaces.', CURRENT_TIMESTAMP - INTERVAL '3 days'),
(3, 2, 3, 'Assessment Pending', 'Experienced with PostgreSQL and scalable services.', CURRENT_TIMESTAMP - INTERVAL '2 days'),
(4, 2, 1, 'Applied', 'Passionate about intelligent recommendation algorithms.', CURRENT_TIMESTAMP - INTERVAL '1 day');

SELECT setval('applications_id_seq', (SELECT MAX(id) FROM applications));

-- Submissions
INSERT INTO submissions (id, challenge_id, student_id, application_id, github_repo_url, live_demo_url, project_file, explanation, status, score, feedback, submitted_at) VALUES
(1, 1, 1, 1, 'https://github.com/alexrivera-demo/challengehire-attendance-portal', 'https://attendance-demo.alexrivera.dev', 'alex_attendance_v1.zip',
'Normalized 3NF relational database with REST endpoints and unit tests.', 'evaluated', 94, 'Outstanding code quality and normalized schema.', CURRENT_TIMESTAMP - INTERVAL '4 days'),
(2, 4, 2, 2, 'https://github.com/samchen-code/challengehire-responsive-job-board', 'https://jobs-demo.samchen.design', 'sam_jobboard_ui.zip',
'Clean accessible job board using CSS Grid and JS.', 'evaluated', 92, 'Excellent design sensibility and typography.', CURRENT_TIMESTAMP - INTERVAL '2 days');

SELECT setval('submissions_id_seq', (SELECT MAX(id) FROM submissions));

-- Evaluation Results
INSERT INTO evaluation_results (id, submission_id, code_quality_score, functionality_score, ui_ux_score, total_score, max_score, ai_suggested_score, ai_feedback, recruiter_comments) VALUES
(1, 1, 29, 38, 27, 94, 100, 92, 'AI Assessment: Clean MVC design and 3NF schema adherence.', 'Shortlisted for technical round.'),
(2, 2, 28, 36, 28, 92, 100, 90, 'AI Assessment: Semantic accessible HTML and responsive CSS.', 'Shortlisted for engineering review.');

SELECT setval('evaluation_results_id_seq', (SELECT MAX(id) FROM evaluation_results));

-- Assessments & Questions
INSERT INTO assessments (id, challenge_id, title, description, pass_percentage, duration_minutes) VALUES
(1, 1, 'Web & Database Engineering Fundamentals', 'Verifies knowledge of SQL joins, HTTP methods, session management, and MVC architecture.', 60, 20);

SELECT setval('assessments_id_seq', (SELECT MAX(id) FROM assessments));

INSERT INTO questions (assessment_id, question_text, question_type, options_json, correct_answer, points) VALUES
(1, 'Which SQL constraint guarantees that values in a column are all unique across records and cannot be NULL?', 'mcq', '["FOREIGN KEY", "PRIMARY KEY", "CHECK", "INDEX"]', 'PRIMARY KEY', 10),
(1, 'In REST API design, which HTTP method should be idempotent and used to retrieve representation of a resource?', 'mcq', '["POST", "GET", "PATCH", "DELETE"]', 'GET', 10),
(1, 'What is the main purpose of database indexing?', 'mcq', '["Encrypt sensitive data", "Speed up data retrieval operations", "Enforce business logic", "Backup tables automatically"]', 'Speed up data retrieval operations', 10);

-- Recruiter Reviews
INSERT INTO recruiter_reviews (recruiter_id, student_id, application_id, rating, review_notes, decision) VALUES
(1, 1, 1, 5, 'Alex demonstrated mastery in relational schema design and practical Flask implementation. Submission passed all criteria.', 'shortlist'),
(1, 2, 2, 5, 'Samantha has top-tier UI design sensibility and clean coding style. Passed to team lead.', 'shortlist');

-- Notifications
INSERT INTO notifications (user_id, title, message, link, is_read) VALUES
(4, 'Challenge Evaluated!', 'Your submission for "Full-Stack Student Attendance & Portal System" was graded 94/100 by Sarah Jenkins.', '/student/submissions', FALSE),
(4, 'Application Shortlisted', 'Congratulations! NexaTech Solutions has updated your application status to Shortlisted.', '/student/applications', FALSE),
(1, 'New Application Received', 'Alex Rivera applied for Junior Full-Stack Web Developer.', '/recruiter/applicants', TRUE);
