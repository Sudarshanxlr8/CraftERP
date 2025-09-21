from flask import request, jsonify
from models.user_model import User, OtpToken
from utils.password_helper import hash_password, verify_password
from utils.jwt_helper import encode_jwt
from validators.auth_validator import validate_email, validate_password
from mail import mail
from flask_mail import Message
from datetime import datetime, timedelta
import random
import string

def validate_role(role):
    """
    Validate that the role is one of the allowed values
    """
    if not role or not isinstance(role, str):
        return False
        
    # Convert to lowercase for case-insensitive comparison
    role_lower = role.lower().strip()
    
    # Add all possible roles including 'Operator'
    allowed_roles = [
        'administrator', 'admin',
        'manufacturing manager', 
        'employee',
        'inventory manager',
        'operator',  # Add this line
        'staff',
        'supervisor'
    ]
    
    return role_lower in allowed_roles

def register_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')

    if not all([username, email, password, role]):
        return jsonify({'error': 'Missing fields'}), 400

    if role == 'Administrator':
        return jsonify({'error': 'Cannot register as Administrator via public signup'}), 403

    # Debug: Check which validation is failing
    email_valid = validate_email(email)
    password_valid = validate_password(password)
    role_valid = validate_role(role)
    
    print(f"Email validation: {email_valid}")
    print(f"Password validation: {password_valid}")
    print(f"Role validation: {role_valid}")
    print(f"Role received: {role}")

    if not email_valid or not password_valid or not role_valid:
        return jsonify({
            'error': 'Invalid input',
            'details': {
                'email_valid': email_valid,
                'password_valid': password_valid,
                'role_valid': role_valid,
                'role_received': role
            }
        }), 400

    if User.find_by_email(email) or User.find_by_username(username):
        return jsonify({'error': 'User already exists'}), 400

    password_hash = hash_password(password)
    user = User.create(username, email, password_hash, role)

    return jsonify({'message': 'User registered', 'username': username}), 201

def login_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not all([email, password]):
        return jsonify({'error': 'Missing fields'}), 400

    user = User.find_by_email(email)
    if not user or not verify_password(password, user.data.get('password_hash')):
        return jsonify({'error': 'Invalid credentials'}), 401

    # Create a user object for JWT encoding
    user_obj = type('User', (), {
        'id': str(user.data.get('_id')),
        'username': user.data.get('username'),
        'email': user.data.get('email'),
        'role': user.data.get('role')
    })()
    token = encode_jwt(user_obj)
    return jsonify({'token': token, 'username': user.data.get('username'), 'role': user.data.get('role')}), 200

def forgot_password():
    data = request.get_json()
    email = data.get('email')
    user = User.find_by_email(email)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    otp = ''.join(random.choices(string.digits, k=6))
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    otp_token = OtpToken.create(user.data.get('_id'))
    
    # Update the OTP token with the generated OTP
    otp_token.data['otp_code'] = otp
    otp_token.data['expires_at'] = expires_at
    otp_token.collection.update_one(
        {'_id': otp_token.data['_id']},
        {'$set': {'otp_code': otp, 'expires_at': expires_at}}
    )

    msg = Message('Password Reset OTP', recipients=[email])
    msg.body = f'Your OTP is {otp}. It expires in 10 minutes.'
    mail.send(msg)

    return jsonify({'message': 'OTP sent to email'}), 200

def reset_password():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')
    new_password = data.get('new_password')

    if not all([email, otp, new_password]) or not validate_password(new_password):
        return jsonify({'error': 'Invalid input'}), 400

    user = User.find_by_email(email)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    otp_token = OtpToken.find_by_otp_code(otp)
    if not otp_token or not otp_token.is_valid():
        return jsonify({'error': 'Invalid or expired OTP'}), 400

    user.update_password(hash_password(new_password))
    otp_token.mark_as_used()

    return jsonify({'message': 'Password reset successful'}), 200

# Protected: For admins to create users (including other admins)
def create_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')

    if not all([username, email, password, role]):
        return jsonify({'error': 'Missing fields'}), 400

    if not validate_email(email) or not validate_password(password) or not validate_role(role):
        return jsonify({'error': 'Invalid input'}), 400

    if User.find_by_email(email) or User.find_by_username(username):
        return jsonify({'error': 'User already exists'}), 400

    password_hash = hash_password(password)
    user = User.create(username, email, password_hash, role)

    return jsonify({'message': 'User created', 'username': username}), 201