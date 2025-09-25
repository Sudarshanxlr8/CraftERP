from flask import Blueprint
from controllers.user_controller import update_profile, get_all_users, create_user, delete_user
from middlewares.auth_middleware import token_required, role_required

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['PUT'])
@token_required
def update():
    return update_profile()

@user_bp.route('/users', methods=['GET'])
@token_required
@role_required(['Administrator'])
def users():
    return get_all_users()

@user_bp.route('/users', methods=['POST'])
@token_required
@role_required(['Administrator'])
def add_user():
    return create_user()

@user_bp.route('/users/<user_id>', methods=['DELETE'])
@token_required
@role_required(['Administrator'])
def remove_user(user_id):
    return delete_user(user_id)