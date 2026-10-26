-- ========================================================
-- ChallengeHire - Unified Cloud MySQL Import Script
-- Works on ANY Online MySQL Host (TiDB, Aiven, Railway, etc.)
-- Creates all 18 normalized tables and populates sample data
-- ========================================================

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS recruiter_reviews;
DROP TABLE IF EXISTS ai_recommendations;
DROP TABLE IF EXISTS evaluation_results;
DROP TABLE IF EXISTS assessment_attempts;
DROP TABLE IF EXISTS questions;
DROP TABLE IF EXISTS assessments;
DROP TABLE IF EXISTS submissions;
DROP TABLE IF EXISTS applications;
DROP TABLE IF EXISTS challenge_required_skills;
DROP TABLE IF EXISTS challenges;
DROP TABLE IF EXISTS job_required_skills;
DROP TABLE IF EXISTS jobs;
DROP TABLE IF EXISTS student_skills;
DROP TABLE IF EXISTS skills;
DROP TABLE IF EXISTS recruiter_profiles;
DROP TABLE IF EXISTS student_profiles;
DROP TABLE IF EXISTS companies;
DROP TABLE IF EXISTS users;

SET FOREIGN_KEY_CHECKS = 1;

-- 1. Users Table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(191) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('student', 'recruiter', 'admin') NOT NULL DEFAULT 'student',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_email (email),
    INDEX idx_user_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Companies Table
CREATE TABLE companies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    website VARCHAR(255),
    description TEXT,
    logo_url VARCHAR(255),
    location VARCHAR(255) NOT NULL,
    industry VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_company_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Student Profiles Table
