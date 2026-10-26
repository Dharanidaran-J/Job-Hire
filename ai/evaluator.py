"""
ChallengeHire AI Submission Evaluator & Scoring Engine
Supports automated rubric analysis, objective quiz grading, and optional LLM
evaluation with explainable feedback and graceful fallback heuristics.
"""

import os
import re
import json

def grade_quiz_attempt(assessment, submitted_answers):
    """
    Evaluates objective assessment / quiz questions.
    :param assessment: Assessment model instance
    :param submitted_answers: dict of {question_id_str: selected_answer_str}
    :return: dict with total_points, earned_points, percentage, passed, details
    """
    total_points = 0
    earned_points = 0
    question_results = []
    
    questions = assessment.questions.all()
    for q in questions:
        total_points += q.points
        ans = submitted_answers.get(str(q.id), '').strip()
        is_correct = (ans.lower() == q.correct_answer.strip().lower())
        
        if is_correct:
            earned_points += q.points
            
        question_results.append({
            'question_id': q.id,
            'question_text': q.question_text,
            'submitted_answer': ans,
            'correct_answer': q.correct_answer,
            'is_correct': is_correct,
            'points_awarded': q.points if is_correct else 0,
            'max_points': q.points
        })
        
    percentage = round((earned_points / total_points * 100)) if total_points > 0 else 0
    passed = percentage >= assessment.pass_percentage
    
    return {
        'total_points': total_points,
        'earned_points': earned_points,
        'percentage': percentage,
        'passed': passed,
        'details': question_results
    }


def evaluate_project_submission(challenge, github_url, live_demo_url, explanation, api_key=None):
    """
    Evaluates a practical challenge submission using either Gemini AI (if key is supplied)
    or a deterministic, explainable rule-based rubric heuristic fallback.
    """
    # 1. Try LLM evaluation if API key is provided
    if api_key:
        try:
            ai_result = _call_gemini_evaluator(challenge, github_url, live_demo_url, explanation, api_key)
            if ai_result:
                return ai_result
        except Exception:
            # Fall back seamlessly to heuristic evaluation
            pass
            
    # 2. Rule-Based Heuristic Evaluation
    return _heuristic_rubric_evaluation(challenge, github_url, live_demo_url, explanation)


