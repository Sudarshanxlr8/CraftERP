from flask import Blueprint
from middlewares.auth_middleware import token_required, role_required
from controllers.bom_controller import create_bom, get_boms, update_bom, get_bom, render_bom_create_page, get_next_bom_id

bom_bp = Blueprint('bom', __name__)

@bom_bp.route('/bom/create')
@token_required
@role_required(['Administrator', 'Manufacturing Manager'])
def bom_create_page():
    return render_bom_create_page()

@bom_bp.route('/boms/next_id', methods=['GET'])
@token_required
@role_required(['Administrator', 'Manufacturing Manager'])
def get_next_id():
    return get_next_bom_id()

@bom_bp.route('/boms', methods=['POST'])
@token_required
@role_required(['Administrator', 'Manufacturing Manager'])
def create():
    return create_bom()

@bom_bp.route('/boms', methods=['GET'])
@token_required
@role_required(['Administrator', 'Manufacturing Manager', 'Production Planner'])
def get_boms():
    return get_boms()

@bom_bp.route('/boms/<bom_id>', methods=['GET'])
@token_required
@role_required(['Administrator', 'Manufacturing Manager', 'Production Planner'])
def get_bom_by_id(bom_id):
    return get_bom(bom_id)

@bom_bp.route('/boms/<bom_id>', methods=['PUT'])
@token_required
@role_required(['Administrator', 'Manufacturing Manager'])
def update(bom_id):
    return update_bom(bom_id)

@bom_bp.route('/boms/<string:bom_id>', methods=['GET'])
@token_required
def get_single(bom_id):
    return get_bom(bom_id)
