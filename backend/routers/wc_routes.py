from flask import Blueprint
from middlewares.auth_middleware import token_required, role_required
from controllers.wc_controller import get_workcenters, get_workcenter, update_workcenter, get_utilization, create_workcenter

wc_bp = Blueprint('wc', __name__)

@wc_bp.route('/workcenters', methods=['POST'])
@token_required
@role_required(['Administrator', 'Manufacturing Manager'])
def create_workcenter_route():
    return create_workcenter()

@wc_bp.route('/workcenters', methods=['GET'])
def list_workcenters():
    return get_workcenters()

@wc_bp.route('/workcenters/<string:id>', methods=['GET'])
def workcenter_detail(id):
    return get_workcenter(id)

@wc_bp.route('/workcenters/<string:id>/update', methods=['PUT'])
@token_required
@role_required(['Administrator', 'Manufacturing Manager'])
def workcenter_update(id):
    return update_workcenter(id)

@wc_bp.route('/workcenters/<string:id>/utilization', methods=['GET'])
def workcenter_utilization(id):
    return get_utilization(id)