from flask import request, jsonify
from utils.jwt_helper import decode_jwt

def auth_middleware(f):
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Unauthorized'}), 401

        token = auth_header.split(' ')[1]
        payload = decode_jwt(token)
        if not payload:
            return jsonify({'error': 'Invalid token'}), 401

        # Attach payload to request if needed (e.g., request.user = payload)
        return f(*args, **kwargs)
    return wrapper