import json
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(191), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student') # 'student', 'recruiter', 'admin'
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student_profile = db.relationship('StudentProfile', backref='user', uselist=False, cascade="all, delete-orphan")
    recruiter_profile = db.relationship('RecruiterProfile', backref='user', uselist=False, cascade="all, delete-orphan")
    notifications = db.relationship('Notification', backref='user', cascade="all, delete-orphan", lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_student(self):
        return self.role == 'student'
        
    def is_recruiter(self):
        return self.role == 'recruiter'


class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    website = db.Column(db.String(255))
    description = db.Column(db.Text)
    logo_url = db.Column(db.String(255))
    location = db.Column(db.String(255), nullable=False)
    industry = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    recruiters = db.relationship('RecruiterProfile', backref='company', lazy='dynamic')
    jobs = db.relationship('Job', backref='company', lazy='dynamic')


class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    full_name = db.Column(db.String(150), nullable=False, index=True)
    college_name = db.Column(db.String(255), nullable=False, index=True)
    graduation_year = db.Column(db.Integer)
    degree = db.Column(db.String(100))
    bio = db.Column(db.Text)
    github_url = db.Column(db.String(255))
    portfolio_url = db.Column(db.String(255))
    linkedin_url = db.Column(db.String(255))
    resume_filename = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student_skills = db.relationship('StudentSkill', backref='student', cascade="all, delete-orphan", lazy='dynamic')
    applications = db.relationship('Application', backref='student', cascade="all, delete-orphan", lazy='dynamic')
    submissions = db.relationship('Submission', backref='student', cascade="all, delete-orphan", lazy='dynamic')
    assessment_attempts = db.relationship('AssessmentAttempt', backref='student', cascade="all, delete-orphan", lazy='dynamic')
    ai_recommendations = db.relationship('AIRecommendation', backref='student', cascade="all, delete-orphan", lazy='dynamic')
    reviews_received = db.relationship('RecruiterReview', backref='student', cascade="all, delete-orphan", lazy='dynamic')

    @property
    def skills_list(self):
        return [ss.skill.name for ss in self.student_skills.join(Skill).all()]


class RecruiterProfile(db.Model):
    __tablename__ = 'recruiter_profiles'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    full_name = db.Column(db.String(150), nullable=False, index=True)
    official_email = db.Column(db.String(191), nullable=False)
    designation = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(30))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    jobs = db.relationship('Job', backref='recruiter', cascade="all, delete-orphan", lazy='dynamic')
    challenges = db.relationship('Challenge', backref='recruiter', lazy='dynamic')
    reviews_given = db.relationship('RecruiterReview', backref='recruiter', lazy='dynamic')


class Skill(db.Model):
    __tablename__ = 'skills'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False, default='general') # frontend, backend, database, devops, ai_ml, general


class StudentSkill(db.Model):
    __tablename__ = 'student_skills'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), nullable=False)
    proficiency_level = db.Column(db.String(20), default='intermediate') # beginner, intermediate, advanced
    verified = db.Column(db.Boolean, default=False)
    score_earned = db.Column(db.Integer, default=0)
    
    skill = db.relationship('Skill', backref='student_associations')
    __table_args__ = (db.UniqueConstraint('student_id', 'skill_id', name='uq_student_skill'),)


class Challenge(db.Model):
    __tablename__ = 'challenges'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recruiter_id = db.Column(db.Integer, db.ForeignKey('recruiter_profiles.id', ondelete='SET NULL'), nullable=True)
    title = db.Column(db.String(255), nullable=False)
    problem_statement = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    difficulty_level = db.Column(db.String(20), default='intermediate') # beginner, intermediate, advanced
    max_score = db.Column(db.Integer, default=100, nullable=False)
    time_limit_minutes = db.Column(db.Integer, default=180)
    submission_deadline = db.Column(db.DateTime, nullable=True)
    evaluation_criteria = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='active') # active, archived, draft
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    required_skills = db.relationship('ChallengeRequiredSkill', backref='challenge', cascade="all, delete-orphan", lazy='dynamic')
    submissions = db.relationship('Submission', backref='challenge', cascade="all, delete-orphan", lazy='dynamic')
    assessments = db.relationship('Assessment', backref='challenge', cascade="all, delete-orphan", lazy='dynamic')
    jobs = db.relationship('Job', backref='associated_challenge_rel', foreign_keys='Job.associated_challenge_id')

    @property
    def skills_list(self):
        return [crs.skill.name for crs in self.required_skills.join(Skill).all()]


class ChallengeRequiredSkill(db.Model):
    __tablename__ = 'challenge_required_skills'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id', ondelete='CASCADE'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), nullable=False)
    
    skill = db.relationship('Skill')
    __table_args__ = (db.UniqueConstraint('challenge_id', 'skill_id', name='uq_challenge_skill'),)


