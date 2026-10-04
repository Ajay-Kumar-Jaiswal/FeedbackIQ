import logging
from flask import Blueprint, request, g
from middleware.auth_middleware import jwt_required
from services.auth_service import register_user, login_user
from utils.responses import success_response, error_response

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    try:
        result = register_user(name, email, password)
        return success_response(result, 201)
    except ValueError as ve:
        logger.warning("Registration validation failed for email '%s': %s", email, str(ve))
        return error_response(str(ve), 400)
    except Exception as ex:
        logger.error("Registration database/system error occurred for email '%s': %s", email, str(ex), exc_info=True)
        return error_response("An error occurred during registration", 500)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get('email')
    password = data.get('password')

    try:
        result = login_user(email, password)
        return success_response(result, 200)
    except ValueError as ve:
        logger.warning("Login failed for email '%s': %s", email, str(ve))
        return error_response(str(ve), 401)
    except Exception as ex:
        logger.error("Login database/system error occurred for email '%s': %s", email, str(ex), exc_info=True)
        return error_response("An error occurred during login", 500)

@auth_bp.route('/me', methods=['GET'])
@jwt_required
def get_me():
    user = g.current_user
    return success_response({
        'id': user.id,
        'name': user.name,
        'email': user.email
    }, 200)
