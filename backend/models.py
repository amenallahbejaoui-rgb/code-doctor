import bcrypt
import pymysql

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "npwd",
    "database": "ahey"
}

def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode(), stored_password.encode())

def add_user(username, password, email=None, is_admin=0):
    password_hash = hash_password(password)
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (username, email, password_hash, is_admin) VALUES (%s, %s, %s, %s)",
                (username, email, password_hash, is_admin)
            )
            connection.commit()
        return True
    except pymysql.err.IntegrityError:
        return False
    finally:
        if 'connection' in locals() and connection:
            connection.close()

def verify_user(identifier, password):
    # identifier can be username or email
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            # First check if it's the admin user
            if identifier == 'admin' and password == 'admin123':
                return True, True
            
            # For other users, check the database
            cursor.execute(
                "SELECT password_hash, is_admin FROM users WHERE username = %s OR email = %s",
                (identifier, identifier)
            )
            result = cursor.fetchone()
            if result and verify_password(result[0], password):
                # Debug log
                print(f"User verified: {identifier}, is_admin: {bool(result[1])}")
                return True, bool(result[1])  # Ensure boolean value
            return False, False
    finally:
        if 'connection' in locals() and connection:
            connection.close()

def get_all_users():
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, username, email, is_admin FROM users")
            return cursor.fetchall()
    finally:
        if 'connection' in locals() and connection:
            connection.close()

def delete_user(user_id):
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            connection.commit()
            return cursor.rowcount > 0
    finally:
        if 'connection' in locals() and connection:
            connection.close()

def get_user_id_by_username(username):
    db_config = {
        "host": "localhost",
        "user": "root",
        "password": "npwd",
        "database": "ahey"
    }
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
            return result[0] if result else None
    finally:
        connection.close()

def ensure_admin_exists():
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            # Check if admin exists
            cursor.execute("SELECT id FROM users WHERE username = 'admin'")
            if not cursor.fetchone():
                # Create admin user if it doesn't exist
                password_hash = hash_password('admin123')
                cursor.execute(
                    "INSERT INTO users (username, password_hash, email, is_admin) VALUES (%s, %s, %s, %s)",
                    ('admin', password_hash, 'admin@example.com', 1)
                )
                connection.commit()
                print("Admin user created successfully")
    except Exception as e:
        print(f"Error ensuring admin exists: {str(e)}")
    finally:
        if 'connection' in locals() and connection:
            connection.close()

# Call this when the module is imported
ensure_admin_exists()