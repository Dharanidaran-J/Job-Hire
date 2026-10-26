"""
ChallengeHire Recruiter Routes
Handles Recruiter Dashboard, Job & Challenge Management, Applicant Review,
Manual & AI-Assisted Submission Grading, Candidate Comparison, and Status Transitions.
"""

from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, g, jsonify
from models import (
    db, Job, Challenge, Application, Submission, StudentProfile,
    Skill, JobRequiredSkill, ChallengeRequiredSkill, EvaluationResult,
    RecruiterReview, Notification
)
from routes.auth_routes import recruiter_required
from ai.comparator import compare_candidates_for_job

recruiter_bp = Blueprint('recruiter', __name__, url_prefix='/recruiter')

@recruiter_bp.route('/dashboard')
@recruiter_required
def dashboard():
    recruiter = g.profile
    if not recruiter:
        flash('Recruiter profile not found.', 'danger')
        return redirect(url_for('main.index'))
        
    jobs = recruiter.jobs.order_by(Job.created_at.desc()).all()
    job_ids = [j.id for j in jobs]
    
    # Applicants for this recruiter's jobs
    applications = Application.query.filter(Application.job_id.in_(job_ids)).order_by(Application.applied_at.desc()).all() if job_ids else []
    
    # Submissions for challenges created by this recruiter
    recruiter_challenges = recruiter.challenges.all()
    challenge_ids = [c.id for c in recruiter_challenges]
    submissions = Submission.query.filter(Submission.challenge_id.in_(challenge_ids)).order_by(Submission.submitted_at.desc()).all() if challenge_ids else []
    
    # Calculate KPI Statistics
    total_jobs = len(jobs)
    total_applicants = len(applications)
    pending_apps = sum(1 for a in applications if a.status in ('Applied', 'Assessment Pending', 'Under Review'))
    completed_assessments = sum(1 for s in submissions if s.status == 'evaluated')
    
    stats = {
        'total_jobs': total_jobs,
        'total_applicants': total_applicants,
        'pending_applications': pending_apps,
        'completed_assessments': completed_assessments,
        'shortlisted_count': sum(1 for a in applications if a.status == 'Shortlisted'),
        'selected_count': sum(1 for a in applications if a.status == 'Selected')
    }
    
    # Recent applicants
    recent_applicants = applications[:5]
    
    return render_template('recruiter/dashboard.html',
                           recruiter=recruiter,
                           stats=stats,
                           jobs=jobs,
                           recent_applicants=recent_applicants,
                           challenges=recruiter_challenges)


@recruiter_bp.route('/jobs')
@recruiter_required
def manage_jobs():
    recruiter = g.profile
    jobs = recruiter.jobs.order_by(Job.created_at.desc()).all()
    return render_template('recruiter/manage_jobs.html', jobs=jobs)


@recruiter_bp.route('/jobs/new', methods=['GET', 'POST'])
@recruiter_required
def create_job():
    recruiter = g.profile
    all_skills = Skill.query.order_by(Skill.name).all()
    challenges = recruiter.challenges.filter_by(status='active').all()
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        experience_level = request.form.get('experience_level', 'entry')
        employment_type = request.form.get('employment_type', 'full_time')
        location = request.form.get('location', '').strip()
        is_remote = bool(request.form.get('is_remote'))
        salary_min = request.form.get('salary_min') or None
        salary_max = request.form.get('salary_max') or None
        associated_challenge_id = request.form.get('associated_challenge_id') or None
        
        if not title or not description or not location:
            flash('Please complete all required fields.', 'danger')
            return render_template('recruiter/post_job.html', all_skills=all_skills, challenges=challenges)
            
        new_job = Job(
            recruiter_id=recruiter.id,
            company_id=recruiter.company_id,
            title=title,
            description=description,
            experience_level=experience_level,
            employment_type=employment_type,
            location=location,
            is_remote=is_remote,
            salary_min=salary_min,
            salary_max=salary_max,
            associated_challenge_id=associated_challenge_id if associated_challenge_id and associated_challenge_id.isdigit() else None,
            status='active'
        )
        db.session.add(new_job)
        db.session.flush()
        
        # Add required skills
        selected_skills = request.form.getlist('skills')
        for s_id in selected_skills:
            if s_id.isdigit():
                is_mandatory = bool(request.form.get(f'mandatory_{s_id}'))
                weight = int(request.form.get(f'weight_{s_id}', 2))
                db.session.add(JobRequiredSkill(
                    job_id=new_job.id,
                    skill_id=int(s_id),
                    is_mandatory=is_mandatory,
                    weight=weight
                ))
                
        db.session.commit()
        flash(f'Job opening "{title}" published successfully!', 'success')
        return redirect(url_for('recruiter.manage_jobs'))
        
    return render_template('recruiter/post_job.html', all_skills=all_skills, challenges=challenges, job=None)


