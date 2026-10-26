"""
ChallengeHire AI Candidate Comparator
Compares candidate submissions, technical match percentages, and practical evidence
for recruiters with multi-dimensional radar metrics.
"""

from .matcher import calculate_skill_match

def compare_candidates_for_job(job, student_profiles):
    """
    Produces side-by-side comparative analysis of selected candidates for a job.
    :param job: Job instance
    :param student_profiles: list of StudentProfile instances
    :return: dict with comparative table, radar dimensions, and AI takeaways
    """
    job_skills_list = [
        {'name': jrs.skill.name, 'is_mandatory': jrs.is_mandatory, 'weight': jrs.weight}
        for jrs in job.required_skills.all()
    ]
    
    candidates_data = []
    
    for student in student_profiles:
        # 1. Skill Match
        student_skills = {
            ss.skill.name: {'proficiency': ss.proficiency_level, 'verified': ss.verified}
            for ss in student.student_skills.all()
        }
        match_info = calculate_skill_match(student_skills, job_skills_list)
        
        # 2. Challenge Submissions
        submission = None
        eval_result = None
        if job.associated_challenge_id:
            sub = student.submissions.filter_by(challenge_id=job.associated_challenge_id).first()
            if sub:
                submission = sub
                eval_result = sub.evaluation
                
        # If no job-specific challenge, check highest scoring submission
        if not submission:
            submission = student.submissions.order_by(student.submissions.entity.score.desc()).first()
            if submission:
                eval_result = submission.evaluation
                
        # 3. Application Record
        application = student.applications.filter_by(job_id=job.id).first()
        
        # 4. Dimension metrics (0-100)
        skill_score = match_info['match_percentage']
        challenge_score = submission.score if submission else 0
        code_quality = (eval_result.code_quality_score * (100 / 30)) if eval_result else (60 if submission else 0)
        functionality = (eval_result.functionality_score * (100 / 40)) if eval_result else (60 if submission else 0)
        
        # Evidence Completeness Score
        evidence_score = 0
        if student.github_url or (submission and submission.github_repo_url):
            evidence_score += 40
        if submission and submission.live_demo_url:
            evidence_score += 35
        if submission and len(submission.explanation) > 50:
            evidence_score += 25
            
        candidate_item = {
            'student_id': student.id,
            'name': student.full_name,
            'college': student.college_name,
            'degree': student.degree or 'N/A',
            'graduation_year': student.graduation_year or 'N/A',
            'application_status': application.status if application else 'Not Applied',
            'cover_letter': application.cover_letter if application else '',
            'skill_match_percentage': match_info['match_percentage'],
            'fit_category': match_info['fit_category'],
            'matched_skills_names': [m['name'] for m in match_info['matched_skills']],
            'missing_skills_names': [m['name'] for m in match_info['missing_skills']],
            'challenge_title': submission.challenge.title if submission else 'None',
            'challenge_score': submission.score if submission else 'N/A',
            'submission_status': submission.status if submission else 'Not Submitted',
            'github_url': submission.github_repo_url if submission else student.github_url,
            'demo_url': submission.live_demo_url if submission else student.portfolio_url,
            'metrics': {
                'Skill Match': skill_score,
                'Challenge Score': challenge_score,
                'Code Quality': round(code_quality),
                'Functionality': round(functionality),
                'Project Evidence': evidence_score
            }
        }
        candidates_data.append(candidate_item)
        
    # Generate comparative takeaways
    takeaways = []
    if len(candidates_data) >= 2:
        sorted_by_challenge = sorted(candidates_data, key=lambda x: (x['challenge_score'] if isinstance(x['challenge_score'], int) else 0), reverse=True)
        sorted_by_skills = sorted(candidates_data, key=lambda x: x['skill_match_percentage'], reverse=True)
        
        takeaways.append(f"**Top Challenge Performer**: {sorted_by_challenge[0]['name']} scored {sorted_by_challenge[0]['challenge_score']}/100 on practical project delivery.")
        takeaways.append(f"**Highest Skill Match**: {sorted_by_skills[0]['name']} matches {sorted_by_skills[0]['skill_match_percentage']}% of required competencies.")
        
    return {
        'job_title': job.title,
        'candidates': candidates_data,
        'takeaways': takeaways,
        'metric_labels': ['Skill Match', 'Challenge Score', 'Code Quality', 'Functionality', 'Project Evidence']
    }
