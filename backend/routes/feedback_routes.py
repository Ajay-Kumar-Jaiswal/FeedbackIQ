from flask import Blueprint, request, g
from middleware.auth_middleware import jwt_required
from services.feedback_service import (
    create_feedback,
    get_feedbacks,
    get_feedback_by_id,
    delete_feedback
)
from utils.responses import success_response, error_response

feedback_bp = Blueprint('feedback', __name__, url_prefix='/api/feedback')

@feedback_bp.route('', methods=['POST'])
@jwt_required
def create():
    data = request.get_json(silent=True) or {}
    text = data.get('text')

    try:
        result = create_feedback(g.current_user, text)
        return success_response(result, 201)
    except ValueError as ve:
        return error_response(str(ve), 400)
    except Exception as ex:
        return error_response("An error occurred while creating feedback", 500)

@feedback_bp.route('', methods=['GET'])
@jwt_required
def get_all():
    category = request.args.get('category')
    sentiment = request.args.get('sentiment')
    priority = request.args.get('priority')
    search = request.args.get('search')

    try:
        results = get_feedbacks(
            user=g.current_user,
            category=category,
            sentiment=sentiment,
            priority=priority,
            search=search
        )
        return success_response(results, 200)
    except Exception as ex:
        return error_response("An error occurred while retrieving feedback", 500)

@feedback_bp.route('/<int:feedback_id>', methods=['GET'])
@jwt_required
def get_one(feedback_id):
    try:
        result = get_feedback_by_id(g.current_user, feedback_id)
        if not result:
            return error_response("Feedback not found", 404)
        return success_response(result, 200)
    except Exception as ex:
        return error_response("An error occurred while retrieving feedback", 500)

@feedback_bp.route('/<int:feedback_id>', methods=['DELETE'])
@jwt_required
def delete_one(feedback_id):
    try:
        deleted = delete_feedback(g.current_user, feedback_id)
        if not deleted:
            return error_response("Feedback not found", 404)
        return ('', 204)
    except Exception as ex:
        return error_response("An error occurred while deleting feedback", 500)
