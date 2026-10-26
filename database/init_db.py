"""
ChallengeHire Database Initializer & Seeder
Creates tables and seeds initial realistic demo data across all 18 tables.
"""

import sys
import os
from datetime import datetime, timedelta

# Ensure parent path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import (
    db, User, Company, StudentProfile, RecruiterProfile, Skill,
    StudentSkill, Challenge, ChallengeRequiredSkill, Job, JobRequiredSkill,
    Application, Submission, Assessment, Question, AssessmentAttempt,
    EvaluationResult, AIRecommendation, RecruiterReview, Notification
)

def seed_database(app):
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if already seeded
        if User.query.first():
            print("Database already contains records. Skipping seed.")
            return

        print("Seeding ChallengeHire database with realistic records...")

        # 1. Skills
        skill_catalog = [
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
            ('Cybersecurity', 'backend')
        ]
        
        skills_map = {}
        for name, cat in skill_catalog:
            sk = Skill(name=name, category=cat)
            db.session.add(sk)
            skills_map[name] = sk
            
        db.session.commit()

        # 2. Companies
        c1 = Company(
            name="NexaTech Solutions",
            website="https://nexatech.example.com",
            description="Pioneering cloud computing and scalable enterprise SaaS infrastructure.",
            logo_url="https://images.unsplash.com/photo-1549923746-c502d488b3ea?w=120&auto=format&fit=crop&q=60",
            location="San Francisco, CA / Remote",
            industry="Cloud & Enterprise SaaS"
        )
        c2 = Company(
            name="PulseAI Innovations",
            website="https://pulseai.example.io",
            description="Next-generation AI agents and intelligent data analytics workflows.",
            logo_url="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=120&auto=format&fit=crop&q=60",
            location="New York, NY / Hybrid",
            industry="Artificial Intelligence"
        )
        c3 = Company(
            name="QuantumPay FinTech",
            website="https://quantumpay.example.com",
            description="High-throughput cross-border financial transactions and secure banking APIs.",
            logo_url="https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=120&auto=format&fit=crop&q=60",
            location="London, UK / Remote",
            industry="Financial Technology"
        )
        db.session.add_all([c1, c2, c3])
        db.session.commit()

        # 3. Recruiter Users & Profiles (password: password123)
        # Recruiter 1
        u_rec1 = User(email="sarah.jenkins@nexatech.com", role="recruiter")
        u_rec1.set_password("password123")
        db.session.add(u_rec1)
        db.session.flush()
        
        rp1 = RecruiterProfile(
            user_id=u_rec1.id,
            company_id=c1.id,
            full_name="Sarah Jenkins",
            official_email="sarah.jenkins@nexatech.com",
            designation="Lead Technical Talent Partner",
            phone="+1-415-555-0192"
        )
        db.session.add(rp1)

        # Recruiter 2
        u_rec2 = User(email="marcus.vance@pulseai.io", role="recruiter")
        u_rec2.set_password("password123")
        db.session.add(u_rec2)
        db.session.flush()
        
        rp2 = RecruiterProfile(
            user_id=u_rec2.id,
            company_id=c2.id,
            full_name="Marcus Vance",
            official_email="marcus.vance@pulseai.io",
            designation="Director of Engineering Recruitment",
            phone="+1-212-555-0143"
        )
        db.session.add(rp2)

        # Recruiter 3
        u_rec3 = User(email="priya.sharma@quantumpay.com", role="recruiter")
        u_rec3.set_password("password123")
        db.session.add(u_rec3)
        db.session.flush()
        
        rp3 = RecruiterProfile(
            user_id=u_rec3.id,
            company_id=c3.id,
            full_name="Priya Sharma",
            official_email="priya.sharma@quantumpay.com",
            designation="Senior Technical Recruiter",
            phone="+44-20-7946-0912"
        )
        db.session.add(rp3)
        db.session.commit()

        # 4. Student Users & Profiles
        # Student 1: Alex Rivera
        u_stu1 = User(email="alex.rivera@student.edu", role="student")
        u_stu1.set_password("password123")
        db.session.add(u_stu1)
        db.session.flush()
        
        sp1 = StudentProfile(
            user_id=u_stu1.id,
            full_name="Alex Rivera",
            college_name="Stanford University",
            graduation_year=2025,
            degree="B.S. in Computer Science",
            bio="Full-stack software developer passionate about building performant web apps and AI-assisted tooling.",
            github_url="https://github.com/alexrivera-demo",
            portfolio_url="https://alexrivera.dev",
            linkedin_url="https://linkedin.com/in/alexrivera-demo"
        )
        db.session.add(sp1)
        db.session.flush()

        # Student 2: Samantha Chen
        u_stu2 = User(email="samantha.chen@student.edu", role="student")
        u_stu2.set_password("password123")
        db.session.add(u_stu2)
        db.session.flush()
        
        sp2 = StudentProfile(
            user_id=u_stu2.id,
            full_name="Samantha Chen",
            college_name="UC Berkeley",
            graduation_year=2025,
            degree="B.S. in EECS",
            bio="Frontend-leaning engineer specialized in sleek responsive interfaces, accessible UX, and state management.",
            github_url="https://github.com/samchen-code",
            portfolio_url="https://samchen.design",
            linkedin_url="https://linkedin.com/in/samchen-demo"
        )
        db.session.add(sp2)
        db.session.flush()

        # Student 3: David O'Connor
        u_stu3 = User(email="david.oconnor@student.edu", role="student")
        u_stu3.set_password("password123")
        db.session.add(u_stu3)
        db.session.flush()
        
        sp3 = StudentProfile(
            user_id=u_stu3.id,
            full_name="David O'Connor",
            college_name="Georgia Institute of Technology",
            graduation_year=2024,
            degree="M.S. in Computer Science",
            bio="Backend and distributed systems engineer with deep interest in relational databases and scalable microservices.",
            github_url="https://github.com/davidoc-tech",
            portfolio_url="https://davidoconnor.io",
            linkedin_url="https://linkedin.com/in/davidoc-demo"
        )
        db.session.add(sp3)
        db.session.commit()

        # 5. Assign Student Skills
        def add_ss(stu_id, skill_name, prof, verified, score):
            sk = skills_map.get(skill_name)
            if sk:
                db.session.add(StudentSkill(
                    student_id=stu_id,
                    skill_id=sk.id,
                    proficiency_level=prof,
                    verified=verified,
                    score_earned=score
                ))

        # Alex Skills
        add_ss(sp1.id, 'Python', 'advanced', True, 92)
        add_ss(sp1.id, 'Flask', 'advanced', True, 88)
        add_ss(sp1.id, 'JavaScript', 'intermediate', True, 85)
        add_ss(sp1.id, 'HTML5', 'advanced', True, 90)
        add_ss(sp1.id, 'CSS3', 'advanced', True, 90)
        add_ss(sp1.id, 'MySQL', 'advanced', True, 87)
        add_ss(sp1.id, 'REST APIs', 'advanced', True, 91)

        # Samantha Skills
        add_ss(sp2.id, 'JavaScript', 'advanced', True, 95)
        add_ss(sp2.id, 'React', 'advanced', True, 94)
        add_ss(sp2.id, 'HTML5', 'advanced', True, 96)
        add_ss(sp2.id, 'CSS3', 'advanced', True, 95)
        add_ss(sp2.id, 'UI/UX Design', 'advanced', True, 92)

        # David Skills
        add_ss(sp3.id, 'Python', 'advanced', True, 94)
        add_ss(sp3.id, 'MySQL', 'advanced', True, 95)
        add_ss(sp3.id, 'PostgreSQL', 'advanced', True, 90)
        add_ss(sp3.id, 'Docker', 'intermediate', True, 82)
        add_ss(sp3.id, 'Git', 'advanced', True, 89)

        db.session.commit()

        # 6. Challenges (Practical assessments)
        now = datetime.utcnow()

        ch1 = Challenge(
            recruiter_id=rp1.id,
            title="Full-Stack Student Attendance & Portal System",
            problem_statement="Build a functional web application for managing student course registrations, daily attendance tracking, and attendance percentage reporting. The application must feature responsive tables, role-based views for teachers and students, and persistent relational data storage.",
            instructions="1. Implement clean database schema with courses, students, and attendance logs.\n2. Create REST API endpoints or server-rendered views for marking attendance.\n3. Include input validation and error states.\n4. Provide a GitHub repository link with a comprehensive README and a working demo link.",
            difficulty_level="intermediate",
            max_score=100,
            time_limit_minutes=240,
            submission_deadline=now + timedelta(days=14),
            evaluation_criteria="Code Architecture (30%), Database Modeling & Queries (30%), UI/UX Responsiveness (20%), Edge Case Handling & Documentation (20%)",
            status="active"
        )
        ch2 = Challenge(
            recruiter_id=rp2.id,
            title="AI Skill Matcher & Recommendation Engine Microservice",
            problem_statement="Develop an intelligent microservice that extracts technical keywords from student profiles and calculates similarity against job descriptions, returning a match score, missing skill recommendations, and ranked challenges.",
            instructions="1. Use Python (Flask/FastAPI) to expose a POST /match-skills endpoint.\n2. Handle skill synonyms and taxonomy categorization.\n3. Return explainable breakdown of matched vs missing skills.\n4. Include unit tests demonstrating calculation accuracy.",
            difficulty_level="advanced",
            max_score=100,
            time_limit_minutes=300,
            submission_deadline=now + timedelta(days=21),
            evaluation_criteria="Algorithmic Accuracy (35%), API Design & Clean Code (35%), Test Coverage (15%), Documentation & Edge Cases (15%)",
            status="active"
        )
        ch3 = Challenge(
            recruiter_id=rp3.id,
            title="High-Throughput Payment Ledger & Transaction Validator",
            problem_statement="Construct a transaction processing service that validates incoming double-entry financial transactions, guarantees ACID consistency, prevents race conditions, and logs tamper-evident audit trails.",
            instructions="1. Implement transactional isolation for debit/credit operations.\n2. Prevent negative balances and double spend.\n3. Return structured error codes on insufficient funds.\n4. Provide benchmark script demonstrating concurrent safety.",
            difficulty_level="advanced",
            max_score=100,
            time_limit_minutes=360,
            submission_deadline=now + timedelta(days=10),
            evaluation_criteria="Database Concurrency & ACID Safety (40%), Error Handling & Security (30%), Code Cleanliness (20%), Performance (10%)",
            status="active"
        )
        ch4 = Challenge(
            recruiter_id=rp1.id,
            title="Modern Responsive Job Board Frontend Component",
            problem_statement="Craft a responsive, accessible job catalog UI with instant client-side filtering by location, salary range, and technology tags. Include animated status badges and clean card transitions.",
            instructions="1. Build using modern semantic HTML5, CSS custom properties (Flexbox/Grid), and Vanilla JavaScript.\n2. Zero dependencies preferred or lightweight modern UI library.\n3. Must achieve full responsiveness across mobile (375px), tablet (768px), and desktop (1200px+).",
            difficulty_level="beginner",
            max_score=100,
            time_limit_minutes=180,
            submission_deadline=now + timedelta(days=18),
            evaluation_criteria="Visual Polish & Typography (35%), CSS Architecture & Responsiveness (35%), Interactive Filtering Logic (20%), Accessibility (10%)",
            status="active"
        )
        ch5 = Challenge(
            recruiter_id=rp2.id,
            title="Automated CI/CD Pipeline & Docker Containerizer",
            problem_statement="Containerize a multi-tier Python Flask + MySQL web application using multi-stage Dockerfiles and Docker Compose. Include automated healthcheck scripts and persistent volume mounting.",
            instructions="1. Write an optimized non-root Dockerfile for the Flask web service.\n2. Configure docker-compose.yml linking the app and MySQL with healthcheck dependencies.\n3. Provide a GitHub Actions workflow YAML that builds the image and runs test suites.",
            difficulty_level="intermediate",
            max_score=100,
            time_limit_minutes=180,
            submission_deadline=now + timedelta(days=15),
            evaluation_criteria="Dockerfile Optimization & Security (35%), Compose Configuration (35%), CI/CD Workflow (20%), Documentation (10%)",
            status="active"
        )
        db.session.add_all([ch1, ch2, ch3, ch4, ch5])
        db.session.commit()

        # Link challenge skills
        def link_cs(ch_id, skill_names):
            for name in skill_names:
                sk = skills_map.get(name)
                if sk:
                    db.session.add(ChallengeRequiredSkill(challenge_id=ch_id, skill_id=sk.id))

        link_cs(ch1.id, ['Python', 'Flask', 'HTML5', 'CSS3', 'MySQL'])
        link_cs(ch2.id, ['Python', 'Flask', 'REST APIs', 'Machine Learning'])
        link_cs(ch3.id, ['Python', 'MySQL', 'PostgreSQL', 'Cybersecurity'])
        link_cs(ch4.id, ['JavaScript', 'HTML5', 'CSS3', 'UI/UX Design'])
        link_cs(ch5.id, ['Docker', 'Git', 'Python', 'MySQL'])
        db.session.commit()

        # 7. Jobs (at least 6 diverse openings)
        j1 = Job(
            recruiter_id=rp1.id,
            company_id=c1.id,
            title="Junior Full-Stack Web Developer",
            description="We are looking for an ambitious Full-Stack Developer to join our Cloud Applications team. You will build user-facing features, design RESTful APIs, and contribute to our robust database layer. Candidates who complete our practical challenge receive priority interview scheduling!",
            experience_level="entry",
            employment_type="full_time",
            location="San Francisco, CA",
            is_remote=True,
            salary_min=78000.00,
            salary_max=98000.00,
            currency="USD",
            deadline=(now + timedelta(days=30)).date(),
            status="active",
            associated_challenge_id=ch1.id
        )
        j2 = Job(
            recruiter_id=rp2.id,
            company_id=c2.id,
            title="Backend Python & AI Integration Engineer",
            description="PulseAI is hiring a Backend Engineer to build high-scale APIs connecting LLMs, vector indices, and customer relational data. You will architect resilient endpoints, optimize SQL queries, and implement automated data pipelines.",
            experience_level="mid",
            employment_type="full_time",
            location="New York, NY",
            is_remote=False,
            salary_min=95000.00,
            salary_max=125000.00,
            currency="USD",
            deadline=(now + timedelta(days=25)).date(),
            status="active",
            associated_challenge_id=ch2.id
        )
        j3 = Job(
            recruiter_id=rp3.id,
            company_id=c3.id,
            title="FinTech Backend API & Systems Engineer",
            description="Join QuantumPay to build the backbone of next-gen financial settlement networks. You will work on ACID-compliant ledger systems, idempotent API design, and high-concurrency database operations.",
            experience_level="mid",
            employment_type="full_time",
            location="London, UK",
            is_remote=True,
            salary_min=90000.00,
            salary_max=115000.00,
            currency="USD",
            deadline=(now + timedelta(days=20)).date(),
            status="active",
            associated_challenge_id=ch3.id
        )
        j4 = Job(
            recruiter_id=rp1.id,
            company_id=c1.id,
            title="Frontend UI/UX Web Engineer",
            description="NexaTech is searching for a detail-obsessed Frontend Developer. You will translate wireframes into pixel-perfect, accessible, and fast web experiences with clean JavaScript and CSS architecture.",
            experience_level="entry",
            employment_type="full_time",
            location="San Francisco, CA",
            is_remote=True,
            salary_min=72000.00,
            salary_max=90000.00,
            currency="USD",
            deadline=(now + timedelta(days=28)).date(),
            status="active",
            associated_challenge_id=ch4.id
        )
        j5 = Job(
            recruiter_id=rp2.id,
            company_id=c2.id,
            title="AI & Machine Learning Engineering Intern",
            description="A high-impact summer/fall internship for students passionate about machine learning, natural language processing, and practical recommendation algorithms. Work directly with senior staff research engineers.",
            experience_level="entry",
            employment_type="internship",
            location="New York, NY",
            is_remote=True,
            salary_min=45000.00,
            salary_max=60000.00,
            currency="USD",
            deadline=(now + timedelta(days=35)).date(),
            status="active",
            associated_challenge_id=ch2.id
        )
        j6 = Job(
            recruiter_id=rp1.id,
            company_id=c1.id,
            title="Cloud Infrastructure & DevOps Engineer",
            description="Help manage and automate our multi-region Kubernetes and Docker cloud deployments. Implement automated CI/CD pipelines, container security, and system observability.",
            experience_level="mid",
            employment_type="full_time",
            location="Austin, TX",
            is_remote=False,
            salary_min=105000.00,
            salary_max=135000.00,
            currency="USD",
            deadline=(now + timedelta(days=40)).date(),
            status="active",
            associated_challenge_id=ch5.id
        )
        db.session.add_all([j1, j2, j3, j4, j5, j6])
        db.session.commit()

        # Link job required skills
        def link_js(job_id, skill_weights):
            for name, is_mand, weight in skill_weights:
                sk = skills_map.get(name)
                if sk:
                    db.session.add(JobRequiredSkill(
                        job_id=job_id,
                        skill_id=sk.id,
                        is_mandatory=is_mand,
                        weight=weight
                    ))

        link_js(j1.id, [('Python', True, 3), ('Flask', True, 3), ('JavaScript', True, 2), ('MySQL', True, 3), ('HTML5', False, 1)])
        link_js(j2.id, [('Python', True, 3), ('REST APIs', True, 3), ('Machine Learning', True, 2), ('MySQL', True, 2)])
        link_js(j3.id, [('Python', True, 3), ('MySQL', True, 3), ('PostgreSQL', True, 2), ('Cybersecurity', True, 2)])
        link_js(j4.id, [('JavaScript', True, 3), ('HTML5', True, 3), ('CSS3', True, 3), ('UI/UX Design', True, 2)])
        link_js(j5.id, [('Python', True, 3), ('Machine Learning', True, 3), ('TensorFlow', False, 2)])
        link_js(j6.id, [('Docker', True, 3), ('Git', True, 2), ('AWS', True, 3)])
        db.session.commit()

        # 8. Applications
        app1 = Application(
            job_id=j1.id,
            student_id=sp1.id,
            status="Shortlisted",
            cover_letter="I am eager to contribute my full-stack Python/Flask and relational database experience to NexaTech. I completed the attendance portal challenge with 94/100 score.",
            applied_at=now - timedelta(days=5)
        )
        app2 = Application(
            job_id=j4.id,
            student_id=sp2.id,
            status="Under Review",
            cover_letter="Excited about crafting seamless interfaces for NexaTech. My Berkeley coursework and portfolio showcase strong vanilla JavaScript and responsive CSS capabilities.",
            applied_at=now - timedelta(days=3)
        )
        app3 = Application(
            job_id=j2.id,
            student_id=sp3.id,
            status="Assessment Pending",
            cover_letter="I have substantial background in database tuning and Python backend services at Georgia Tech. Look forward to taking the challenge!",
            applied_at=now - timedelta(days=2)
        )
        app4 = Application(
            job_id=j2.id,
            student_id=sp1.id,
            status="Applied",
            cover_letter="Passionate about intelligent recommendation algorithms and Python APIs. Looking forward to tackling the challenge assessment.",
            applied_at=now - timedelta(days=1)
        )
        db.session.add_all([app1, app2, app3, app4])
        db.session.commit()

        # 9. Submissions
        sub1 = Submission(
            challenge_id=ch1.id,
            student_id=sp1.id,
            application_id=app1.id,
            github_repo_url="https://github.com/alexrivera-demo/challengehire-attendance-portal",
            live_demo_url="https://attendance-demo.alexrivera.dev",
            project_file="alex_attendance_v1.zip",
            explanation="Architected a 3NF relational database schema with courses, students, and attendance sheets. Built RESTful Flask blueprint endpoints with parameterized queries, role checks, and an interactive Chart.js dashboard showing student percentage statistics. Implemented unit tests for negative input handling.",
            status="evaluated",
            score=94,
            feedback="Outstanding code quality! The database schema is fully normalized, queries use proper indexes, and the responsive UI handles edge cases cleanly. Strong recommendation for technical interview.",
            submitted_at=now - timedelta(days=4)
        )
        sub2 = Submission(
            challenge_id=ch4.id,
            student_id=sp2.id,
            application_id=app2.id,
            github_repo_url="https://github.com/samchen-code/challengehire-responsive-job-board",
            live_demo_url="https://jobs-demo.samchen.design",
            project_file="sam_jobboard_ui.zip",
            explanation="Designed an ultra-clean, accessible job board catalog using CSS Grid, custom properties, and native JavaScript state filtering. Includes smooth badge animations, empty-state placeholders, and mobile touch drawer navigation.",
            status="evaluated",
            score=92,
            feedback="Superb attention to detail and typography. Clean separation of concerns in CSS and zero external dependencies. Highly impressive work for an entry-level candidate.",
            submitted_at=now - timedelta(days=2)
        )
        db.session.add_all([sub1, sub2])
        db.session.commit()

        # 10. Evaluation Results (Rubrics)
        er1 = EvaluationResult(
            submission_id=sub1.id,
            code_quality_score=29,
            functionality_score=38,
            ui_ux_score=27,
            total_score=94,
            max_score=100,
            ai_suggested_score=92,
            ai_feedback="AI Assessment: Clean modular MVC structure. Schema adheres to 3NF standards. Input validation covers nulls and boundary IDs. Code demonstrates strong adherence to PEP 8 standards.",
            recruiter_comments="Excellent candidate with strong fundamentals in backend engineering and database design. Shortlisted for Round 2 technical interview."
        )
        er2 = EvaluationResult(
            submission_id=sub2.id,
            code_quality_score=28,
            functionality_score=36,
            ui_ux_score=28,
            total_score=92,
            max_score=100,
            ai_suggested_score=90,
            ai_feedback="AI Assessment: Semantic HTML structure verified. Accessible ARIA attributes present. Filter debouncing implemented properly. CSS variables provide consistent theming.",
            recruiter_comments="Great frontend sense and clean architectural style. Shortlisted for engineering review."
        )
        db.session.add_all([er1, er2])
        db.session.commit()

        # 11. Assessments & Questions
        as1 = Assessment(
            challenge_id=ch1.id,
            title="Web & Database Engineering Fundamentals",
            description="Verifies knowledge of SQL joins, HTTP methods, session management, and MVC architecture.",
            pass_percentage=60,
            duration_minutes=20
        )
        db.session.add(as1)
        db.session.commit()

        q1 = Question(
            assessment_id=as1.id,
            question_text="Which SQL constraint guarantees that values in a column are all unique across records and cannot be NULL?",
            question_type="mcq",
            options_json='["FOREIGN KEY", "PRIMARY KEY", "CHECK", "INDEX"]',
            correct_answer="PRIMARY KEY",
            points=10
        )
        q2 = Question(
            assessment_id=as1.id,
            question_text="In REST API design, which HTTP method should be idempotent and used to retrieve representation of a resource?",
            question_type="mcq",
            options_json='["POST", "GET", "PATCH", "DELETE"]',
            correct_answer="GET",
            points=10
        )
        q3 = Question(
            assessment_id=as1.id,
            question_text="What is the primary purpose of database indexing?",
            question_type="mcq",
            options_json='["Encrypt sensitive data", "Speed up data retrieval operations", "Enforce business logic", "Backup tables automatically"]',
            correct_answer="Speed up data retrieval operations",
            points=10
        )
        db.session.add_all([q1, q2, q3])
        db.session.commit()

        # 12. Recruiter Reviews
        rr1 = RecruiterReview(
            recruiter_id=rp1.id,
            student_id=sp1.id,
            application_id=app1.id,
            rating=5,
            review_notes="Alex demonstrated mastery in relational schema design and practical Flask implementation. Submission passed all criteria.",
            decision="shortlist"
        )
        rr2 = RecruiterReview(
            recruiter_id=rp1.id,
            student_id=sp2.id,
            application_id=app2.id,
            rating=5,
            review_notes="Samantha has top-tier UI design sensibility and clean coding style. Passed to engineering team lead.",
            decision="shortlist"
        )
        db.session.add_all([rr1, rr2])

        # 13. Notifications
        n1 = Notification(
            user_id=u_stu1.id,
            title="Challenge Evaluated!",
            message='Your submission for "Full-Stack Student Attendance & Portal System" was graded 94/100 by Sarah Jenkins.',
            link="/student/submissions",
            is_read=False
        )
        n2 = Notification(
            user_id=u_stu1.id,
            title="Application Shortlisted",
            message="Congratulations! NexaTech Solutions has updated your application status to Shortlisted.",
            link="/student/applications",
            is_read=False
        )
        n3 = Notification(
            user_id=u_rec1.id,
            title="New Application Received",
            message="Alex Rivera applied for Junior Full-Stack Web Developer.",
            link="/recruiter/applicants",
            is_read=True
        )
        db.session.add_all([n1, n2, n3])
        db.session.commit()

        print("ChallengeHire database successfully initialized and seeded!")

if __name__ == '__main__':
    from flask import Flask
    from config import Config
    
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.get_database_uri()
    db.init_app(app)
    seed_database(app)
