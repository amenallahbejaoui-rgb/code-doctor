from functools import wraps
from flask import request, jsonify
import jwt
from config.settings import Config
from middleware.error import APIError
from datetime import datetime

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Get token from header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        if not token:
            raise APIError('Authentication token is missing', 401)

        try:
            # Decode token
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            # Extract user_id from the payload
            request.user_id = payload.get('user_id')
            if not request.user_id:
                raise APIError('Invalid token payload', 401)
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            raise APIError('Token has expired', 401)
        except jwt.InvalidTokenError:
            raise APIError('Invalid token', 401)
        except Exception as e:
            raise APIError(f'Authentication failed: {str(e)}', 401)

    return decorated

def generate_token(user_id):
    """Generate JWT token for user."""
    try:
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + Config.JWT_ACCESS_TOKEN_EXPIRES
        }
        return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')
    except Exception as e:
        raise APIError(f'Token generation failed: {str(e)}', 500)

 