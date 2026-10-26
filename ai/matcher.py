"""
ChallengeHire AI Skill Matcher & Gap Analyzer
Calculates explainable skill matching, weighted fit scores,
and identifies missing competencies between candidates and job descriptions.
"""

def normalize_skill(skill_name):
    """Normalize skill name for robust matching."""
    return skill_name.strip().lower()

def calculate_skill_match(student_skills_dict, job_required_skills_list):
    """
    Calculates detailed match statistics between candidate and job.
    
    :param student_skills_dict: dict of {skill_name: {'proficiency': 'beginner'|'intermediate'|'advanced', 'verified': bool}}
    :param job_required_skills_list: list of dicts with {'name': str, 'is_mandatory': bool, 'weight': int}
    
    :return: dict with match_percentage, matched_skills, missing_skills, gap_analysis, and summary
    """
    if not job_required_skills_list:
        return {
            'match_percentage': 100,
            'fit_category': 'Strong Match',
            'matched_skills': list(student_skills_dict.keys()),
            'missing_skills': [],
            'mandatory_missing': [],
            'optional_missing': [],
            'weighted_score': 100.0,
            'total_skills_required': 0
        }
        
    student_lookup = {normalize_skill(k): v for k, v in student_skills_dict.items()}
    
    proficiency_multiplier = {
        'advanced': 1.0,
        'intermediate': 0.85,
        'beginner': 0.60
    }
    
    total_weight = 0
    earned_weight = 0
    matched_skills = []
    missing_skills = []
    mandatory_missing = []
    optional_missing = []
    
    for req in job_required_skills_list:
        req_name = req['name']
        norm_req = normalize_skill(req_name)
        weight = req.get('weight', 1)
        is_mandatory = req.get('is_mandatory', True)
        
        # Mandatory skills carry higher baseline weight
        effective_weight = weight * (1.5 if is_mandatory else 1.0)
        total_weight += effective_weight
        
        if norm_req in student_lookup:
            student_meta = student_lookup[norm_req]
            prof = student_meta.get('proficiency', 'intermediate').lower()
            verified = student_meta.get('verified', False)
            
            prof_score = proficiency_multiplier.get(prof, 0.75)
            # slight boost if skill is verified through challenge
            verification_bonus = 1.05 if verified else 1.0
            
            awarded = min(effective_weight, effective_weight * prof_score * verification_bonus)
            earned_weight += awarded
            
            matched_skills.append({
                'name': req_name,
                'proficiency': prof.capitalize(),
                'verified': verified,
                'is_mandatory': is_mandatory,
                'match_contribution': round((awarded / effective_weight) * 100)
            })
        else:
            missing_info = {
                'name': req_name,
                'is_mandatory': is_mandatory,
                'priority': 'Critical' if is_mandatory else 'Recommended'
            }
            missing_skills.append(missing_info)
            if is_mandatory:
                mandatory_missing.append(missing_info)
            else:
                optional_missing.append(missing_info)

    raw_percentage = (earned_weight / total_weight * 100) if total_weight > 0 else 0
    match_percentage = round(raw_percentage)

    if match_percentage >= 80 and len(mandatory_missing) == 0:
        fit_category = 'Strong Match'
        fit_color = 'success'
    elif match_percentage >= 60:
        fit_category = 'Moderate Fit'
        fit_color = 'warning'
    elif match_percentage >= 40:
        fit_category = 'Partial Fit'
        fit_color = 'secondary'
    else:
        fit_category = 'High Skill Gap'
        fit_color = 'danger'

    return {
        'match_percentage': match_percentage,
        'fit_category': fit_category,
        'fit_color': fit_color,
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'mandatory_missing': mandatory_missing,
        'optional_missing': optional_missing,
        'total_skills_required': len(job_required_skills_list),
        'matched_count': len(matched_skills),
        'missing_count': len(missing_skills)
    }
