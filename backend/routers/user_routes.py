from flask import Blueprint
from controllers.user_controller import update_profile, get_all_users
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