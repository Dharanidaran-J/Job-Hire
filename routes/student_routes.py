"""
ChallengeHire Student Routes
Handles Student Dashboard, Profile Management, Job Search & Application,
Challenge Participation & Submissions, Assessment Quiz, and AI Recommendations.
"""

import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, g, current_app
from werkzeug.utils import secure_filename

from models import (
    db, Job, Challenge, Application, Submission, StudentProfile,
    Skill, StudentSkill, Assessment, AssessmentAttempt, EvaluationResult,
    Notification, RecruiterProfile, Company
)
from routes.auth_routes import student_required
from ai.matcher import calculate_skill_match
from ai.recommender import recommend_challenges_for_student, recommend_jobs_for_student, get_skill_gap_action_plan
from ai.evaluator import evaluate_project_submission, grade_quiz_attempt

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/dashboard')
@student_required
def dashboard():
    student = g.profile
    if not student:
        flash('Student profile not found.', 'danger')
        return redirect(url_for('main.index'))
        
    all_challenges = Challenge.query.all()
    all_jobs = Job.query.all()
    
    # 1. AI Recommended Challenges
    ai_challenges = recommend_challenges_for_student(student, all_challenges, limit=3)
    
    # 2. AI Recommended Jobs
    ai_jobs = recommend_jobs_for_student(student, all_jobs, limit=4)
    
    # 3. Applied Jobs
    applications = student.applications.order_by(Application.applied_at.desc()).limit(5).all()
    
    # 4. Submissions History
    submissions = student.submissions.order_by(Submission.submitted_at.desc()).limit(5).all()
    
    # 5. Skills Summary
    skills = student.student_skills.join(Skill).all()
    
    # Statistics counts
    stats = {
        'total_applied': student.applications.count(),
        'total_submitted': student.submissions.count(),
        'avg_score': 0,
        'verified_skills': sum(1 for s in skills if s.verified)
    }
    
    evaluated_subs = [s for s in submissions if s.score and s.score > 0]
    if evaluated_subs:
        stats['avg_score'] = round(sum(s.score for s in evaluated_subs) / len(evaluated_subs))
        
    return render_template('student/dashboard.html',
                           student=student,
                           stats=stats,
                           ai_challenges=ai_challenges,
                           ai_jobs=ai_jobs,
                           applications=applications,
                           submissions=submissions,
                           skills=skills)


@student_bp.route('/profile', methods=['GET', 'POST'])
@student_required
def profile():
    student = g.profile
    all_skills = Skill.query.order_by(Skill.name).all()
    
    if request.method == 'POST':
        student.full_name = request.form.get('full_name', student.full_name).strip()
        student.college_name = request.form.get('college_name', student.college_name).strip()
        student.degree = request.form.get('degree', student.degree).strip()
        grad_year = request.form.get('graduation_year', '').strip()
        if grad_year.isdigit():
            student.graduation_year = int(grad_year)
        student.bio = request.form.get('bio', student.bio).strip()
        student.github_url = request.form.get('github_url', student.github_url).strip()
        student.portfolio_url = request.form.get('portfolio_url', student.portfolio_url).strip()
        student.linkedin_url = request.form.get('linkedin_url', student.linkedin_url).strip()
        
        # Update skills
        selected_skill_ids = request.form.getlist('skills')
        StudentSkill.query.filter_by(student_id=student.id).delete()
        
        for s_id in selected_skill_ids:
            if s_id.isdigit():
                db.session.add(StudentSkill(
                    student_id=student.id,
                    skill_id=int(s_id),
                    proficiency_level=request.form.get(f'prof_{s_id}', 'intermediate'),
                    verified=False,
                    score_earned=0
                ))
                
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('student.profile'))
        
    current_skill_ids = {ss.skill_id: ss.proficiency_level for ss in student.student_skills.all()}
    return render_template('student/profile.html',
                           student=student,
                           all_skills=all_skills,
                           current_skill_ids=current_skill_ids)


@student_bp.route('/jobs')
@student_required
def jobs():
    student = g.profile
    search_query = request.args.get('q', '').strip()
    experience = request.args.get('experience', '')
    is_remote = request.args.get('remote', '')
    skill_filter = request.args.get('skill', '')
    
    query = Job.query.filter_by(status='active')
    
    if search_query:
        query = query.filter(Job.title.ilike(f'%{search_query}%') | Job.description.ilike(f'%{search_query}%'))
        
    if experience:
        query = query.filter_by(experience_level=experience)
        
    if is_remote == '1':
        query = query.filter_by(is_remote=True)
        
    raw_jobs = query.order_by(Job.created_at.desc()).all()
    
    # Calculate AI Match score for each job
    student_skills_dict = {
        ss.skill.name: {'proficiency': ss.proficiency_level, 'verified': ss.verified}
        for ss in student.student_skills.all()
    }
    
    applied_job_ids = {app.job_id: app.status for app in student.applications.all()}
    
    job_cards = []
    for job in raw_jobs:
        req_skills = [
            {'name': jrs.skill.name, 'is_mandatory': jrs.is_mandatory, 'weight': jrs.weight}
            for jrs in job.required_skills.all()
        ]
        
        if skill_filter and not any(s['name'].lower() == skill_filter.lower() for s in req_skills):
            continue
            
        match_data = calculate_skill_match(student_skills_dict, req_skills)
        job_cards.append({
            'job': job,
            'match_data': match_data,
            'is_applied': job.id in applied_job_ids,
            'application_status': applied_job_ids.get(job.id)
        })
        
    # Sort by match percentage
    job_cards.sort(key=lambda x: x['match_data']['match_percentage'], reverse=True)
    all_skills = Skill.query.order_by(Skill.name).all()
    
    return render_template('student/jobs.html',
                           job_cards=job_cards,
                           all_skills=all_skills,
                           search_query=search_query,
                           experience=experience,
                           is_remote=is_remote,
                           skill_filter=skill_filter)


