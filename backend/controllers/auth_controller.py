from flask import request, jsonify
from app import db
from models.user_model import User
from utils.password_helper import hash_password, verify_password
from utils.jwt_helper import encode_jwt
from validators.auth_validator import validate_email, validate_password

def register_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not all([username, email, password]):
        return jsonify({'error': 'Missing fields'}), 400

    if not validate_email(email):
        return jsonify({'error': 'Invalid email'}), 400

    if not validate_password(password):
        return jupytext({'error': 'Password too short'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400

    password_hash = hash_password(password)
    user = User(username=username, email=email, password_hash=password_hash)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered', 'username': username}), 201

def login_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not all([email, password]):
        return jsonify({'error': 'Missing fields'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not verify_password(password, user.password_hash):
        return jsonify({'error': 'Invalid credentials'}), 401

    token = encode_jwt({'username': user.username})
    return jsonify({'token': token, 'username': user.username}), 200