from flask import Blueprint
from middlewares.auth_middleware import token_required
from controllers.report_controller import get_operator_report, get_manager_report, get_admin_report, get_inventory_report

report_bp = Blueprint('report', __name__)

@report_bp.route('/reports/operator', methods=['GET'])
@token_required
def operator():
    return get_operator_report()

@report_bp.route('/reports/manager', methods=['GET'])
@token_required
def manager():
    return get_manager_report()

@report_bp.route('/reports/admin', methods=['GET'])
@token_required
def admin():
    return get_admin_report()

@report_bp.route('/reports/inventory', methods=['GET'])
@token_required
def inventory():
    return get_inventory_report()