CREATE TABLE student_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
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
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_student_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_student_name (full_name),
    INDEX idx_student_college (college_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Recruiter Profiles Table
CREATE TABLE recruiter_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    company_id INT NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    official_email VARCHAR(191) NOT NULL,
    designation VARCHAR(100) NOT NULL,
    phone VARCHAR(30),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_recruiter_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_recruiter_company FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    INDEX idx_recruiter_name (full_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Skills Table
CREATE TABLE skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    category ENUM('frontend', 'backend', 'database', 'devops', 'ai_ml', 'mobile', 'general') NOT NULL DEFAULT 'general',
    INDEX idx_skill_name (name),
    INDEX idx_skill_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Student Skills Table
CREATE TABLE student_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    skill_id INT NOT NULL,
    proficiency_level ENUM('beginner', 'intermediate', 'advanced') NOT NULL DEFAULT 'intermediate',
    verified BOOLEAN NOT NULL DEFAULT FALSE,
    score_earned INT DEFAULT 0,
    CONSTRAINT fk_ss_student FOREIGN KEY (student_id) REFERENCES student_profiles(id) ON DELETE CASCADE,
    CONSTRAINT fk_ss_skill FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    UNIQUE KEY uq_student_skill (student_id, skill_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. Challenges Table
CREATE TABLE challenges (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recruiter_id INT,
    title VARCHAR(255) NOT NULL,
    problem_statement TEXT NOT NULL,
    instructions TEXT NOT NULL,
    difficulty_level ENUM('beginner', 'intermediate', 'advanced') NOT NULL DEFAULT 'intermediate',
    max_score INT NOT NULL DEFAULT 100,
    time_limit_minutes INT DEFAULT 180,
    submission_deadline DATETIME,
    evaluation_criteria TEXT NOT NULL,
    status ENUM('active', 'archived', 'draft') NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_challenge_recruiter FOREIGN KEY (recruiter_id) REFERENCES recruiter_profiles(id) ON DELETE SET NULL,
    INDEX idx_challenge_difficulty (difficulty_level),
    INDEX idx_challenge_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. Challenge Required Skills Table
CREATE TABLE challenge_required_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    challenge_id INT NOT NULL,
    skill_id INT NOT NULL,
    CONSTRAINT fk_crs_challenge FOREIGN KEY (challenge_id) REFERENCES challenges(id) ON DELETE CASCADE,
    CONSTRAINT fk_crs_skill FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    UNIQUE KEY uq_challenge_skill (challenge_id, skill_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 9. Jobs Table
CREATE TABLE jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recruiter_id INT NOT NULL,
    company_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    experience_level ENUM('entry', 'mid', 'senior') NOT NULL DEFAULT 'entry',
    employment_type ENUM('full_time', 'internship', 'part_time', 'contract') NOT NULL DEFAULT 'full_time',
    location VARCHAR(150) NOT NULL,
    is_remote BOOLEAN NOT NULL DEFAULT FALSE,
    salary_min DECIMAL(12, 2),
    salary_max DECIMAL(12, 2),
    currency VARCHAR(10) DEFAULT 'USD',
    deadline DATE,
    status ENUM('active', 'closed', 'draft') NOT NULL DEFAULT 'active',
    associated_challenge_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_job_recruiter FOREIGN KEY (recruiter_id) REFERENCES recruiter_profiles(id) ON DELETE CASCADE,
    CONSTRAINT fk_job_company FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    CONSTRAINT fk_job_challenge FOREIGN KEY (associated_challenge_id) REFERENCES challenges(id) ON DELETE SET NULL,
    INDEX idx_job_status (status),
    INDEX idx_job_exp (experience_level),
    INDEX idx_job_remote (is_remote)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 10. Job Required Skills Table
CREATE TABLE job_required_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT NOT NULL,
    skill_id INT NOT NULL,
    is_mandatory BOOLEAN NOT NULL DEFAULT TRUE,
    weight INT NOT NULL DEFAULT 1,
    CONSTRAINT fk_jrs_job FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    CONSTRAINT fk_jrs_skill FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    UNIQUE KEY uq_job_skill (job_id, skill_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 11. Applications Table
CREATE TABLE applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT NOT NULL,
    student_id INT NOT NULL,
    status ENUM('Applied', 'Assessment Pending', 'Under Review', 'Shortlisted', 'Rejected', 'Selected') NOT NULL DEFAULT 'Applied',
    cover_letter TEXT,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_app_job FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    CONSTRAINT fk_app_student FOREIGN KEY (student_id) REFERENCES student_profiles(id) ON DELETE CASCADE,
    UNIQUE KEY uq_job_student (job_id, student_id),
    INDEX idx_app_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 12. Submissions Table
CREATE TABLE submissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    challenge_id INT NOT NULL,
    student_id INT NOT NULL,
    application_id INT,
    github_repo_url VARCHAR(255),
    live_demo_url VARCHAR(255),
    project_file VARCHAR(255),
    explanation TEXT NOT NULL,
    status ENUM('submitted', 'evaluating', 'evaluated') NOT NULL DEFAULT 'submitted',
    score INT DEFAULT 0,
    feedback TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_sub_challenge FOREIGN KEY (challenge_id) REFERENCES challenges(id) ON DELETE CASCADE,
    CONSTRAINT fk_sub_student FOREIGN KEY (student_id) REFERENCES student_profiles(id) ON DELETE CASCADE,
    CONSTRAINT fk_sub_application FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE SET NULL,
    INDEX idx_sub_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 13. Assessments Table
CREATE TABLE assessments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    challenge_id INT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    pass_percentage INT NOT NULL DEFAULT 60,
    duration_minutes INT NOT NULL DEFAULT 30,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_assessment_challenge FOREIGN KEY (challenge_id) REFERENCES challenges(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 14. Questions Table
CREATE TABLE questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    assessment_id INT NOT NULL,
    question_text TEXT NOT NULL,
    question_type ENUM('mcq', 'code_snippet', 'short_answer') NOT NULL DEFAULT 'mcq',
    options_json TEXT,
    correct_answer TEXT NOT NULL,
    points INT NOT NULL DEFAULT 10,
    CONSTRAINT fk_question_assessment FOREIGN KEY (assessment_id) REFERENCES assessments(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 15. Assessment Attempts Table
CREATE TABLE assessment_attempts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    assessment_id INT NOT NULL,
    student_id INT NOT NULL,
    score INT NOT NULL DEFAULT 0,
    max_score INT NOT NULL DEFAULT 100,
    passed BOOLEAN NOT NULL DEFAULT FALSE,
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_attempt_assessment FOREIGN KEY (assessment_id) REFERENCES assessments(id) ON DELETE CASCADE,
    CONSTRAINT fk_attempt_student FOREIGN KEY (student_id) REFERENCES student_profiles(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 16. Evaluation Results Table
CREATE TABLE evaluation_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    submission_id INT NOT NULL UNIQUE,
    code_quality_score INT NOT NULL DEFAULT 0,
    functionality_score INT NOT NULL DEFAULT 0,
    ui_ux_score INT NOT NULL DEFAULT 0,
    total_score INT NOT NULL DEFAULT 0,
    max_score INT NOT NULL DEFAULT 100,
    ai_suggested_score INT DEFAULT NULL,
    ai_feedback TEXT,
    recruiter_comments TEXT,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_eval_submission FOREIGN KEY (submission_id) REFERENCES submissions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 17. AI Recommendations Table
CREATE TABLE ai_recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    recommendation_type ENUM('challenge', 'skill_gap', 'job') NOT NULL,
    target_id INT NOT NULL,
    score_or_fit FLOAT NOT NULL DEFAULT 0.0,
    rationale TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_air_student FOREIGN KEY (student_id) REFERENCES student_profiles(id) ON DELETE CASCADE,
    INDEX idx_air_type (recommendation_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 18. Recruiter Reviews Table
CREATE TABLE recruiter_reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recruiter_id INT NOT NULL,
    student_id INT NOT NULL,
    application_id INT,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review_notes TEXT NOT NULL,
    decision ENUM('shortlist', 'reject', 'hire', 'further_review') NOT NULL DEFAULT 'further_review',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_rr_recruiter FOREIGN KEY (recruiter_id) REFERENCES recruiter_profiles(id) ON DELETE CASCADE,
    CONSTRAINT fk_rr_student FOREIGN KEY (student_id) REFERENCES student_profiles(id) ON DELETE CASCADE,
    CONSTRAINT fk_rr_application FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 19. Notifications Table
CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    link VARCHAR(255),
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_notif_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_notif_user_read (user_id, is_read)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========================================================
-- INSERT SEED DATA
-- ========================================================

-- Skills
INSERT INTO skills (name, category) VALUES
('Python', 'backend'),
('Flask', 'backend'),
('Django', 'backend'),
('JavaScript', 'frontend'),
('React', 'frontend'),
('HTML5', 'frontend'),
('CSS3', 'frontend'),
('Node.js', 'backend'),
('MySQL', 'database'),
('PostgreSQL', 'database'),
('REST APIs', 'backend'),
('Docker', 'devops'),
('Git', 'devops'),
('Machine Learning', 'ai_ml'),
('TensorFlow', 'ai_ml'),
('AWS', 'devops'),
('UI/UX Design', 'frontend'),
('Cybersecurity', 'backend');

-- Users (Default password for all test accounts: password123)
INSERT INTO users (id, email, password_hash, role, is_active) VALUES
(1, 'sarah.jenkins@nexatech.com', 'scrypt:32768:8:1$7tS5v8lG8g6DfgkL$a6ee71f28876c1fe6a1a45ce3766eb51dcfebda9cf41d8eeb545ff033878b46571542f7c02b545d134b2fa7fe01f2be52ad39ecfc463eefce7c688d0b2fbb1c3', 'recruiter', TRUE),
(2, 'marcus.vance@pulseai.io', 'scrypt:32768:8:1$7tS5v8lG8g6DfgkL$a6ee71f28876c1fe6a1a45ce3766eb51dcfebda9cf41d8eeb545ff033878b46571542f7c02b545d134b2fa7fe01f2be52ad39ecfc463eefce7c688d0b2fbb1c3', 'recruiter', TRUE),
(3, 'priya.sharma@quantumpay.com', 'scrypt:32768:8:1$7tS5v8lG8g6DfgkL$a6ee71f28876c1fe6a1a45ce3766eb51dcfebda9cf41d8eeb545ff033878b46571542f7c02b545d134b2fa7fe01f2be52ad39ecfc463eefce7c688d0b2fbb1c3', 'recruiter', TRUE),
(4, 'alex.rivera@student.edu', 'scrypt:32768:8:1$7tS5v8lG8g6DfgkL$a6ee71f28876c1fe6a1a45ce3766eb51dcfebda9cf41d8eeb545ff033878b46571542f7c02b545d134b2fa7fe01f2be52ad39ecfc463eefce7c688d0b2fbb1c3', 'student', TRUE),
(5, 'samantha.chen@student.edu', 'scrypt:32768:8:1$7tS5v8lG8g6DfgkL$a6ee71f28876c1fe6a1a45ce3766eb51dcfebda9cf41d8eeb545ff033878b46571542f7c02b545d134b2fa7fe01f2be52ad39ecfc463eefce7c688d0b2fbb1c3', 'student', TRUE),
(6, 'david.oconnor@student.edu', 'scrypt:32768:8:1$7tS5v8lG8g6DfgkL$a6ee71f28876c1fe6a1a45ce3766eb51dcfebda9cf41d8eeb545ff033878b46571542f7c02b545d134b2fa7fe01f2be52ad39ecfc463eefce7c688d0b2fbb1c3', 'student', TRUE);

-- Companies
INSERT INTO companies (id, name, website, description, logo_url, location, industry) VALUES
(1, 'NexaTech Solutions', 'https://nexatech.example.com', 'Pioneering cloud computing and scalable enterprise SaaS infrastructure.', '/static/img/company1.png', 'San Francisco, CA / Remote', 'Cloud & Enterprise SaaS'),
(2, 'PulseAI Innovations', 'https://pulseai.example.io', 'Next-generation AI agents and intelligent data analytics workflows.', '/static/img/company2.png', 'New York, NY / Hybrid', 'Artificial Intelligence'),
(3, 'QuantumPay FinTech', 'https://quantumpay.example.com', 'High-throughput cross-border financial transactions and secure banking APIs.', '/static/img/company3.png', 'London, UK / Remote', 'Financial Technology');

-- Recruiter Profiles
INSERT INTO recruiter_profiles (id, user_id, company_id, full_name, official_email, designation, phone) VALUES
(1, 1, 1, 'Sarah Jenkins', 'sarah.jenkins@nexatech.com', 'Lead Technical Talent Partner', '+1-415-555-0192'),
(2, 2, 2, 'Marcus Vance', 'marcus.vance@pulseai.io', 'Head of Engineering & Recruitment', '+1-212-555-0143'),
(3, 3, 3, 'Priya Sharma', 'priya.sharma@quantumpay.com', 'Senior Technical Recruiter', '+44-20-7946-0912');

-- Student Profiles
INSERT INTO student_profiles (id, user_id, full_name, college_name, graduation_year, degree, bio, github_url, portfolio_url, linkedin_url) VALUES
(1, 4, 'Alex Rivera', 'Stanford University', 2025, 'B.S. in Computer Science', 'Full-stack software developer passionate about building performant web apps and AI-assisted tooling.', 'https://github.com/alexrivera-demo', 'https://alexrivera.dev', 'https://linkedin.com/in/alexrivera-demo'),
(2, 5, 'Samantha Chen', 'UC Berkeley', 2025, 'B.S. in Electrical Engineering & CS', 'Frontend-leaning engineer specialized in sleek responsive interfaces, accessible UX, and state management.', 'https://github.com/samchen-code', 'https://samchen.design', 'https://linkedin.com/in/samchen-demo'),
(3, 6, 'David O Connor', 'Georgia Institute of Technology', 2024, 'M.S. in Computer Science', 'Backend and distributed systems engineer with deep interest in relational databases and scalable microservices.', 'https://github.com/davidoc-tech', 'https://davidoconnor.io', 'https://linkedin.com/in/davidoc-demo');

-- Student Skills
INSERT INTO student_skills (student_id, skill_id, proficiency_level, verified, score_earned) VALUES
(1, 1, 'advanced', TRUE, 92),
(1, 2, 'advanced', TRUE, 88),
(1, 4, 'intermediate', TRUE, 85),
(1, 6, 'advanced', TRUE, 90),
(1, 7, 'advanced', TRUE, 90),
(1, 9, 'advanced', TRUE, 87),
(1, 11, 'advanced', TRUE, 91),
(2, 4, 'advanced', TRUE, 95),
(2, 5, 'advanced', TRUE, 94),
(2, 6, 'advanced', TRUE, 96),
(2, 7, 'advanced', TRUE, 95),
(2, 17, 'advanced', TRUE, 92),
(3, 1, 'advanced', TRUE, 94),
(3, 9, 'advanced', TRUE, 95),
(3, 10, 'advanced', TRUE, 90),
(3, 12, 'intermediate', TRUE, 82),
(3, 13, 'advanced', TRUE, 89);

-- Challenges
INSERT INTO challenges (id, recruiter_id, title, problem_statement, instructions, difficulty_level, max_score, time_limit_minutes, submission_deadline, evaluation_criteria, status) VALUES
(1, 1, 'Full-Stack Student Attendance & Portal System', 
'Build a functional web application for managing student course registrations, daily attendance tracking, and attendance percentage reporting. The application must feature responsive tables, role-based views for teachers and students, and persistent relational data storage.',
'1. Implement clean database schema with courses, students, and attendance logs.\n2. Create REST API endpoints or server-rendered views for marking attendance.\n3. Include input validation and error states.\n4. Provide a GitHub repository link with a comprehensive README and a working demo link.',
'intermediate', 100, 240, DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 14 DAY), 
'Code Architecture (30%), Database Modeling & Queries (30%), UI/UX Responsiveness (20%), Edge Case Handling & Documentation (20%)', 'active'),

(2, 2, 'AI Skill Matcher & Recommendation Engine Microservice',
'Develop an intelligent microservice that extracts technical keywords from student profiles and calculates similarity against job descriptions, returning a match score, missing skill recommendations, and ranked challenges.',
'1. Use Python (Flask/FastAPI) to expose a POST /match-skills endpoint.\n2. Handle skill synonyms and taxonomy categorization.\n3. Return explainable breakdown of matched vs missing skills.\n4. Include unit tests demonstrating calculation accuracy.',
'advanced', 100, 300, DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 21 DAY),
'Algorithmic Accuracy (35%), API Design & Clean Code (35%), Test Coverage (15%), Documentation & Edge Cases (15%)', 'active'),

(3, 3, 'High-Throughput Payment Ledger & Transaction Validator',
'Construct a transaction processing service that validates incoming double-entry financial transactions, guarantees ACID consistency, prevents race conditions, and logs tamper-evident audit trails.',
'1. Implement transactional isolation for debit/credit operations.\n2. Prevent negative balances and double spend.\n3. Return structured error codes on insufficient funds.\n4. Provide benchmark script demonstrating concurrent safety.',
'advanced', 100, 360, DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 10 DAY),
'Database Concurrency & ACID Safety (40%), Error Handling & Security (30%), Code Cleanliness (20%), Performance (10%)', 'active'),

(4, 1, 'Modern Responsive Job Board Frontend Component',
'Craft a responsive, accessible job catalog UI with instant client-side filtering by location, salary range, and technology tags. Include animated status badges and clean card transitions.',
'1. Build using modern semantic HTML5, CSS custom properties (Flexbox/Grid), and Vanilla JavaScript.\n2. Zero dependencies preferred or lightweight modern UI library.\n3. Must achieve full responsiveness across mobile (375px), tablet (768px), and desktop (1200px+).',
'beginner', 100, 180, DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 18 DAY),
'Visual Polish & Typography (35%), CSS Architecture & Responsiveness (35%), Interactive Filtering Logic (20%), Accessibility (10%)', 'active'),

(5, 2, 'Automated CI/CD Pipeline & Docker Containerizer',
'Containerize a multi-tier Python Flask + MySQL web application using multi-stage Dockerfiles and Docker Compose. Include automated healthcheck scripts and persistent volume mounting.',
'1. Write an optimized non-root Dockerfile for the Flask web service.\n2. Configure docker-compose.yml linking the app and MySQL with healthcheck dependencies.\n3. Provide a GitHub Actions workflow YAML that builds the image and runs test suites.',
'intermediate', 100, 180, DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 15 DAY),
'Dockerfile Optimization & Security (35%), Compose Configuration (35%), CI/CD Workflow (20%), Documentation (10%)', 'active');

-- Challenge Skills
INSERT INTO challenge_required_skills (challenge_id, skill_id) VALUES
(1, 1), (1, 2), (1, 6), (1, 7), (1, 9),
(2, 1), (2, 2), (2, 11), (2, 14),
(3, 1), (3, 9), (3, 10), (3, 18),
(4, 4), (4, 6), (4, 7), (4, 17),
(5, 12), (5, 13), (5, 1), (5, 9);

-- Jobs
INSERT INTO jobs (id, recruiter_id, company_id, title, description, experience_level, employment_type, location, is_remote, salary_min, salary_max, currency, deadline, status, associated_challenge_id) VALUES
(1, 1, 1, 'Junior Full-Stack Web Developer',
'We are looking for an ambitious Full-Stack Developer to join our Cloud Applications team. You will build user-facing features, design RESTful APIs, and contribute to our robust database layer. Candidates who complete our practical challenge receive priority interview scheduling!',
'entry', 'full_time', 'San Francisco, CA', TRUE, 78000.00, 98000.00, 'USD', DATE_ADD(CURRENT_DATE, INTERVAL 30 DAY), 'active', 1),

(2, 2, 2, 'Backend Python & AI Integration Engineer',
'PulseAI is hiring a Backend Engineer to build high-scale APIs connecting LLMs, vector indices, and customer relational data. You will architect resilient endpoints, optimize SQL queries, and implement automated data pipelines.',
'mid', 'full_time', 'New York, NY', FALSE, 95000.00, 125000.00, 'USD', DATE_ADD(CURRENT_DATE, INTERVAL 25 DAY), 'active', 2),

(3, 3, 3, 'FinTech Backend API & Systems Engineer',
'Join QuantumPay to build the backbone of next-gen financial settlement networks. You will work on ACID-compliant ledger systems, idempotent API design, and high-concurrency database operations.',
'mid', 'full_time', 'London, UK', TRUE, 90000.00, 115000.00, 'USD', DATE_ADD(CURRENT_DATE, INTERVAL 20 DAY), 'active', 3),

(4, 1, 1, 'Frontend UI/UX Web Engineer',
'NexaTech is searching for a detail-obsessed Frontend Developer. You will translate wireframes into pixel-perfect, accessible, and fast web experiences with clean JavaScript and CSS architecture.',
'entry', 'full_time', 'San Francisco, CA', TRUE, 72000.00, 90000.00, 'USD', DATE_ADD(CURRENT_DATE, INTERVAL 28 DAY), 'active', 4),

(5, 2, 2, 'AI & Machine Learning Engineering Intern',
'A high-impact summer/fall internship for students passionate about machine learning, natural language processing, and practical recommendation algorithms. Work directly with senior staff research engineers.',
'entry', 'internship', 'New York, NY', TRUE, 45000.00, 60000.00, 'USD', DATE_ADD(CURRENT_DATE, INTERVAL 35 DAY), 'active', 2),

(6, 1, 1, 'Cloud Infrastructure & DevOps Engineer',
'Help manage and automate our multi-region Kubernetes and Docker cloud deployments. Implement automated CI/CD pipelines, container security, and system observability.',
'mid', 'full_time', 'Austin, TX', FALSE, 105000.00, 135000.00, 'USD', DATE_ADD(CURRENT_DATE, INTERVAL 40 DAY), 'active', 5);

-- Job Required Skills
INSERT INTO job_required_skills (job_id, skill_id, is_mandatory, weight) VALUES
(1, 1, TRUE, 3), (1, 2, TRUE, 3), (1, 4, TRUE, 2), (1, 9, TRUE, 3), (1, 6, FALSE, 1),
(2, 1, TRUE, 3), (2, 11, TRUE, 3), (2, 14, TRUE, 2), (2, 9, TRUE, 2),
(3, 1, TRUE, 3), (3, 9, TRUE, 3), (3, 10, TRUE, 2), (3, 18, TRUE, 2),
(4, 4, TRUE, 3), (4, 6, TRUE, 3), (4, 7, TRUE, 3), (4, 17, TRUE, 2),
(5, 1, TRUE, 3), (5, 14, TRUE, 3), (5, 15, FALSE, 2),
(6, 12, TRUE, 3), (6, 13, TRUE, 2), (6, 16, TRUE, 3);

-- Applications
INSERT INTO applications (id, job_id, student_id, status, cover_letter, applied_at) VALUES
(1, 1, 1, 'Shortlisted', 'I am eager to contribute my full-stack Python/Flask and relational database experience to NexaTech. I completed the attendance portal challenge with 94/100 score.', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 5 DAY)),
(2, 4, 2, 'Under Review', 'Excited about crafting seamless interfaces for NexaTech. My Berkeley coursework and portfolio showcase strong vanilla JavaScript and responsive CSS capabilities.', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 3 DAY)),
(3, 2, 3, 'Assessment Pending', 'I have substantial background in database tuning and Python backend services at Georgia Tech. Look forward to taking the challenge!', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 2 DAY)),
(4, 2, 1, 'Applied', 'Passionate about intelligent recommendation algorithms and Python APIs. Looking forward to tackling the challenge assessment.', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 1 DAY));

-- Submissions
INSERT INTO submissions (id, challenge_id, student_id, application_id, github_repo_url, live_demo_url, project_file, explanation, status, score, feedback, submitted_at) VALUES
(1, 1, 1, 1, 'https://github.com/alexrivera-demo/challengehire-attendance-portal', 'https://attendance-demo.alexrivera.dev', 'alex_attendance_v1.zip',
'Architected a 3NF relational database schema with courses, students, and attendance sheets. Built RESTful Flask blueprint endpoints with parameterized queries, role checks, and an interactive Chart.js dashboard showing student percentage statistics. Implemented unit tests for negative input handling.',
'evaluated', 94, 'Outstanding code quality! The database schema is fully normalized, queries use proper indexes, and the responsive UI handles edge cases cleanly. Strong recommendation for technical interview.', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 4 DAY)),

