from flask import Blueprint
from middlewares.auth_middleware import token_required, role_required
from controllers.inventory_controller import update_inventory

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/inventory', methods=['PUT'])
@token_required
@role_required(['Administrator', 'Inventory Manager'])
def update():
    return update_inventory()