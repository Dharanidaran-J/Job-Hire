"""
ChallengeHire Main Public Routes
Landing page with live database statistics, featured jobs & challenges,
How It Works, benefits, and informational pages.
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from models import db, Job, Challenge, Company, StudentProfile, Submission, StudentSkill

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # 1. Fetch real live database statistics
    stats = {
        'total_jobs': Job.query.filter_by(status='active').count(),
        'total_challenges': Challenge.query.filter_by(status='active').count(),
        'total_companies': Company.query.count(),
        'total_submissions': Submission.query.count(),
        'total_verified_skills': StudentSkill.query.filter_by(verified=True).count()
    }
    
    # 2. Featured Jobs (latest 4 active jobs with company & skills)
    featured_jobs = Job.query.filter_by(status='active').order_by(Job.created_at.desc()).limit(4).all()
    
    # 3. Popular Challenges (latest 3 active challenges)
    popular_challenges = Challenge.query.filter_by(status='active').order_by(Challenge.created_at.desc()).limit(3).all()
    
    return render_template('index.html',
                           stats=stats,
                           featured_jobs=featured_jobs,
                           popular_challenges=popular_challenges)


@main_bp.route('/about')
def about():
    return render_template('about.html')


@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        flash('Thank you for reaching out! Our team will get back to you shortly.', 'success')
        return redirect(url_for('main.contact'))
    return render_template('contact.html')


@main_bp.route('/privacy')
def privacy():
    return render_template('privacy.html')
