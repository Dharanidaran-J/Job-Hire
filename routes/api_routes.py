"""
ChallengeHire REST API Routes
Provides JSON endpoints for real-time notifications, dynamic skill matching,
and interactive client-side operations.
"""

from flask import Blueprint, jsonify, request, g, session
from models import db, Notification, Job, Skill, StudentProfile
from routes.auth_routes import login_required
from ai.matcher import calculate_skill_match

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/notifications/unread-count')
def unread_notifications_count():
    if not g.user:
        return jsonify({'count': 0})
    count = Notification.query.filter_by(user_id=g.user.id, is_read=False).count()
    return jsonify({'count': count})


@api_bp.route('/notifications')
def get_notifications():
    if not g.user:
        return jsonify([])
    notifs = Notification.query.filter_by(user_id=g.user.id).order_by(Notification.created_at.desc()).limit(10).all()
    return jsonify([{
        'id': n.id,
        'title': n.title,
        'message': n.message,
        'link': n.link,
        'is_read': n.is_read,
        'created_at': n.created_at.strftime('%b %d, %H:%M')
    } for n in notifs])


@api_bp.route('/notifications/mark-read', methods=['POST'])
def mark_notifications_read():
    if not g.user:
        return jsonify({'success': False}), 401
    Notification.query.filter_by(user_id=g.user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify({'success': True})


@api_bp.route('/skill-match/simulate', methods=['POST'])
def simulate_skill_match():
    """
    Live AI Skill Match Simulator endpoint.
    Accepts student skills and job required skills, returns calculated fit breakdown.
    """
    data = request.get_json() or {}
    student_skills = data.get('student_skills', {}) # {'python': {'proficiency': 'advanced'}}
    job_skills = data.get('job_skills', []) # [{'name': 'Python', 'is_mandatory': True, 'weight': 3}]
    
    match_result = calculate_skill_match(student_skills, job_skills)
    return jsonify(match_result)
