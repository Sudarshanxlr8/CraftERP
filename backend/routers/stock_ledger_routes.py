from flask import Blueprint
from middlewares.auth_middleware import token_required
from controllers.stock_ledger_controller import get_stock_ledger

stock_ledger_bp = Blueprint('stock_ledger', __name__)

@stock_ledger_bp.route('/stock-ledger/<int:product_id>', methods=['GET'])
@token_required
def get_ledger(product_id):
    return get_stock_ledger(product_id)