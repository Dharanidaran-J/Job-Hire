-- ========================================================
-- ChallengeHire - MySQL Relational Database Schema
-- AI-Based Job Recruitment Management System
-- Normalized to 3NF with Primary Keys, Foreign Keys, Indexes
-- ========================================================

CREATE DATABASE IF NOT EXISTS challengehire_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE challengehire_db;

-- Disable FK checks during schema drops/recreation
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

-- 1. Users Table (Core Auth for all roles)
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

-- 5. Skills Table (Taxonomy)
CREATE TABLE skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    category ENUM('frontend', 'backend', 'database', 'devops', 'ai_ml', 'mobile', 'general') NOT NULL DEFAULT 'general',
    INDEX idx_skill_name (name),
    INDEX idx_skill_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Student Skills Table (Many-to-Many)
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

-- 7. Challenges Table (Real-world assessments created by recruiters or platform)
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

-- 8. Challenge Required Skills Table (Many-to-Many)
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

-- 10. Job Required Skills Table (Many-to-Many)
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

-- 11. Applications Table (Job Applications)
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

-- 12. Submissions Table (Practical Challenge Submissions)
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

-- 13. Assessments Table (Objective / Knowledge tests linked to challenges)
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

-- 14. Questions Table (Quiz questions for assessments)
CREATE TABLE questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    assessment_id INT NOT NULL,
    question_text TEXT NOT NULL,
    question_type ENUM('mcq', 'code_snippet', 'short_answer') NOT NULL DEFAULT 'mcq',
    options_json TEXT, -- JSON array of options e.g. ["Option A", "Option B", ...]
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

-- 16. Evaluation Results Table (Detailed Rubric Scores for Submissions)
CREATE TABLE evaluation_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    submission_id INT NOT NULL UNIQUE,
    code_quality_score INT NOT NULL DEFAULT 0,     -- e.g. out of 30
    functionality_score INT NOT NULL DEFAULT 0,    -- e.g. out of 40
    ui_ux_score INT NOT NULL DEFAULT 0,            -- e.g. out of 30
    total_score INT NOT NULL DEFAULT 0,            -- e.g. out of 100
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
    target_id INT NOT NULL, -- references challenge_id, job_id, or skill_id
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
