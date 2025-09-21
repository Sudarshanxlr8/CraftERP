from flask import Blueprint, render_template
from middlewares.auth_middleware import token_required, role_required
from controllers.wo_controller import create_wo, update_wo_status, get_assigned_work_orders, get_work_orders

wo_bp = Blueprint('wo', __name__)

@wo_bp.route('/mos/<string:mo_id>/wos', methods=['POST'])
@token_required
@role_required(['Administrator', 'Manufacturing Manager'])
def create(mo_id):
    return create_wo(mo_id)

@wo_bp.route('/wos/<string:wo_id>/status', methods=['PUT'])
@token_required
def update_status(wo_id):
    return update_wo_status(wo_id)

@wo_bp.route('/wos/assigned', methods=['GET'])
@token_required
@role_required(['Operator'])
def get_assigned():
    return get_assigned_work_orders()

@wo_bp.route('/wos', methods=['GET'])
@token_required
@role_required(['Administrator', 'Manufacturing Manager'])
def get_all_work_orders():
    return get_work_orders()

@wo_bp.route('/wo-list')
@token_required
@role_required(['Administrator', 'Manufacturing Manager', 'Operator'])
def wo_list_page():
    """Render the work orders list page for operators and managers"""
    return render_template('wo_list.html')