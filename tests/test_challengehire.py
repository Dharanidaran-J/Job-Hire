"""
ChallengeHire - Automated Test Suite
Covers Authentication, Role-based Access, Database Operations,
Duplicate Application Prevention, Challenge Submissions, and AI Skill Matching.
"""

import unittest
import os
import sys

# Ensure parent directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from config import Config
from models import db, User, StudentProfile, RecruiterProfile, Company, Skill, Job, Challenge, Application, Submission
from ai.matcher import calculate_skill_match

class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    # Use isolated in-memory or temporary SQLite database for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    USE_SQLITE_FALLBACK = True

class ChallengeHireTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_database_initialization(self):
        """Test database tables and models exist."""
        skills_count = Skill.query.count()
        self.assertGreater(skills_count, 0, "Initial seed data should populate skills catalog.")

    def test_student_registration_and_login(self):
        """Test student registration and secure password checking."""
        response = self.client.post('/register/student', data={
            'full_name': 'Test Candidate',
            'email': 'candidate.test@student.edu',
            'password': 'securepassword123',
            'confirm_password': 'securepassword123',
            'college_name': 'Tech Institute',
            'degree': 'B.S. Software Eng',
            'graduation_year': '2026',
            'bio': 'Passionate builder'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        user = User.query.filter_by(email='candidate.test@student.edu').first()
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password('securepassword123'))
        self.assertEqual(user.role, 'student')
        self.assertEqual(user.student_profile.full_name, 'Test Candidate')

    def test_unauthorized_dashboard_access(self):
        """Test that unauthenticated users are redirected from protected dashboards."""
        # Unauthenticated student dashboard access
        resp_student = self.client.get('/student/dashboard', follow_redirects=False)
        self.assertEqual(resp_student.status_code, 302)
        self.assertIn('/login', resp_student.headers['Location'])

        # Unauthenticated recruiter dashboard access
        resp_rec = self.client.get('/recruiter/dashboard', follow_redirects=False)
        self.assertEqual(resp_rec.status_code, 302)
        self.assertIn('/login', resp_rec.headers['Location'])

    def test_prevent_duplicate_job_application(self):
        """Test that candidate cannot apply more than once to the same job opening."""
        # Log in as pre-seeded student Alex Rivera
        self.client.post('/login', data={
            'email': 'alex.rivera@student.edu',
            'password': 'password123'
        }, follow_redirects=True)

        job = Job.query.first()
        student = User.query.filter_by(email='alex.rivera@student.edu').first().student_profile

        # Existing application might already exist from seed data for job 1
        existing_app = Application.query.filter_by(job_id=job.id, student_id=student.id).first()
        if not existing_app:
            # Apply first time
            res1 = self.client.post(f'/student/jobs/{job.id}/apply', data={'cover_letter': 'First application'}, follow_redirects=True)
            self.assertEqual(res1.status_code, 200)

        # Apply second time - should be prevented
        res2 = self.client.post(f'/student/jobs/{job.id}/apply', data={'cover_letter': 'Duplicate attempt'}, follow_redirects=True)
        self.assertIn(b'already applied', res2.data.lower())

    def test_challenge_submission_and_rubric_evaluation(self):
        """Test practical challenge submission triggers rubric scoring and feedback."""
        # Log in as Alex
        self.client.post('/login', data={
            'email': 'alex.rivera@student.edu',
            'password': 'password123'
        }, follow_redirects=True)

        challenge = Challenge.query.first()
        
        resp = self.client.post(f'/student/challenges/{challenge.id}/submit', data={
            'github_repo_url': 'https://github.com/alexrivera-demo/attendance-portal-v2',
            'live_demo_url': 'https://attendance-demo-v2.vercel.app',
            'explanation': 'Implemented normalized MySQL schema, REST APIs with Flask blueprints, unit tests, and clean architecture.'
        }, follow_redirects=True)
        
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'evaluated successfully', resp.data.lower())
        
        sub = Submission.query.filter_by(challenge_id=challenge.id).order_by(Submission.submitted_at.desc()).first()
        self.assertIsNotNone(sub)
        self.assertGreaterEqual(sub.score, 60)
        self.assertIsNotNone(sub.evaluation)
        self.assertGreater(sub.evaluation.total_score, 0)

    def test_ai_skill_matching_engine(self):
        """Test accuracy of the AI skill matching algorithm."""
        candidate_skills = {
            'python': {'proficiency': 'advanced', 'verified': True},
            'flask': {'proficiency': 'advanced', 'verified': True},
            'mysql': {'proficiency': 'intermediate', 'verified': False}
        }
        
        job_skills = [
            {'name': 'Python', 'is_mandatory': True, 'weight': 3},
            {'name': 'Flask', 'is_mandatory': True, 'weight': 3},
            {'name': 'MySQL', 'is_mandatory': True, 'weight': 2},
            {'name': 'Docker', 'is_mandatory': False, 'weight': 1}
        ]
        
        result = calculate_skill_match(candidate_skills, job_skills)
        self.assertGreaterEqual(result['match_percentage'], 70)
        self.assertEqual(result['matched_count'], 3)
        self.assertEqual(result['missing_count'], 1)
        self.assertEqual(result['missing_skills'][0]['name'], 'Docker')

if __name__ == '__main__':
    unittest.main()
