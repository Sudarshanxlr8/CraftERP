from flask import request, jsonify, render_template
from models.bom_model import BOM, BOMItem, BOMOperation
from models.product_model import Product

def render_bom_create_page():
    """Render the BOM create page"""
    return render_template('bom_create.html')

def create_bom():
    data = request.get_json()
    required_fields = ['bom_id', 'product_name', 'items', 'operations']
    if not all(key in data for key in required_fields):
        return jsonify({'error': 'Missing fields'}), 400

    # Check if BOM ID already exists
    existing_bom = BOM.find_by_bom_id(data['bom_id'])
    if existing_bom:
        return jsonify({'error': 'BOM ID already exists'}), 400

    # Process items - create or find products by name
    processed_items = []
    for item in data['items']:
        component_name = item['component_name']
        quantity = item['quantity']
        unit = item['unit']
        
        # Find or create the component product
        component = Product.find_by_name_and_type(component_name, 'raw')
        if not component:
            # Create new component product
            component_data = {
                'name': component_name,
                'type': 'raw',
                'unit': unit
            }
            component_id = Product.create(component_data)
        else:
            component_id = str(component['_id'])
        
        processed_items.append({
            'raw_material_id': component_id,
            'quantity': quantity,
            'unit': unit
        })

    # Process operations
    processed_operations = []
    for op in data['operations']:
        processed_operations.append({
            'operation_name': op['name'],
            'work_center_id': op['work_center_id'],
            'time_required': op['time_required']
        })

    # Create BOM with embedded items and operations
    bom = BOM.create(
        data['bom_id'], 
        data['product_name'],
        items=processed_items,
        operations=processed_operations
    )

    return jsonify({'message': 'BOM created', 'id': str(bom.data['_id']), 'bom_id': data['bom_id']}), 201

def update_bom(bom_id):
    data = request.get_json()
    required_fields = ['bom_id', 'product_name', 'items', 'operations']
    if not all(key in data for key in required_fields):
        return jsonify({'error': 'Missing fields'}), 400

    bom = BOM.find_by_id(bom_id)
    if not bom:
        return jsonify({'error': 'BOM not found'}), 404

    # Check if new BOM ID conflicts with existing ones (excluding current BOM)
    existing_bom = BOM.find_by_bom_id_excluding(data['bom_id'], str(bom['_id']))
    if existing_bom:
        return jsonify({'error': 'BOM ID already exists'}), 400

    # Update BOM fields
    update_data = {
        'bom_id': data['bom_id'],
        'product_name': data['product_name']
    }

    # Delete existing items and operations
    BOMItem.delete_by_bom_id(str(bom['_id']))
    BOMOperation.delete_by_bom_id(str(bom['_id']))

    # Add new components - create or find products by name
    for item in data['items']:
        component_name = item['component_name']
        quantity = item['quantity']
        unit = item['unit']
        
        # Find or create the component product
        component = Product.find_by_name_and_type(component_name, 'raw')
        if not component:
            # Create new component product
            component_data = {
                'name': component_name,
                'type': 'raw',
                'unit': unit
            }
            component_id = Product.create(component_data)
        else:
            component_id = str(component['_id'])
        
        bom_item_data = {
            'bom_id': str(bom['_id']),
            'raw_material_id': component_id,
            'quantity': quantity,
            'unit': unit
        }
        BOMItem.create(bom_item_data)

    # Add new operations
    for op in data['operations']:
        bom_op_data = {
            'bom_id': str(bom['_id']),
            'operation_name': op['name'],
            'work_center_id': op['work_center_id'],
            'time_required': op['time_required']
        }
        BOMOperation.create(bom_op_data)

    BOM.update_by_id(str(bom['_id']), update_data)
    return jsonify({'message': 'BOM updated'}), 200

def get_boms():
    boms = BOM.get_all_boms()
    return jsonify(boms), 200

def get_bom(bom_id):
    bom = BOM.find_by_id(bom_id)
    if not bom:
        return jsonify({'error': 'BOM not found'}), 404

    items = []
    bom_items = BOMItem.find_by_bom_id(str(bom['_id']))
    for item in bom_items:
        raw_material = Product.find_by_id(item['raw_material_id'])
        items.append({
            'raw_material': {'id': str(raw_material['_id']), 'name': raw_material['name']},
            'quantity': item['quantity'],
            'unit': item['unit']
        })

    operations = []
    bom_operations = BOMOperation.find_by_bom_id(str(bom['_id']))
    for op in bom_operations:
        operations.append({
            'name': op['operation_name'],
            'work_center_id': op['work_center_id'],
            'time_required': op['time_required']
        })

    return jsonify({
        'id': str(bom['_id']),
        'bom_id': bom['bom_id'],
        'product_name': bom['product_name'],
        'items': items,
        'operations': operations
    }), 200