@recruiter_bp.route('/jobs/<int:job_id>/edit', methods=['GET', 'POST'])
@recruiter_required
def edit_job(job_id):
    recruiter = g.profile
    job = Job.query.filter_by(id=job_id, recruiter_id=recruiter.id).first_or_404()
    all_skills = Skill.query.order_by(Skill.name).all()
    challenges = recruiter.challenges.filter_by(status='active').all()
    
    if request.method == 'POST':
        job.title = request.form.get('title', job.title).strip()
        job.description = request.form.get('description', job.description).strip()
        job.experience_level = request.form.get('experience_level', job.experience_level)
        job.employment_type = request.form.get('employment_type', job.employment_type)
        job.location = request.form.get('location', job.location).strip()
        job.is_remote = bool(request.form.get('is_remote'))
        job.salary_min = request.form.get('salary_min') or None
        job.salary_max = request.form.get('salary_max') or None
        job.status = request.form.get('status', job.status)
        
        ch_id = request.form.get('associated_challenge_id')
        job.associated_challenge_id = int(ch_id) if ch_id and ch_id.isdigit() else None
        
        # Update skills
        JobRequiredSkill.query.filter_by(job_id=job.id).delete()
        selected_skills = request.form.getlist('skills')
        for s_id in selected_skills:
            if s_id.isdigit():
                is_mandatory = bool(request.form.get(f'mandatory_{s_id}'))
                weight = int(request.form.get(f'weight_{s_id}', 2))
                db.session.add(JobRequiredSkill(
                    job_id=job.id,
                    skill_id=int(s_id),
                    is_mandatory=is_mandatory,
                    weight=weight
                ))
                
        db.session.commit()
        flash('Job opening updated successfully!', 'success')
        return redirect(url_for('recruiter.manage_jobs'))
        
    current_skill_ids = {jrs.skill_id: {'mandatory': jrs.is_mandatory, 'weight': jrs.weight} for jrs in job.required_skills.all()}
    return render_template('recruiter/post_job.html',
                           all_skills=all_skills,
                           challenges=challenges,
                           job=job,
                           current_skill_ids=current_skill_ids)


@recruiter_bp.route('/jobs/<int:job_id>/toggle', methods=['POST'])
@recruiter_required
def toggle_job_status(job_id):
    recruiter = g.profile
    job = Job.query.filter_by(id=job_id, recruiter_id=recruiter.id).first_or_404()
    job.status = 'closed' if job.status == 'active' else 'active'
    db.session.commit()
    flash(f'Job "{job.title}" status changed to {job.status.title()}.', 'info')
    return redirect(url_for('recruiter.manage_jobs'))


@recruiter_bp.route('/challenges')
@recruiter_required
def manage_challenges():
    recruiter = g.profile
    challenges = recruiter.challenges.order_by(Challenge.created_at.desc()).all()
    return render_template('recruiter/manage_challenges.html', challenges=challenges)


@recruiter_bp.route('/challenges/new', methods=['GET', 'POST'])
@recruiter_required
def create_challenge():
    recruiter = g.profile
    all_skills = Skill.query.order_by(Skill.name).all()
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        problem_statement = request.form.get('problem_statement', '').strip()
        instructions = request.form.get('instructions', '').strip()
        difficulty_level = request.form.get('difficulty_level', 'intermediate')
        max_score = int(request.form.get('max_score', 100))
        evaluation_criteria = request.form.get('evaluation_criteria', '').strip()
        
        if not title or not problem_statement or not instructions or not evaluation_criteria:
            flash('Please complete all challenge specifications.', 'danger')
            return render_template('recruiter/create_challenge.html', all_skills=all_skills, challenge=None)
            
        new_ch = Challenge(
            recruiter_id=recruiter.id,
            title=title,
            problem_statement=problem_statement,
            instructions=instructions,
            difficulty_level=difficulty_level,
            max_score=max_score,
            evaluation_criteria=evaluation_criteria,
            status='active'
        )
        db.session.add(new_ch)
        db.session.flush()
        
        # Link skills
        selected_skills = request.form.getlist('skills')
        for s_id in selected_skills:
            if s_id.isdigit():
                db.session.add(ChallengeRequiredSkill(
                    challenge_id=new_ch.id,
                    skill_id=int(s_id)
                ))
                
        db.session.commit()
        flash(f'Practical Challenge "{title}" created successfully!', 'success')
        return redirect(url_for('recruiter.manage_challenges'))
        
    return render_template('recruiter/create_challenge.html', all_skills=all_skills, challenge=None)