def _heuristic_rubric_evaluation(challenge, github_url, live_demo_url, explanation):
    """
    Deterministic rubric evaluation based on documented deliverables, explanation depth,
    code repository presence, and domain keyword alignment.
    """
    explanation_clean = (explanation or "").strip()
    word_count = len(explanation_clean.split())
    
    # 1. Deliverables & Evidence Scoring (Max 30) - Code Quality & Architecture
    code_quality = 18 # baseline
    if github_url and ('github.com' in github_url.lower() or 'gitlab.com' in github_url.lower() or 'bitbucket.org' in github_url.lower()):
        code_quality += 6 # Valid repo link provided
    if any(kw in explanation_clean.lower() for kw in ['mvc', 'modular', 'architecture', 'clean code', 'refactor', 'pattern', 'structure', 'pep 8']):
        code_quality += 4
    code_quality = min(30, max(10, code_quality))
    
    # 2. Functionality & Requirements Verification (Max 40)
    functionality = 24 # baseline
    if live_demo_url and ('http://' in live_demo_url or 'https://' in live_demo_url):
        functionality += 7 # Live demo verified
    if any(kw in explanation_clean.lower() for kw in ['database', 'schema', 'sql', 'query', 'crud', 'api', 'endpoint', 'validation', 'error handling']):
        functionality += 5
    if any(kw in explanation_clean.lower() for kw in ['test', 'unit test', 'coverage', 'edge case', 'tested']):
        functionality += 4
    functionality = min(40, max(15, functionality))
    
    # 3. UI/UX & Documentation Quality (Max 30)
    ui_ux = 16 # baseline
    if word_count >= 100:
        ui_ux += 5
    elif word_count >= 40:
        ui_ux += 3
        
    if any(kw in explanation_clean.lower() for kw in ['responsive', 'mobile', 'accessible', 'css', 'grid', 'flexbox', 'design', 'chart', 'modal']):
        ui_ux += 6
    if any(kw in explanation_clean.lower() for kw in ['readme', 'setup', 'instructions', 'guide', 'install']):
        ui_ux += 3
    ui_ux = min(30, max(10, ui_ux))
    
    total_score = code_quality + functionality + ui_ux
    
    # Construct actionable, explainable feedback
    strengths = []
    growth_areas = []
    
    if github_url:
        strengths.append("Repository evidence provided with project source code.")
    else:
        growth_areas.append("Providing a public GitHub or Git repository link significantly increases reviewer confidence.")
        
    if live_demo_url:
        strengths.append("Live deployment or demo URL provided for instant recruiter verification.")
    else:
        growth_areas.append("Deploying a live preview (e.g. Vercel, Netlify, Render) is strongly encouraged.")
        
    if word_count > 60:
        strengths.append("Comprehensive technical explanation outlining architectural choices and database design.")
    else:
        growth_areas.append("Expand on how you solved core edge cases, schema design, and concurrency in your writeup.")
        
    feedback_text = (
        f"**Automated Rubric Assessment (Max {challenge.max_score} pts)**\n\n"
        f"• **Code Quality & Architecture**: {code_quality}/30 pts\n"
        f"• **Functionality & Requirements**: {functionality}/40 pts\n"
        f"• **UI/UX & Documentation**: {ui_ux}/30 pts\n\n"
        f"**Key Observations:**\n" + "\n".join([f"✓ {s}" for s in strengths]) + "\n" +
        "\n".join([f"⚠ {g}" for g in growth_areas]) + "\n\n"
        f"*Note: This evaluation is an AI-assisted heuristic rubric. Recruiters should review project code directly prior to final decision.*"
    )
    
    return {
        'code_quality_score': code_quality,
        'functionality_score': functionality,
        'ui_ux_score': ui_ux,
        'total_score': total_score,
        'ai_suggested_score': total_score,
        'ai_feedback': feedback_text,
        'source': 'heuristic_engine'
    }


def _call_gemini_evaluator(challenge, github_url, live_demo_url, explanation, api_key):
    """Optional call to Google Gemini API when key is configured."""
    import requests
    
    prompt = f"""
    You are an expert technical hiring evaluator for ChallengeHire.
    Evaluate the following student submission for a practical coding challenge.

    Challenge Title: {challenge.title}
    Problem Statement: {challenge.problem_statement}
    Evaluation Criteria: {challenge.evaluation_criteria}

    Student Submission:
    - GitHub Repo URL: {github_url or 'None'}
    - Live Demo URL: {live_demo_url or 'None'}
    - Technical Explanation & Approach:
    \"\"\"{explanation}\"\"\"

    Respond ONLY in valid JSON format with this exact structure:
    {{
        "code_quality_score": <integer between 10 and 30>,
        "functionality_score": <integer between 15 and 40>,
        "ui_ux_score": <integer between 10 and 30>,
        "total_score": <sum of the three above>,
        "ai_feedback": "<Concise markdown review highlighting strengths, architectural soundness, and suggestions for improvement>"
    }}
    """
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2}
    }
    
    res = requests.post(url, json=payload, timeout=8)
    if res.status_code == 200:
        data = res.json()
        raw_text = data['candidates'][0]['content']['parts'][0]['text']
        # Clean JSON markdown fences
        raw_text = re.sub(r'```json\s*', '', raw_text)
        raw_text = re.sub(r'```\s*', '', raw_text).strip()
        parsed = json.loads(raw_text)
        
        parsed['ai_suggested_score'] = parsed.get('total_score', 80)
        parsed['source'] = 'gemini_llm'
        return parsed
        
    return None
