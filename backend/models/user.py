import hashlib
from config.database import DatabaseConfig
from middleware.error import APIError
import traceback
from mysql.connector.cursor import MySQLCursorDict

class UserModel:
    def __init__(self):
        self._create_tables()

    def _create_tables(self):
        """Create necessary database tables if they don't exist."""
        try:
            conn = DatabaseConfig.get_connection()
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    email VARCHAR(255),
                    is_admin BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            raise APIError(f"Failed to create database tables: {str(e)}", 500)

    def create_user(self, username, password, email=None):
        """Create a new user."""
        try:
            # Hash the password using MD5
            password_hash = hashlib.md5(password.encode()).hexdigest()

            conn = DatabaseConfig.get_connection()
            cursor = conn.cursor(dictionary=True)

            # Check if username already exists
            cursor.execute(
                "SELECT id FROM users WHERE username = %s",
                (username,)
            )
            if cursor.fetchone():
                raise APIError("Username already exists", 400)

            # Insert new user
            cursor.execute(
                """
                INSERT INTO users (username, password_hash, email, is_admin)
                VALUES (%s, %s, %s, %s)
                """,
                (username, password_hash, email, 0)
            )
            conn.commit()
            user_id = cursor.lastrowid
            
            cursor.close()
            conn.close()
            return user_id

        except APIError:
            raise
        except Exception as e:
            raise APIError(f"Failed to create user: {str(e)}", 500)

    def authenticate_user(self, username, password):
        """Authenticate a user and return user data if successful."""
        try:
            # Hash the password using MD5
            password_hash = hashlib.md5(password.encode()).hexdigest()

            conn = DatabaseConfig.get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                "SELECT id, username, password_hash, email, is_admin FROM users WHERE username = %s",
                (username,)
            )
            user_row = cursor.fetchone()

            cursor.close()
            conn.close()

            if not user_row:
                raise APIError("Invalid username or password", 401)

            # Verify password
            if user_row['password_hash'] != password_hash:
                raise APIError("Invalid username or password", 401)

            return {
                'id': user_row['id'],
                'username': user_row['username'],
                'email': user_row['email'],
                'is_admin': bool(user_row['is_admin'])  # Ensure boolean
            }

        except APIError:
            raise
        except Exception as e:
            raise APIError(f"Authentication failed: {str(e)}", 500)

    def get_user_by_id(self, user_id):
        """Get user by ID."""
        try:
            conn = DatabaseConfig.get_connection()
            cursor = conn.cursor(cursor_class=MySQLCursorDict)
            cursor.execute(
                "SELECT id, username, email, is_admin FROM users WHERE id = %s",
                (user_id,)
            )
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            if not user:
                raise APIError("User not found", 404)
            return user

        except APIError:
            raise
        except Exception as e:
            raise APIError(f"Failed to get user: {str(e)}", 500)

    def update_user(self, user_id, email=None):
        """Update user information."""
        try:
            conn = DatabaseConfig.get_connection()
            cursor = conn.cursor(cursor_class=MySQLCursorDict)
            if email:
                cursor.execute(
                    "UPDATE users SET email = %s WHERE id = %s",
                    (email, user_id)
                )
                conn.commit()
            cursor.close()
            conn.close()
            return self.get_user_by_id(user_id)

        except APIError:
            raise
        except Exception as e:
            raise APIError(f"Failed to update user: {str(e)}", 500)

    def delete_user(self, user_id):
        """Delete a user."""
        try:
            conn = DatabaseConfig.get_connection()
            cursor = conn.cursor(cursor_class=MySQLCursorDict)
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
            cursor.close()
            conn.close()
            return True

        except Exception as e:
            raise APIError(f"Failed to delete user: {str(e)}", 500)

    def get_all_users(self):
        """Return all users."""
        try:
            conn = DatabaseConfig.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, username, email, is_admin FROM users")
            users = cursor.fetchall()
            cursor.close()
            conn.close()
            return users
        except Exception as e:
            raise APIError(f"Failed to fetch users: {str(e)}", 500)