@recruiter_bp.route('/challenges/<int:challenge_id>/edit', methods=['GET', 'POST'])
@recruiter_required
def edit_challenge(challenge_id):
    recruiter = g.profile
    challenge = Challenge.query.filter_by(id=challenge_id, recruiter_id=recruiter.id).first_or_404()
    all_skills = Skill.query.order_by(Skill.name).all()
    
    if request.method == 'POST':
        challenge.title = request.form.get('title', challenge.title).strip()
        challenge.problem_statement = request.form.get('problem_statement', challenge.problem_statement).strip()
        challenge.instructions = request.form.get('instructions', challenge.instructions).strip()
        challenge.difficulty_level = request.form.get('difficulty_level', challenge.difficulty_level)
        challenge.max_score = int(request.form.get('max_score', challenge.max_score))
        challenge.evaluation_criteria = request.form.get('evaluation_criteria', challenge.evaluation_criteria).strip()
        challenge.status = request.form.get('status', challenge.status)
        
        # Update skills
        ChallengeRequiredSkill.query.filter_by(challenge_id=challenge.id).delete()
        selected_skills = request.form.getlist('skills')
        for s_id in selected_skills:
            if s_id.isdigit():
                db.session.add(ChallengeRequiredSkill(
                    challenge_id=challenge.id,
                    skill_id=int(s_id)
                ))
                
        db.session.commit()
        flash('Challenge specifications updated!', 'success')
        return redirect(url_for('recruiter.manage_challenges'))
        
    current_skill_ids = [crs.skill_id for crs in challenge.required_skills.all()]
    return render_template('recruiter/create_challenge.html',
                           all_skills=all_skills,
                           challenge=challenge,
                           current_skill_ids=current_skill_ids)


@recruiter_bp.route('/applicants')
@recruiter_required
def applicants():
    recruiter = g.profile
    jobs = recruiter.jobs.all()
    job_ids = [j.id for j in jobs]
    
    selected_job_id = request.args.get('job_id', type=int)
    status_filter = request.args.get('status', '')
    min_score = request.args.get('min_score', type=int)
    
    query = Application.query.filter(Application.job_id.in_(job_ids)) if job_ids else Application.query.filter_by(id=-1)
    
    if selected_job_id:
        query = query.filter_by(job_id=selected_job_id)
    if status_filter:
        query = query.filter_by(status=status_filter)
        
    apps = query.order_by(Application.applied_at.desc()).all()
    
    # Enrich applicants with challenge submission score and AI skill match
    enriched = []
    for app in apps:
        student = app.student
        job = app.job
        
        # Get associated challenge submission
        submission = None
        if job.associated_challenge_id:
            submission = Submission.query.filter_by(
                challenge_id=job.associated_challenge_id,
                student_id=student.id
            ).first()
            
        score = submission.score if submission else None
        
        if min_score is not None and (score is None or score < min_score):
            continue
            
        enriched.append({
            'app': app,
            'student': student,
            'job': job,
            'submission': submission,
            'score': score
        })
        
    return render_template('recruiter/applicants.html',
                           applicants=enriched,
                           jobs=jobs,
                           selected_job_id=selected_job_id,
                           status_filter=status_filter,
                           min_score=min_score)


