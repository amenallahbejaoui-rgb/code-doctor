import re
from middleware.error import APIError

def validate_github_url(url):
    """Validate GitHub repository URL format."""
    if not url:
        raise APIError("GitHub URL is required", 400)
    pattern = r'^https?://(?:www\.)?github\.com/[a-zA-Z0-9-]+/[a-zA-Z0-9-._]+/?$'
    if not re.match(pattern, url):
        raise APIError("Invalid GitHub repository URL format. Must be like: https://github.com/username/repo", 400)
    return url

def validate_username(username):
    """Validate username format."""
    if not username:
        raise APIError("Username is required", 400)
    if len(username) < 3:
        raise APIError("Username must be at least 3 characters long", 400)
    if len(username) > 50:
        raise APIError("Username must be less than 50 characters", 400)
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        raise APIError("Username can only contain letters, numbers, underscores, and hyphens", 400)
    return username

def validate_password(password):
    """Validate password strength."""
    if not password:
        raise APIError("Password is required", 400)
    if len(password) < 8:
        raise APIError("Password must be at least 8 characters long", 400)
    if not re.search(r'[A-Z]', password):
        raise APIError("Password must contain at least one uppercase letter", 400)
    if not re.search(r'[a-z]', password):
        raise APIError("Password must contain at least one lowercase letter", 400)
    if not re.search(r'[0-9]', password):
        raise APIError("Password must contain at least one number", 400)
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise APIError("Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)", 400)
    return password

def validate_email(email):
    """Validate email format."""
    if not email:
        return None
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise APIError("Invalid email format. Must be like: user@example.com", 400)
    return email

def validate_repo_id(repo_id):
    """Validate repository ID."""
    try:
        repo_id = int(repo_id)
        if repo_id <= 0:
            raise APIError("Invalid repository ID", 400)
        return repo_id
    except ValueError:
        raise APIError("Repository ID must be a positive integer", 400) 