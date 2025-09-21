from flask import request, jsonify
from models import WorkCenter

# Role decorators are applied at route level, not needed here
def create_workcenter():
    data = request.json
    required_fields = ['name', 'hourly_cost_rate', 'capacity']
    if not all(key in data for key in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if work center name already exists
    existing = WorkCenter.find_by_name(data['name'])
    if existing:
        return jsonify({'error': 'Work center name already exists'}), 400
    
    wc = WorkCenter.create(
        name=data['name'],
        description=data.get('description', ''),
        hourly_cost_rate=data['hourly_cost_rate'],
        status=data.get('status', 'active'),
        capacity=data['capacity'],
        efficiency=data.get('efficiency', 1.0)
    )
    return jsonify({'message': 'Work center created successfully', 'id': str(wc.data['_id'])}), 201

def get_workcenters():
    workcenters = WorkCenter.find_all()
    return jsonify(workcenters)

def get_workcenter(id):
    wc = WorkCenter.find_by_id(id)
    if not wc:
        return jsonify({'error': 'Work center not found'}), 404
    return jsonify(wc.to_dict())

# Role decorator is already applied at route level, no need here
def update_workcenter(id):
    wc = WorkCenter.find_by_id(id)
    if not wc:
        return jsonify({'error': 'Work center not found'}), 404
    
    data = request.json
    update_data = {
        'name': data.get('name', wc.data.get('name')),
        'description': data.get('description', wc.data.get('description')),
        'hourly_cost_rate': data.get('hourly_cost_rate', wc.data.get('hourly_cost_rate'))
    }
    
    WorkCenter.update_by_id(id, update_data)
    return jsonify({'message': 'Work center updated successfully'})

def get_utilization(id):
    # Placeholder: Implement actual utilization calculation here (e.g., based on work orders)
    # For now, returning dummy data
    return jsonify({
        'rate': 75,  # Example utilization rate in %
        'downtime_hours': 2  # Example downtime hours
    })