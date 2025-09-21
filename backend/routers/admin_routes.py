from flask import Blueprint
from controllers.auth_controller import create_user
from middlewares.auth_middleware import auth_middleware

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/create-user', methods=['POST'])
@auth_middleware(roles=['Administrator'])  # Only admins can access
def create():
    return create_user()