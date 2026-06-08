from flask import Blueprint, request, jsonify, current_app
from functools import wraps
import jwt
from datetime import datetime, timedelta
from models.user import UserModel
from middleware.auth import generate_token, login_required
from middleware.error import APIError
from utils.validators import validate_username, validate_password, validate_email
from config.settings import Config
import traceback
from flask_cors import cross_origin

auth = Blueprint('auth', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            token = token.split(' ')[1]  # Remove 'Bearer ' prefix
            data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
            request.user = data['username']
            request.user_id = data['user_id']
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        return f(*args, **kwargs)
    return decorated

@auth.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    try:
        data = request.get_json()
        if not data:
            raise APIError("No data provided", 400)

        current_app.logger.info(f"Registration attempt with data: {data}")

        # Validate input
        try:
            username = validate_username(data.get('username'))
            password = validate_password(data.get('password'))
            email = validate_email(data.get('email'))
        except APIError as e:
            current_app.logger.error(f"Validation error: {str(e)}")
            raise

        # Create user
        try:
            user_model = UserModel()
            user_id = user_model.create_user(username, password, email)
        except APIError as e:
            current_app.logger.error(f"User creation error: {str(e)}")
            raise
        except Exception as e:
            current_app.logger.error(f"Database error: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            raise APIError(f"Database error: {str(e)}", 500)

        # Generate token
        try:
            token = generate_token(user_id)
        except Exception as e:
            current_app.logger.error(f"Token generation error: {str(e)}")
            raise APIError(f"Token generation failed: {str(e)}", 500)

        current_app.logger.info(f"User registered successfully: {username}")

        return jsonify({
            'status': 'success',
            'message': 'User registered successfully',
            'data': {
                'token': token,
                'user_id': user_id,
                'username': username
            }
        })

    except APIError as e:
        current_app.logger.error(f"API Error in register: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), e.status_code
    except Exception as e:
        current_app.logger.error(f"Unexpected error in register: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': f'An unexpected error occurred: {str(e)}'
        }), 500

@auth.route('/login', methods=['POST'])
def login():
    """Authenticate a user and return a token."""
    try:
        data = request.get_json()
        if not data:
            raise APIError("No data provided", 400)

        current_app.logger.info(f"Login attempt with data: {data}")

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            raise APIError("Username and password are required", 400)

        # Authenticate user
        try:
            user_model = UserModel()
            user = user_model.authenticate_user(username, password)
        except APIError as e:
            current_app.logger.error(f"Authentication error: {str(e)}")
            raise
        except Exception as e:
            current_app.logger.error(f"Database error: {str(e)}")
            raise APIError(f"Database error: {str(e)}", 500)

        # Generate token
        try:
            token = generate_token(user['id'])
        except Exception as e:
            current_app.logger.error(f"Token generation error: {str(e)}")
            raise APIError(f"Token generation failed: {str(e)}", 500)

        current_app.logger.info(f"Login successful for user: {username}")

        return jsonify({
            'status': 'success',
            'message': 'Login successful',
            'data': {
                'token': token,
                'user_id': user['id'],
                'username': user['username'],
                'is_admin': user.get('is_admin', False)  # <-- Add this line
            }
        })

    except APIError as e:
        current_app.logger.error(f"API Error in login: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), e.status_code
    except Exception as e:
        current_app.logger.error(f"Unexpected error in login: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': f'An unexpected error occurred: {str(e)}'
        }), 500

@auth.route('/admin/users', methods=['GET', 'OPTIONS'])
@cross_origin(origins=["http://localhost:3000"])
@login_required  # or your admin_required decorator
def get_all_users():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        user_model = UserModel()
        users = user_model.get_all_users()  # You need to implement this method if not present
        return jsonify({
            'status': 'success',
            'data': users
        })
    except Exception as e:
        current_app.logger.error(f"Failed to fetch users: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"Failed to fetch users: {str(e)}"
        }), 500