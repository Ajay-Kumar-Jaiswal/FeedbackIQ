import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from models import db
from models.user import User
from models.feedback import Feedback
from routes.auth_routes import auth_bp
from routes.feedback_routes import feedback_bp

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("FeedbackIQ")

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize SQLAlchemy
    db.init_app(app)

    # Configure CORS for frontend access
    CORS(
        app,
        resources={r"/api/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]}},
        supports_credentials=True
    )

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(feedback_bp)

    # Global Error Handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"status": 404, "message": "Resource not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({"status": 405, "message": "Method not allowed"}), 405

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"status": 500, "message": "Internal server error"}), 500

    # Initialize database tables
    with app.app_context():
        try:
            db.create_all()
            logger.info("FeedbackIQ database tables verified/created successfully.")
        except Exception as ex:
            logger.warning("Could not auto-create database tables on startup (%s). Ensure MySQL is running with the configured credentials.", str(ex))

    return app

app = create_app()

if __name__ == "__main__":
    logger.info("Starting FeedbackIQ Flask backend on port %d...", Config.PORT)
    app.run(host="0.0.0.0", port=Config.PORT, debug=True)
