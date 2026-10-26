"""
ChallengeHire - Main Application Factory & Entry Point
AI-Based Job Recruitment Management System with Real-World Challenge Assessment
"""

import os
from flask import Flask, render_template
from config import Config
from models import db
from database.init_db import seed_database

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configure database URI (MySQL or SQLite fallback)
    db_uri = config_class.get_database_uri()
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    
    # Initialize extensions
    db.init_app(app)
    
    # Register Blueprints
    from routes.auth_routes import auth_bp
    from routes.main_routes import main_bp
    from routes.student_routes import student_bp
    from routes.recruiter_routes import recruiter_bp
    from routes.api_routes import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(recruiter_bp)
    app.register_blueprint(api_bp)
    
    # Template Filters & Helpers
    @app.template_filter('currency')
    def currency_filter(val):
        if val is None:
            return "N/A"
        try:
            return f"${float(val):,.0f}"
        except Exception:
            return str(val)

    @app.template_filter('status_badge')
    def status_badge_filter(status):
        badges = {
            'Applied': 'badge-info',
            'Assessment Pending': 'badge-warning',
            'Under Review': 'badge-primary',
            'Shortlisted': 'badge-success',
            'Selected': 'badge-emerald',
            'Rejected': 'badge-danger',
            'active': 'badge-success',
            'closed': 'badge-secondary',
            'draft': 'badge-warning',
            'evaluated': 'badge-success',
            'evaluating': 'badge-warning',
            'submitted': 'badge-info'
        }
        return badges.get(status, 'badge-secondary')
        
    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    # Auto-initialize database on application launch
    with app.app_context():
        try:
            seed_database(app)
        except Exception as ex:
            print(f"Notice on auto-seeding: {ex}")

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
