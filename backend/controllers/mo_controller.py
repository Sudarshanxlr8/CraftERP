from flask import request, jsonify, g
from models.mo_model import ManufacturingOrder
from models.bom_model import BOM
from models.user_model import User
from datetime import datetime

def create_mo():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['bom_id', 'quantity', 'schedule_start', 'deadline', 'assignee_id']
    if not all(key in data for key in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Validate quantity
    try:
        quantity = int(data['quantity'])
        if quantity <= 0:
            return jsonify({'error': 'Quantity must be positive'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid quantity format'}), 400
    
    # Validate dates
    try:
        schedule_start = datetime.strptime(data['schedule_start'], '%Y-%m-%d').date()
        deadline = datetime.strptime(data['deadline'], '%Y-%m-%d').date()
        
        if deadline <= schedule_start:
            return jsonify({'error': 'Deadline must be after schedule start date'}), 400
            
        if schedule_start < datetime.now().date():
            return jsonify({'error': 'Schedule start date cannot be in the past'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    # Validate BOM exists
    bom = BOM.find_by_id(data['bom_id'])
    if not bom:
        return jsonify({'error': 'BOM not found'}), 404
    
    # Validate assignee exists and has proper role
    assignee = User.find_by_id(data['assignee_id'])
    if not assignee:
        return jsonify({'error': 'Assignee not found'}), 404
    
    if not (assignee['role'].lower() in ['manufacturing manager', 'operator'] or 
            'operator' in assignee['role'].lower() or 'manufacturing manager' in assignee['role'].lower()):
        return jsonify({'error': 'Assignee must be a Manufacturing Manager or Operator'}), 400
    
    # Create manufacturing order
    try:
        mo_data = {
            'bom_id': str(data['bom_id']),
            'quantity': quantity,
            'schedule_start': schedule_start,
            'deadline': deadline,
            'assignee_id': str(data['assignee_id']),
            'status': 'planned',
            'product_name': bom['product_name']
        }
        
        mo_id = ManufacturingOrder.create(mo_data)
        mo = ManufacturingOrder.find_by_id(mo_id)
        
        return jsonify({
            'message': 'Manufacturing Order created successfully',
            'id': str(mo['_id']),
            'mo': mo
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Failed to create manufacturing order: {str(e)}'}), 500

def get_mos():
    try:
        # Get query parameters
        status = request.args.get('status')
        assignee_id = request.args.get('assignee_id')
        
        # Get all manufacturing orders
        mos = ManufacturingOrder.find_all()
        
        # Filter by status if provided
        if status:
            mos = [mo for mo in mos if mo['status'] == status]
        
        # Filter by assignee_id if provided
        if assignee_id:
            mos = [mo for mo in mos if str(mo['assignee_id']) == assignee_id]
        
        return jsonify({
            'manufacturing_orders': mos,
            'total': len(mos)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch manufacturing orders: {str(e)}'}), 500

def get_mo(mo_id):
    try:
        mo = ManufacturingOrder.find_by_id(mo_id)
        if not mo:
            return jsonify({'error': 'Manufacturing Order not found'}), 404
            
        # Include work orders with operator details
        work_orders = ManufacturingOrder.get_work_orders(str(mo['_id']))
        
        mo['work_orders'] = work_orders
        
        return jsonify(mo), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch manufacturing order: {str(e)}'}), 500

def update_mo_status(mo_id):
    try:
        mo = ManufacturingOrder.find_by_id(mo_id)
        if not mo:
            return jsonify({'error': 'Manufacturing Order not found'}), 404
            
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'error': 'Status is required'}), 400
            
        valid_statuses = ['planned', 'in_progress', 'completed', 'cancelled']
        if new_status not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400
            
        update_data = {
            'status': new_status,
            'updated_at': datetime.utcnow()
        }
        
        ManufacturingOrder.update_by_id(str(mo['_id']), update_data)
        updated_mo = ManufacturingOrder.find_by_id(mo_id)
        
        return jsonify({
            'message': 'Manufacturing Order status updated successfully',
            'mo': updated_mo
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to update manufacturing order status: {str(e)}'}), 500

def get_mo_work_orders(mo_id):
    try:
        mo = ManufacturingOrder.find_by_id(mo_id)
        if not mo:
            return jsonify({'error': 'Manufacturing Order not found'}), 404
            
        work_orders = ManufacturingOrder.get_work_orders(str(mo['_id']))
            
        return jsonify({
            'work_orders': work_orders,
            'total': len(work_orders)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch work orders: {str(e)}'}), 500