@recruiter_bp.route('/submissions/<int:submission_id>/review', methods=['GET', 'POST'])
@recruiter_required
def review_submission(submission_id):
    recruiter = g.profile
    submission = Submission.query.get_or_404(submission_id)
    student = submission.student
    challenge = submission.challenge
    eval_result = submission.evaluation
    application = submission.application
    
    if request.method == 'POST':
        code_score = int(request.form.get('code_quality_score', 0))
        func_score = int(request.form.get('functionality_score', 0))
        ui_score = int(request.form.get('ui_ux_score', 0))
        recruiter_comments = request.form.get('recruiter_comments', '').strip()
        new_app_status = request.form.get('application_status')
        
        total = code_score + func_score + ui_score
        submission.score = total
        submission.status = 'evaluated'
        
        if not eval_result:
            eval_result = EvaluationResult(submission_id=submission.id)
            db.session.add(eval_result)
            
        eval_result.code_quality_score = code_score
        eval_result.functionality_score = func_score
        eval_result.ui_ux_score = ui_score
        eval_result.total_score = total
        eval_result.recruiter_comments = recruiter_comments
        eval_result.evaluated_at = datetime.utcnow()
        
        if application and new_app_status:
            application.status = new_app_status
            # Add Recruiter Review Record
            decision_map = {'Shortlisted': 'shortlist', 'Selected': 'hire', 'Rejected': 'reject'}
            review_rec = RecruiterReview(
                recruiter_id=recruiter.id,
                student_id=student.id,
                application_id=application.id,
                rating=5 if total >= 85 else (4 if total >= 70 else 3),
                review_notes=recruiter_comments,
                decision=decision_map.get(new_app_status, 'further_review')
            )
            db.session.add(review_rec)
            
            # Notify student
            db.session.add(Notification(
                user_id=student.user_id,
                title='Application Status Update',
                message=f'Your application for {application.job.title} is now: {new_app_status}.',
                link='/student/applications'
            ))
            
        db.session.commit()
        flash('Evaluation and review notes successfully recorded!', 'success')
        return redirect(url_for('recruiter.review_submission', submission_id=submission.id))
        
    return render_template('recruiter/submission_review.html',
                           submission=submission,
                           student=student,
                           challenge=challenge,
                           eval_result=eval_result,
                           application=application)


@recruiter_bp.route('/applications/<int:app_id>/status', methods=['POST'])
@recruiter_required
def update_application_status(app_id):
    recruiter = g.profile
    application = Application.query.get_or_404(app_id)
    
    # Verify authorization
    if application.job.recruiter_id != recruiter.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('recruiter.applicants'))
        
    new_status = request.form.get('status')
    valid_statuses = ['Applied', 'Assessment Pending', 'Under Review', 'Shortlisted', 'Rejected', 'Selected']
    
    if new_status in valid_statuses:
        application.status = new_status
        db.session.add(Notification(
            user_id=application.student.user_id,
            title='Application Status Update',
            message=f'Your application for "{application.job.title}" is now marked as {new_status}.',
            link='/student/applications'
        ))
        db.session.commit()
        flash(f'Application status updated to "{new_status}".', 'success')
        
    return redirect(request.referrer or url_for('recruiter.applicants'))


@recruiter_bp.route('/compare')
@recruiter_required
def compare_candidates():
    recruiter = g.profile
    job_id = request.args.get('job_id', type=int)
    candidate_ids_raw = request.args.get('candidate_ids', '')
    
    jobs = recruiter.jobs.all()
    target_job = None
    
    if job_id:
        target_job = Job.query.filter_by(id=job_id, recruiter_id=recruiter.id).first()
    elif jobs:
        target_job = jobs[0]
        
    if not target_job:
        flash('Please post or select a job to compare applicants.', 'info')
        return redirect(url_for('recruiter.dashboard'))
        
    # Get all applicants for this job
    applications = target_job.applications.all()
    available_students = [app.student for app in applications]
    
    # Selected student IDs
    selected_students = []
    if candidate_ids_raw:
        c_ids = [int(x) for x in candidate_ids_raw.split(',') if x.strip().isdigit()]
        selected_students = [s for s in available_students if s.id in c_ids]
    
    # If none explicitly selected, pick first 2-3
    if not selected_students and len(available_students) >= 2:
        selected_students = available_students[:3]
    elif not selected_students and len(available_students) == 1:
        selected_students = available_students
        
    comparison_data = None
    if selected_students:
        comparison_data = compare_candidates_for_job(target_job, selected_students)
        
    return render_template('recruiter/candidate_compare.html',
                           jobs=jobs,
                           target_job=target_job,
                           available_students=available_students,
                           selected_students=selected_students,
                           comparison_data=comparison_data)
