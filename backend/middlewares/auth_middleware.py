from flask import request, jsonify, g
from functools import wraps
from utils.jwt_helper import decode_jwt

def token_required(f):
    """
    Decorator that checks if a valid JWT token is present in the request.
    Attaches the decoded payload to flask.g.user if valid.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Unauthorized', 'message': 'Valid token is required'}), 401

        token = auth_header.split(' ')[1]
        payload = decode_jwt(token)
        if not payload:
            return jsonify({'error': 'Unauthorized', 'message': 'Invalid or expired token'}), 401

        # Store user info in Flask's g object for the current request
        g.user = payload
        return f(*args, **kwargs)
    return decorated

def role_required(allowed_roles):
    """
    Decorator that checks if the authenticated user has one of the allowed roles.
    Must be used after the token_required decorator.
    
    Args:
        allowed_roles: List of role names that are allowed to access the route
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Ensure this decorator is used after token_required
            if not hasattr(g, 'user'):
                return jsonify({'error': 'Server error', 'message': 'token_required decorator must be used before role_required'}), 500

            if g.user.get('role') not in allowed_roles:
                return jsonify({'error': 'Forbidden', 'message': 'Insufficient permissions'}), 403
                
            return f(*args, **kwargs)
        return decorated
    return decorator

# Keep the original auth_middleware for backward compatibility
def auth_middleware(roles=None):
    """
    Legacy combined decorator that checks both token validity and role.
    New code should use token_required and role_required separately for better composability.
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Unauthorized'}), 401

            token = auth_header.split(' ')[1]
            payload = decode_jwt(token)
            if not payload:
                return jsonify({'error': 'Invalid token'}), 401

            if roles and payload.get('role') not in roles:
                return jsonify({'error': 'Insufficient permissions'}), 403

            request.user = payload  # Attach to request
            return f(*args, **kwargs)
        return wrapper
    return decorator