class Job(db.Model):
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recruiter_id = db.Column(db.Integer, db.ForeignKey('recruiter_profiles.id', ondelete='CASCADE'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    experience_level = db.Column(db.String(20), default='entry') # entry, mid, senior
    employment_type = db.Column(db.String(20), default='full_time') # full_time, internship, part_time, contract
    location = db.Column(db.String(150), nullable=False)
    is_remote = db.Column(db.Boolean, default=False)
    salary_min = db.Column(db.Numeric(12, 2), nullable=True)
    salary_max = db.Column(db.Numeric(12, 2), nullable=True)
    currency = db.Column(db.String(10), default='USD')
    deadline = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='active') # active, closed, draft
    associated_challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    required_skills = db.relationship('JobRequiredSkill', backref='job', cascade="all, delete-orphan", lazy='dynamic')
    applications = db.relationship('Application', backref='job', cascade="all, delete-orphan", lazy='dynamic')
    challenge = db.relationship('Challenge', foreign_keys=[associated_challenge_id], overlaps="associated_challenge_rel,jobs")

    @property
    def skills_list(self):
        return [jrs.skill.name for jrs in self.required_skills.join(Skill).all()]


class JobRequiredSkill(db.Model):
    __tablename__ = 'job_required_skills'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), nullable=False)
    is_mandatory = db.Column(db.Boolean, default=True)
    weight = db.Column(db.Integer, default=1)
    
    skill = db.relationship('Skill')
    __table_args__ = (db.UniqueConstraint('job_id', 'skill_id', name='uq_job_skill'),)


class Application(db.Model):
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(30), default='Applied') # Applied, Assessment Pending, Under Review, Shortlisted, Rejected, Selected
    cover_letter = db.Column(db.Text, nullable=True)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    submissions = db.relationship('Submission', backref='application', lazy='dynamic')
    reviews = db.relationship('RecruiterReview', backref='application', lazy='dynamic')
    
    __table_args__ = (db.UniqueConstraint('job_id', 'student_id', name='uq_job_student'),)


class Submission(db.Model):
    __tablename__ = 'submissions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id', ondelete='SET NULL'), nullable=True)
    github_repo_url = db.Column(db.String(255))
    live_demo_url = db.Column(db.String(255))
    project_file = db.Column(db.String(255))
    explanation = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='submitted') # submitted, evaluating, evaluated
    score = db.Column(db.Integer, default=0)
    feedback = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    evaluation = db.relationship('EvaluationResult', backref='submission', uselist=False, cascade="all, delete-orphan")


class Assessment(db.Model):
    __tablename__ = 'assessments'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id', ondelete='CASCADE'), nullable=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    pass_percentage = db.Column(db.Integer, default=60)
    duration_minutes = db.Column(db.Integer, default=30)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    questions = db.relationship('Question', backref='assessment', cascade="all, delete-orphan", lazy='dynamic')
    attempts = db.relationship('AssessmentAttempt', backref='assessment', cascade="all, delete-orphan", lazy='dynamic')


class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id', ondelete='CASCADE'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), default='mcq') # mcq, code_snippet, short_answer
    options_json = db.Column(db.Text) # JSON string
    correct_answer = db.Column(db.Text, nullable=False)
    points = db.Column(db.Integer, default=10)

    @property
    def options(self):
        if self.options_json:
            try:
                return json.loads(self.options_json)
            except Exception:
                return []
        return []


class AssessmentAttempt(db.Model):
    __tablename__ = 'assessment_attempts'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    score = db.Column(db.Integer, default=0)
    max_score = db.Column(db.Integer, default=100)
    passed = db.Column(db.Boolean, default=False)
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow)


class EvaluationResult(db.Model):
    __tablename__ = 'evaluation_results'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id', ondelete='CASCADE'), unique=True, nullable=False)
    code_quality_score = db.Column(db.Integer, default=0)
    functionality_score = db.Column(db.Integer, default=0)
    ui_ux_score = db.Column(db.Integer, default=0)
    total_score = db.Column(db.Integer, default=0)
    max_score = db.Column(db.Integer, default=100)
    ai_suggested_score = db.Column(db.Integer, nullable=True)
    ai_feedback = db.Column(db.Text)
    recruiter_comments = db.Column(db.Text)
    evaluated_at = db.Column(db.DateTime, default=datetime.utcnow)


class AIRecommendation(db.Model):
    __tablename__ = 'ai_recommendations'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    recommendation_type = db.Column(db.String(20), nullable=False) # 'challenge', 'skill_gap', 'job'
    target_id = db.Column(db.Integer, nullable=False)
    score_or_fit = db.Column(db.Float, default=0.0)
    rationale = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class RecruiterReview(db.Model):
    __tablename__ = 'recruiter_reviews'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recruiter_id = db.Column(db.Integer, db.ForeignKey('recruiter_profiles.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id', ondelete='SET NULL'), nullable=True)
    rating = db.Column(db.Integer, default=3) # 1 - 5
    review_notes = db.Column(db.Text, nullable=False)
    decision = db.Column(db.String(20), default='further_review') # shortlist, reject, hire, further_review
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(255))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
