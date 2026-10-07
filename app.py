from datetime import datetime
from flask import Flask, render_template, session
from config import Config
from models import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.student import student_bp
    from routes.lessons import lessons_bp
    from routes.quizzes import quizzes_bp
    from routes.progress import progress_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(lessons_bp)
    app.register_blueprint(quizzes_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(admin_bp)

    # Context processors
    @app.context_processor
    def inject_global_vars():
        return {
            'now': datetime.now(),
            'current_user_name': session.get('full_name'),
            'current_user_role': session.get('role'),
            'is_logged_in': 'user_id' in session
        }

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(403)
    def forbidden_access(e):
        return render_template('403.html'), 403

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