@student_bp.route('/jobs/<int:job_id>')
@student_required
def job_detail(job_id):
    student = g.profile
    job = Job.query.get_or_404(job_id)
    
    # Check application status
    application = Application.query.filter_by(job_id=job.id, student_id=student.id).first()
    
    # Calculate detailed AI match breakdown
    student_skills_dict = {
        ss.skill.name: {'proficiency': ss.proficiency_level, 'verified': ss.verified}
        for ss in student.student_skills.all()
    }
    req_skills = [
        {'name': jrs.skill.name, 'is_mandatory': jrs.is_mandatory, 'weight': jrs.weight}
        for jrs in job.required_skills.all()
    ]
    match_data = calculate_skill_match(student_skills_dict, req_skills)
    
    # Check if student already submitted associated challenge
    associated_submission = None
    if job.associated_challenge_id:
        associated_submission = Submission.query.filter_by(
            challenge_id=job.associated_challenge_id,
            student_id=student.id
        ).first()

    return render_template('student/job_detail.html',
                           job=job,
                           application=application,
                           match_data=match_data,
                           associated_submission=associated_submission)


@student_bp.route('/jobs/<int:job_id>/apply', methods=['POST'])
@student_required
def apply_job(job_id):
    student = g.profile
    job = Job.query.get_or_404(job_id)
    
    # Prevent duplicate applications
    existing = Application.query.filter_by(job_id=job.id, student_id=student.id).first()
    if existing:
        flash('You have already applied for this job opening.', 'info')
        return redirect(url_for('student.job_detail', job_id=job.id))
        
    cover_letter = request.form.get('cover_letter', '').strip()
    
    # If job has an associated challenge, default status to Assessment Pending
    initial_status = 'Assessment Pending' if job.associated_challenge_id else 'Applied'
    
    new_app = Application(
        job_id=job.id,
        student_id=student.id,
        status=initial_status,
        cover_letter=cover_letter
    )
    db.session.add(new_app)
    
    # Notify Recruiter
    if job.recruiter:
        db.session.add(Notification(
            user_id=job.recruiter.user_id,
            title='New Application Received',
            message=f'{student.full_name} has applied for {job.title}.',
            link=f'/recruiter/applicants?job_id={job.id}'
        ))
        
    db.session.commit()
    flash(f'Application successfully submitted for {job.title}!', 'success')
    return redirect(url_for('student.job_detail', job_id=job.id))


@student_bp.route('/challenges')
@student_required
def challenges():
    student = g.profile
    difficulty = request.args.get('difficulty', '')
    search = request.args.get('q', '').strip()
    
    query = Challenge.query.filter_by(status='active')
    if difficulty:
        query = query.filter_by(difficulty_level=difficulty)
    if search:
        query = query.filter(Challenge.title.ilike(f'%{search}%') | Challenge.problem_statement.ilike(f'%{search}%'))
        
    all_challenges = query.order_by(Challenge.created_at.desc()).all()
    
    # Get student's submission status for each challenge
    submissions_map = {s.challenge_id: s for s in student.submissions.all()}
    
    challenge_items = []
    for ch in all_challenges:
        sub = submissions_map.get(ch.id)
        challenge_items.append({
            'challenge': ch,
            'submission': sub,
            'is_submitted': sub is not None,
            'score': sub.score if sub else None
        })
        
    return render_template('student/challenges.html',
                           challenge_items=challenge_items,
                           difficulty=difficulty,
                           search=search)


@student_bp.route('/challenges/<int:challenge_id>')
@student_required
def challenge_detail(challenge_id):
    student = g.profile
    challenge = Challenge.query.get_or_404(challenge_id)
    submission = Submission.query.filter_by(challenge_id=challenge.id, student_id=student.id).first()
    assessment = challenge.assessments.first()
    
    return render_template('student/challenge_detail.html',
                           challenge=challenge,
                           submission=submission,
                           assessment=assessment)


