from datetime import datetime, timedelta, timezone
import re
import bcrypt
import jwt
from config import Config
from models import db
from models.user import User

EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(raw_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(raw_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def generate_token(user: User) -> str:
    now = datetime.now(timezone.utc)
    expiry = now + timedelta(hours=Config.JWT_EXPIRATION_HOURS)
    payload = {
        'sub': user.email,
        'user_id': user.id,
        'iat': int(now.timestamp()),
        'exp': int(expiry.timestamp())
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm='HS256')

def register_user(name: str, email: str, password: str):
    clean_name = (name or '').strip()
    clean_email = (email or '').strip().lower()
    clean_password = (password or '').strip()

    if not clean_email or not EMAIL_REGEX.match(clean_email):
        raise ValueError('Invalid email format')
    if not clean_password or len(clean_password) < 6:
        raise ValueError('Password must be at least 6 characters')

    if User.query.filter_by(email=clean_email).first():
        raise ValueError('Email is already registered')

    if not clean_name:
        clean_name = clean_email.split('@')[0]

    hashed = hash_password(clean_password)
    user = User(name=clean_name, email=clean_email, password=hashed)
    db.session.add(user)
    db.session.commit()

    token = generate_token(user)
    return {
        'token': token,
        'name': user.name,
        'email': user.email
    }

def login_user(email: str, password: str):
    clean_email = (email or '').strip().lower()
    clean_password = (password or '').strip()

    if not clean_email or not clean_password:
        raise ValueError('Email and password are required')

    user = User.query.filter_by(email=clean_email).first()
    if not user or not verify_password(clean_password, user.password):
        raise ValueError('Invalid email or password')

    token = generate_token(user)
    return {
        'token': token,
        'name': user.name,
        'email': user.email
    }
