from flask import request, jsonify, g
from models.user_model import User
from utils.password_helper import hash_password, verify_password
from validators.auth_validator import validate_email, validate_password

def get_user_profile():
    """Get current user's profile information"""
    user = g.user  # From token_required
    user_data = User.find_by_id(user['id'])
    if not user_data:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': str(user_data['_id']),
        'username': user_data['username'],
        'email': user_data['email'],
        'role': user_data['role']
    }), 200

def get_all_users():
    """Get all users (Admin only)"""
    try:
        users = User.get_all_users()
        users_list = [{
            'id': str(user['id']),
            'username': user['username'],
            'email': user['email'],
            'role': user['role']
        } for user in users]
        
        return jsonify({
            'users': users_list,
            'total': len(users_list)
        }), 200
    except Exception as e:
        print(f"Error in get_all_users: {e}") # Added for debugging
        return jsonify({'error': f'Failed to fetch users: {str(e)}'}), 500

def update_profile():
    data = request.get_json()
    user = g.user  # From token_required
    user_data = User.find_by_id(user['id'])
    
    if not user_data:
        return jsonify({'error': 'User not found'}), 404

    update_data = {}

    if 'username' in data:
        existing_user = User.find_by_username(data['username'])
        if existing_user and str(existing_user['_id']) != str(user_data['_id']):
            return jsonify({'error': 'Username already exists'}), 400
        update_data['username'] = data['username']

    if 'email' in data:
        if not validate_email(data['email']):
            return jsonify({'error': 'Invalid email'}), 400
        existing_user = User.find_by_email(data['email'])
        if existing_user and str(existing_user['_id']) != str(user_data['_id']):
            return jsonify({'error': 'Email already exists'}), 400
        update_data['email'] = data['email']

    if 'new_password' in data:
        if not validate_password(data['new_password']):
            return jsonify({'error': 'Invalid password'}), 400
        if 'current_password' not in data or not verify_password(data['current_password'], user_data['password_hash']):
            return jsonify({'error': 'Current password incorrect'}), 401
        update_data['password_hash'] = hash_password(data['new_password'])

    if update_data:
        User.update_by_id(str(user_data['_id']), update_data)
    
    return jsonify({'message': 'Profile updated'}), 200


def create_user():
    """Create a new user (Admin only)"""
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'User')

    if not username or not email or not password:
        return jsonify({'error': 'Missing username, email, or password'}), 400

    if not validate_email(email):
        return jsonify({'error': 'Invalid email format'}), 400

    if not validate_password(password):
        return jsonify({'error': 'Password does not meet requirements'}), 400

    if User.find_by_username(username):
        return jsonify({'error': 'Username already exists'}), 409

    if User.find_by_email(email):
        return jsonify({'error': 'Email already exists'}), 409

    hashed_password = hash_password(password)
    new_user = User.create(username, email, hashed_password, role)

    return jsonify({'message': 'User created successfully', 'user': new_user.to_dict()}), 201

def delete_user(user_id):
    """Delete a user (Admin only)"""
    user = User.find_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    User.delete_by_id(user_id)
    return jsonify({'message': 'User deleted successfully'}), 200