@student_bp.route('/challenges/<int:challenge_id>/submit', methods=['POST'])
@student_required
def submit_challenge(challenge_id):
    student = g.profile
    challenge = Challenge.query.get_or_404(challenge_id)
    
    github_url = request.form.get('github_repo_url', '').strip()
    live_demo_url = request.form.get('live_demo_url', '').strip()
    explanation = request.form.get('explanation', '').strip()
    
    if not github_url and not live_demo_url and not explanation:
        flash('Please provide at least a GitHub link or a detailed project explanation.', 'danger')
        return redirect(url_for('student.challenge_detail', challenge_id=challenge.id))
        
    # Handle optional project file upload
    project_filename = None
    if 'project_file' in request.files:
        file = request.files['project_file']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            save_path = os.path.join(upload_dir, f"{student.id}_{challenge.id}_{filename}")
            file.save(save_path)
            project_filename = filename

    # Check existing submission or create new
    submission = Submission.query.filter_by(challenge_id=challenge.id, student_id=student.id).first()
    if not submission:
        submission = Submission(
            challenge_id=challenge.id,
            student_id=student.id
        )
        db.session.add(submission)
        
    submission.github_repo_url = github_url
    submission.live_demo_url = live_demo_url
    if project_filename:
        submission.project_file = project_filename
    submission.explanation = explanation
    submission.submitted_at = datetime.utcnow()
    submission.status = 'evaluating'
    
    db.session.flush()

    # Link with job application if challenge is linked to a job applied by this student
    if challenge.jobs:
        for j in challenge.jobs:
            app = Application.query.filter_by(job_id=j.id, student_id=student.id).first()
            if app:
                submission.application_id = app.id
                if app.status == 'Assessment Pending':
                    app.status = 'Under Review'
                break

    # Run AI-assisted evaluation
    gemini_key = current_app.config.get('GEMINI_API_KEY')
    eval_output = evaluate_project_submission(challenge, github_url, live_demo_url, explanation, gemini_key)
    
    submission.score = eval_output['total_score']
    submission.feedback = eval_output['ai_feedback']
    submission.status = 'evaluated'
    
    # Save or update EvaluationResult
    eval_result = submission.evaluation
    if not eval_result:
        eval_result = EvaluationResult(submission_id=submission.id)
        db.session.add(eval_result)
        
    eval_result.code_quality_score = eval_output['code_quality_score']
    eval_result.functionality_score = eval_output['functionality_score']
    eval_result.ui_ux_score = eval_output['ui_ux_score']
    eval_result.total_score = eval_output['total_score']
    eval_result.ai_suggested_score = eval_output.get('ai_suggested_score', eval_output['total_score'])
    eval_result.ai_feedback = eval_output['ai_feedback']
    eval_result.evaluated_at = datetime.utcnow()
    
    # Automatically verify related student skills if score >= 75
    if eval_output['total_score'] >= 75:
        for crs in challenge.required_skills.all():
            st_skill = StudentSkill.query.filter_by(student_id=student.id, skill_id=crs.skill_id).first()
            if st_skill:
                st_skill.verified = True
                st_skill.score_earned = max(st_skill.score_earned or 0, eval_output['total_score'])
            else:
                # Add as verified skill
                db.session.add(StudentSkill(
                    student_id=student.id,
                    skill_id=crs.skill_id,
                    proficiency_level='intermediate',
                    verified=True,
                    score_earned=eval_output['total_score']
                ))

    # Send Notification to student
    db.session.add(Notification(
        user_id=student.user_id,
        title='Challenge Evaluated',
        message=f'Your submission for "{challenge.title}" received a score of {eval_output["total_score"]}/100.',
        link=f'/student/submissions'
    ))

    # Notify Recruiter if applicable
    if challenge.recruiter:
        db.session.add(Notification(
            user_id=challenge.recruiter.user_id,
            title='New Challenge Submission',
            message=f'{student.full_name} submitted work for "{challenge.title}". AI suggested score: {eval_output["total_score"]}/100.',
            link='/recruiter/applicants'
        ))

    db.session.commit()
    flash('Challenge submitted and evaluated successfully! Check your feedback and score below.', 'success')
    return redirect(url_for('student.challenge_detail', challenge_id=challenge.id))


@student_bp.route('/applications')
@student_required
def my_applications():
    student = g.profile
    applications = student.applications.order_by(Application.applied_at.desc()).all()
    return render_template('student/my_applications.html', applications=applications)


@student_bp.route('/submissions')
@student_required
def my_submissions():
    student = g.profile
    submissions = student.submissions.order_by(Submission.submitted_at.desc()).all()
    return render_template('student/my_submissions.html', submissions=submissions)


@student_bp.route('/skill-gap/<int:job_id>')
@student_required
def skill_gap(job_id):
    student = g.profile
    job = Job.query.get_or_404(job_id)
    all_challenges = Challenge.query.filter_by(status='active').all()
    
    gap_plan = get_skill_gap_action_plan(student, job, all_challenges)
    return render_template('student/skill_gap.html', gap_plan=gap_plan)
