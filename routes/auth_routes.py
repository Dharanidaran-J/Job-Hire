"""
ChallengeHire Authentication Routes & Access Control Decorators
Handles registration, login, logout, password hashing, and role-based protection.
"""

from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from models import db, User, StudentProfile, RecruiterProfile, Company, Skill, StudentSkill

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in as a student to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        if session.get('user_role') != 'student':
            flash('Access denied: Student privilege required.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def recruiter_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in as a recruiter to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        if session.get('user_role') != 'recruiter':
            flash('Access denied: Recruiter privilege required.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
        g.profile = None
    else:
        g.user = User.query.get(user_id)
        if g.user:
            if g.user.role == 'student':
                g.profile = g.user.student_profile
            elif g.user.role == 'recruiter':
                g.profile = g.user.recruiter_profile
            else:
                g.profile = None
        else:
            g.profile = None

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if g.user:
        if g.user.role == 'student':
            return redirect(url_for('student.dashboard'))
        elif g.user.role == 'recruiter':
            return redirect(url_for('recruiter.dashboard'))
            
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash('Invalid email or password. Please try again.', 'danger')
            return render_template('auth/login.html', email=email)
            
        if not user.is_active:
            flash('Your account has been deactivated. Please contact support.', 'danger')
            return render_template('auth/login.html')
            
        # Store in session
        session.clear()
        session['user_id'] = user.id
        session['user_role'] = user.role
        session['user_email'] = user.email
        
        user_name = "User"
        if user.role == 'student' and user.student_profile:
            user_name = user.student_profile.full_name
        elif user.role == 'recruiter' and user.recruiter_profile:
            user_name = user.recruiter_profile.full_name
        session['user_name'] = user_name
        
        flash(f'Welcome back, {user_name}!', 'success')
        
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
            
        if user.role == 'student':
            return redirect(url_for('student.dashboard'))
        elif user.role == 'recruiter':
            return redirect(url_for('recruiter.dashboard'))
        else:
            return redirect(url_for('main.index'))
            
    return render_template('auth/login.html')


@auth_bp.route('/register/student', methods=['GET', 'POST'])
def register_student():
    if g.user:
        return redirect(url_for('main.index'))
        
    all_skills = Skill.query.order_by(Skill.name).all()
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip()
        college_name = request.form.get('college_name', '').strip()
        degree = request.form.get('degree', '').strip()
        grad_year = request.form.get('graduation_year', '').strip()
        bio = request.form.get('bio', '').strip()
        github_url = request.form.get('github_url', '').strip()
        portfolio_url = request.form.get('portfolio_url', '').strip()
        selected_skills = request.form.getlist('skills') # skill ids
        
        if not email or not password or not full_name or not college_name:
            flash('Please fill in all mandatory fields.', 'danger')
            return render_template('auth/register_student.html', all_skills=all_skills)
            
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register_student.html', all_skills=all_skills)
            
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('auth/register_student.html', all_skills=all_skills)
            
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with this email already exists.', 'warning')
            return render_template('auth/register_student.html', all_skills=all_skills)
            
        # Create user
        new_user = User(email=email, role='student')
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()
        
        # Create student profile
        new_profile = StudentProfile(
            user_id=new_user.id,
            full_name=full_name,
            college_name=college_name,
            degree=degree,
            graduation_year=int(grad_year) if grad_year.isdigit() else None,
            bio=bio,
            github_url=github_url,
            portfolio_url=portfolio_url
        )
        db.session.add(new_profile)
        db.session.flush()
        
        # Add skills
        for s_id in selected_skills:
            if s_id.isdigit():
                db.session.add(StudentSkill(
                    student_id=new_profile.id,
                    skill_id=int(s_id),
                    proficiency_level='intermediate',
                    verified=False,
                    score_earned=0
                ))
                
        db.session.commit()
        
        # Log user in
        session['user_id'] = new_user.id
        session['user_role'] = new_user.role
        session['user_email'] = new_user.email
        session['user_name'] = full_name
        
        flash('Account created successfully! Welcome to ChallengeHire.', 'success')
        return redirect(url_for('student.dashboard'))
        
    return render_template('auth/register_student.html', all_skills=all_skills)


@auth_bp.route('/register/recruiter', methods=['GET', 'POST'])
def register_recruiter():
    if g.user:
        return redirect(url_for('main.index'))
        
    companies = Company.query.order_by(Company.name).all()
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip()
        designation = request.form.get('designation', '').strip()
        phone = request.form.get('phone', '').strip()
        
        company_choice = request.form.get('company_choice', 'existing')
        company_id = request.form.get('company_id')
        new_company_name = request.form.get('new_company_name', '').strip()
        new_company_location = request.form.get('new_company_location', '').strip()
        new_company_industry = request.form.get('new_company_industry', '').strip()
        new_company_website = request.form.get('new_company_website', '').strip()
        
        if not email or not password or not full_name or not designation:
            flash('Please fill in all mandatory recruiter details.', 'danger')
            return render_template('auth/register_recruiter.html', companies=companies)
            
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register_recruiter.html', companies=companies)
            
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with this official email already exists.', 'warning')
            return render_template('auth/register_recruiter.html', companies=companies)
            
        # Handle company
        final_company_id = None
        if company_choice == 'new' and new_company_name:
            new_comp = Company(
                name=new_company_name,
                location=new_company_location or 'Global / Remote',
                industry=new_company_industry or 'Technology',
                website=new_company_website
            )
            db.session.add(new_comp)
            db.session.flush()
            final_company_id = new_comp.id
        elif company_id and company_id.isdigit():
            final_company_id = int(company_id)
        else:
            # Fallback to first company or create one
            first_c = Company.query.first()
            if first_c:
                final_company_id = first_c.id
            else:
                new_comp = Company(name="Tech Innovators Inc", location="Remote", industry="Technology")
                db.session.add(new_comp)
                db.session.flush()
                final_company_id = new_comp.id

        # Create user
        new_user = User(email=email, role='recruiter')
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()
        
        # Create recruiter profile
        new_profile = RecruiterProfile(
            user_id=new_user.id,
            company_id=final_company_id,
            full_name=full_name,
            official_email=email,
            designation=designation,
            phone=phone
        )
        db.session.add(new_profile)
        db.session.commit()
        
        # Log user in
        session['user_id'] = new_user.id
        session['user_role'] = new_user.role
        session['user_email'] = new_user.email
        session['user_name'] = full_name
        
        flash('Recruiter account created successfully! Start posting jobs and practical challenges.', 'success')
        return redirect(url_for('recruiter.dashboard'))
        
    return render_template('auth/register_recruiter.html', companies=companies)


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))
