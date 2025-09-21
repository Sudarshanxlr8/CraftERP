from flask import Blueprint
from middlewares.auth_middleware import token_required, role_required
from controllers.product_controller import create_product, get_products

product_bp = Blueprint('product', __name__)

@product_bp.route('/products', methods=['POST'])
@token_required
@role_required(['Administrator', 'Manufacturing Manager'])
def create():
    return create_product()

@product_bp.route('/products', methods=['GET'])
@token_required
def get_all():
    return get_products()