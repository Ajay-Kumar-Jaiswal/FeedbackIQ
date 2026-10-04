from functools import wraps
from flask import request, g
import jwt
from config import Config
from models.user import User
from utils.responses import error_response

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', None)
        if not auth_header or not auth_header.startswith('Bearer '):
            return error_response('Unauthorized: Authentication token is missing or invalid', 401)
        
        token = auth_header[7:].strip()
        try:
            payload = jwt.decode(token, Config.JWT_SECRET, algorithms=['HS256'])
            email = payload.get('sub')
            if not email:
                return error_response('Unauthorized: Invalid token payload', 401)
            
            user = User.query.filter_by(email=email).first()
            if not user:
                return error_response('Unauthorized: User not found', 401)
            
            g.current_user = user
        except jwt.ExpiredSignatureError:
            return error_response('Unauthorized: Token has expired', 401)
        except jwt.InvalidTokenError:
            return error_response('Unauthorized: Invalid authentication token', 401)
        except Exception:
            return error_response('Unauthorized: Authentication failed', 401)
        
        return f(*args, **kwargs)
    return decorated
