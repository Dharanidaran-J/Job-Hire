"""
ChallengeHire AI Recommender Engine
Recommends challenges and career paths based on candidate profile,
skill gaps, and historical challenge achievements.
"""

from .matcher import normalize_skill, calculate_skill_match

def recommend_challenges_for_student(student_profile, all_challenges, limit=4):
    """
    Ranks available challenges for a student with explainable AI rationales.
    Considers skills student already possesses, skills needing verification,
    and past completed submissions.
    """
    student_skills = {
        ss.skill.name.lower(): {
            'proficiency': ss.proficiency_level,
            'verified': ss.verified,
            'score': ss.score_earned
        }
        for ss in student_profile.student_skills.all()
    }
    
    # IDs of challenges already submitted by student
    completed_submissions = student_profile.submissions.all()
    completed_challenge_ids = {sub.challenge_id: sub for sub in completed_submissions}
    
    ranked = []
    
    for ch in all_challenges:
        if ch.status != 'active':
            continue
            
        is_completed = ch.id in completed_challenge_ids
        ch_skills = [crs.skill.name.lower() for crs in ch.required_skills.all()]
        
        if not ch_skills:
            continue
            
        # Count overlaps
        overlapping_skills = [s for s in ch_skills if s in student_skills]
        new_learning_skills = [s for s in ch_skills if s not in student_skills]
        
        overlap_ratio = len(overlapping_skills) / len(ch_skills) if ch_skills else 0
        
        # Scoring heuristic:
        # Ideal challenge has 50% - 80% overlap (challenges candidate to learn 1-2 new skills while applying existing ones)
        if 0.5 <= overlap_ratio <= 0.85:
            relevance = 90 + (overlap_ratio * 10)
            rationale_type = "Sweet Spot (Apply & Learn)"
        elif overlap_ratio > 0.85:
            relevance = 80 + (overlap_ratio * 15)
            rationale_type = "Direct Skill Mastery"
        elif 0.2 <= overlap_ratio < 0.5:
            relevance = 65 + (overlap_ratio * 20)
            rationale_type = "Skill Expansion"
        else:
            relevance = 45
            rationale_type = "New Domain Exploration"
            
        # If already completed with high score, lower recommendation priority
        if is_completed:
            prev_sub = completed_challenge_ids[ch.id]
            if prev_sub.score >= 80:
                relevance -= 40
                rationale_type = "Already Completed (Strong Score)"
            else:
                relevance += 5
                rationale_type = "Recommended Retake for Higher Score"
                
        # Formulate human-readable rationale
        matched_str = ", ".join([s.title() for s in overlapping_skills[:3]])
        missing_str = ", ".join([s.title() for s in new_learning_skills[:2]])
        
        if rationale_type == "Direct Skill Mastery":
            rationale = f"Directly tests your validated skills in {matched_str}. Completing this showcases production readiness to recruiters."
        elif rationale_type == "Sweet Spot (Apply & Learn)":
            rationale = f"Leverages your existing expertise in {matched_str} while challenging you to pick up {missing_str}."
        elif rationale_type == "Skill Expansion":
            rationale = f"Broadens your portfolio beyond current comfort zone into {missing_str} with practical guidance."
        elif rationale_type == "Recommended Retake for Higher Score":
            rationale = f"You previously scored {prev_sub.score}/100. Improving this project can boost your ranking for linked jobs."
        else:
            rationale = f"Explores new technologies ({missing_str or 'advanced patterns'}) to diversify your verified skill graph."

        ranked.append({
            'challenge': ch,
            'relevance_score': min(100, max(20, round(relevance))),
            'rationale': rationale,
            'is_completed': is_completed,
            'matching_skills': [s.title() for s in overlapping_skills],
            'learning_skills': [s.title() for s in new_learning_skills]
        })
        
    ranked.sort(key=lambda x: x['relevance_score'], reverse=True)
    return ranked[:limit]


def recommend_jobs_for_student(student_profile, all_jobs, limit=6):
    """
    Ranks open jobs according to candidate's skill match percentage.
    """
    student_skills_dict = {
        ss.skill.name: {
            'proficiency': ss.proficiency_level,
            'verified': ss.verified
        }
        for ss in student_profile.student_skills.all()
    }
    
    # Check jobs already applied to
    applied_job_ids = {app.job_id: app.status for app in student_profile.applications.all()}
    
    ranked_jobs = []
    
    for job in all_jobs:
        if job.status != 'active':
            continue
            
        req_skills = [
            {
                'name': jrs.skill.name,
                'is_mandatory': jrs.is_mandatory,
                'weight': jrs.weight
            }
            for jrs in job.required_skills.all()
        ]
        
        match_data = calculate_skill_match(student_skills_dict, req_skills)
        is_applied = job.id in applied_job_ids
        
        ranked_jobs.append({
            'job': job,
            'match_data': match_data,
            'is_applied': is_applied,
            'application_status': applied_job_ids.get(job.id, None)
        })
        
    ranked_jobs.sort(key=lambda x: x['match_data']['match_percentage'], reverse=True)
    return ranked_jobs[:limit]


def get_skill_gap_action_plan(student_profile, target_job, all_challenges):
    """
    Identifies exact skill gaps for a target job and pairs each missing skill
    with relevant practical challenges so student can bridge the gap immediately.
    """
    student_skills_dict = {
        ss.skill.name: {
            'proficiency': ss.proficiency_level,
            'verified': ss.verified
        }
        for ss in student_profile.student_skills.all()
    }
    
    req_skills = [
        {
            'name': jrs.skill.name,
            'is_mandatory': jrs.is_mandatory,
            'weight': jrs.weight
        }
        for jrs in target_job.required_skills.all()
    ]
    
    match_data = calculate_skill_match(student_skills_dict, req_skills)
    missing_skills = match_data['missing_skills']
    
    # Map missing skills to available challenges
    gap_recommendations = []
    
    for missing in missing_skills:
        skill_name = missing['name'].lower()
        matching_challenges = []
        
        for ch in all_challenges:
            ch_skills = [crs.skill.name.lower() for crs in ch.required_skills.all()]
            if skill_name in ch_skills:
                matching_challenges.append(ch)
                
        gap_recommendations.append({
            'skill_name': missing['name'],
            'is_mandatory': missing['is_mandatory'],
            'priority': missing['priority'],
            'recommended_challenges': matching_challenges[:2]
        })
        
    return {
        'job': target_job,
        'match_percentage': match_data['match_percentage'],
        'fit_category': match_data['fit_category'],
        'matched_skills': match_data['matched_skills'],
        'gap_recommendations': gap_recommendations
    }