(2, 4, 2, 2, 'https://github.com/samchen-code/challengehire-responsive-job-board', 'https://jobs-demo.samchen.design', 'sam_jobboard_ui.zip',
'Designed an ultra-clean, accessible job board catalog using CSS Grid, custom properties, and native JavaScript state filtering. Includes smooth badge animations, empty-state placeholders, and mobile touch drawer navigation.',
'evaluated', 92, 'Superb attention to detail and typography. Clean separation of concerns in CSS and zero external dependencies. Highly impressive work for an entry-level candidate.', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 2 DAY));

-- Evaluation Results
INSERT INTO evaluation_results (id, submission_id, code_quality_score, functionality_score, ui_ux_score, total_score, max_score, ai_suggested_score, ai_feedback, recruiter_comments) VALUES
(1, 1, 29, 38, 27, 94, 100, 92, 
'AI Assessment: Clean modular MVC structure. Schema adheres to 3NF standards. Input validation covers nulls and boundary IDs. Code demonstrates strong adherence to PEP 8.',
'Excellent candidate with strong fundamentals in backend engineering and database design. Shortlisted for Round 2.'),
(2, 2, 28, 36, 28, 92, 100, 90,
'AI Assessment: Semantic HTML structure verified. Accessible ARIA attributes present. Filter debouncing implemented properly. CSS variables provide consistent theming.',
'Great frontend sense and clean architectural style. Shortlisted for engineering review.');

-- Assessments & Questions
INSERT INTO assessments (id, challenge_id, title, description, pass_percentage, duration_minutes) VALUES
(1, 1, 'Web & Database Engineering Fundamentals', 'Verifies knowledge of SQL joins, HTTP methods, session management, and MVC architecture.', 60, 20);

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
