from flask import Blueprint, render_template, g, jsonify
from middlewares.auth_middleware import token_required, role_required
from controllers.mo_controller import create_mo, get_mos, get_mo, update_mo_status, get_mo_work_orders
from models.bom_model import BOM
from models.user_model import User
from database import mongo
from datetime import datetime, date

mo_bp = Blueprint('mo', __name__)

@mo_bp.route('/mo/create')
@token_required
@role_required(['Administrator', 'Manufacturing Manager', 'Operator'])
def create_page():
    """Serve the MO creation page with required data"""
    # Get all active BOMs
    boms = BOM.get_all_boms()
    
    # Get users with proper roles (Manufacturing Manager and Operator)
    assignees = User.get_all_users()
    # Filter for manufacturing manager and operator roles
    assignees = [user for user in assignees if 'manufacturing manager' in user['role'].lower() or 'operator' in user['role'].lower()]
    
    # Get today's date for date picker constraints
    today = date.today().isoformat()
    
    return render_template('mo_create.html', 
                         boms=boms, 
                         assignees=assignees, 
                         today=today)

@mo_bp.route('/mos', methods=['POST'])
@token_required
def create():
    return create_mo()

@mo_bp.route('/mos', methods=['GET'])
@token_required
def get_all():
    return get_mos()

@mo_bp.route('/mos/<string:mo_id>', methods=['GET'])
@token_required
def get_one(mo_id):
    return get_mo(mo_id)

@mo_bp.route('/mos/<string:mo_id>/status', methods=['PUT'])
@token_required
@role_required(['Administrator', 'Manufacturing Manager'])
def update_status(mo_id):
    return update_mo_status(mo_id)

@mo_bp.route('/mos/<string:mo_id>/work-orders', methods=['GET'])
@token_required
def get_work_orders(mo_id):
    return get_mo_work_orders(mo_id)

@mo_bp.route('/operators', methods=['GET'])
def get_operators():
    """Get all users with operator role for assignment"""
    try:
        # Use MongoDB syntax to find users with operator or manufacturing manager roles
        users = mongo.db.users.find({
            '$or': [
                {'role': {'$regex': 'operator', '$options': 'i'}},
                {'role': {'$regex': 'manufacturing manager', '$options': 'i'}}
            ]
        })
        
        users_data = []
        for user_data in users:
            user = User(user_data)
            users_data.append(user.to_dict())
        
        return jsonify({'users': users_data}), 200
    except Exception as e:
        return jsonify({'error': 'Error fetching operators', 'message': str(e)}), 500