from flask import Blueprint, request, jsonify
from models import add_user, verify_user, get_all_users, delete_user, get_user_id_by_username
import jwt
import datetime
from functools import wraps
import pymysql
from flask_cors import CORS, cross_origin

SECRET_KEY = "https://jwt.io/#debugger-io?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"  # Use a strong, random secret in production

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'code_doctore',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

auth = Blueprint('auth', __name__)

# Configure CORS for the blueprint
CORS(auth, resources={
    r"/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

def generate_token(username, is_admin=False):
    payload = {
        'username': username,
        'is_admin': is_admin,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        if not token:
            return jsonify({'error': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.user = data['username']
            request.is_admin = data.get('is_admin', False)
            # Fetch user_id from DB and set it
            request.user_id = get_user_id_by_username(request.user)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token!'}), 401
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not getattr(request, 'is_admin', False):
            return jsonify({'error': 'Admin privileges required!'}), 403
        return f(*args, **kwargs)
    return decorated

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400
    if add_user(username, password, email=email):
        return jsonify({'message': 'User registered successfully'}), 201
    else:
        return jsonify({'error': 'User already exists'}), 409

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    identifier = data.get('username') or data.get('email')
    password = data.get('password')
    valid, is_admin = verify_user(identifier, password)
    if valid:
        token = generate_token(identifier, is_admin)
        # Get user email from database
        try:
            connection = pymysql.connect(**db_config)
            with connection.cursor() as cursor:
                # First try to get user by username
                cursor.execute(
                    "SELECT email FROM users WHERE username = %s",
                    (identifier,)
                )
                result = cursor.fetchone()
                
                # If not found by username, try by email
                if not result:
                    cursor.execute(
                        "SELECT email FROM users WHERE email = %s",
                        (identifier,)
                    )
                    result = cursor.fetchone()
                
                user_email = result['email'] if result else None
                print(f"Debug - User: {identifier}, Email found: {user_email}")  # Debug log
        except Exception as e:
            print(f"Error fetching user email: {str(e)}")
            user_email = None
        finally:
            if 'connection' in locals():
                connection.close()

        # Debug log
        print(f"Login successful for user: {identifier}, is_admin: {is_admin}, email: {user_email}")
        return jsonify({
            'message': 'Login successful',
            'data': {
                'token': token,
                'username': identifier,
                'email': user_email,
                'is_admin': bool(is_admin)
            }
        })
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

# Admin endpoints
@auth.route('/admin/users', methods=['GET'])
@token_required
@admin_required
def list_users():
    users = get_all_users()
    return jsonify([
        {'id': u[0], 'username': u[1], 'email': u[2], 'is_admin': bool(u[3])}
        for u in users
    ])

@auth.route('/admin/users/<int:user_id>', methods=['DELETE'])
@token_required
@admin_required
def remove_user(user_id):
    if delete_user(user_id):
        return jsonify({'message': 'User deleted'})
    else:
        return jsonify({'error': 'User not found'}), 404

@auth.route('/logout', methods=['POST'])
@token_required
def logout():
    # For JWT, logout is handled client-side by deleting the token.
    # Optionally, you can implement token blacklisting here.
    return jsonify({'message': 'Successfully logged out.'}), 200

@auth.route('/user/update', methods=['PUT'])
@token_required
def update_user_info():
    data = request.get_json()
    user_id = request.user_id  # This is set by token_required decorator
    
    # Validate required fields
    if not data.get('username') or not data.get('email'):
        return jsonify({'error': 'Username and email are required'}), 400
        
    try:
        # Update user information
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET username = %s, email = %s WHERE id = %s",
                (data['username'], data['email'], user_id)
            )
            connection.commit()
            
            # Get updated user info
            cursor.execute(
                "SELECT id, username, email, is_admin FROM users WHERE id = %s",
                (user_id,)
            )
            user = cursor.fetchone()
            
            if user:
                return jsonify({
                    'message': 'User information updated successfully',
                    'user': {
                        'id': user[0],
                        'username': user[1],
                        'email': user[2],
                        'is_admin': bool(user[3])
                    }
                })
            else:
                return jsonify({'error': 'User not found'}), 404
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'connection' in locals():
            connection.close()

@auth.route('/user/info', methods=['GET'])
@token_required
def get_user_info():
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT username, email, is_admin FROM users WHERE username = %s",
                (request.user,)
            )
            user = cursor.fetchone()
            
            if user:
                return jsonify({
                    'username': user['username'],
                    'email': user['email'],
                    'is_admin': bool(user['is_admin'])
                })
            else:
                return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'connection' in locals():
            connection.close()