from flask import jsonify, request, render_template
from models.bom_model import BOM, BOMItem, BOMOperation
from models.product_model import Product
from models.work_center import WorkCenter

def render_bom_create_page():
    return render_template('bom_create.html')

def create_bom():
    data = request.get_json()
    required_fields = ['bom_id', 'product_name', 'items', 'operations']
    if not all(key in data for key in required_fields):
        return jsonify({'error': 'Missing fields'}), 400

    bom_id = data['bom_id']
    if not bom_id:
        return jsonify({'error': 'BOM ID cannot be empty'}), 400

    if BOM.find_by_bom_id(bom_id):
        return jsonify({'error': 'BOM ID already exists'}), 400

    bom_obj = BOM.create(
        bom_id=bom_id,
        product_name=data['product_name']
    )

    for item in data['items']:
        raw_material_name = item['raw_material']['name']
        quantity = item['quantity']
        unit = item['unit']

        raw_material = Product.find_by_name_and_type(raw_material_name, 'raw')
        if not raw_material:
            raw_material_data = {
                'name': raw_material_name,
                'description': f'Raw material {raw_material_name}',
                'type': 'raw_material',
                'unit_of_measurement': unit,
                'current_stock_level': 0
            }
            raw_material = Product.create(raw_material_data)

        bom_obj.add_item(raw_material.to_dict()['id'], quantity, unit)

    for operation in data['operations']:
        operation_name = operation['operation_name']
        work_center_name = operation['work_center']['name']
        time_required = operation['time_required']

        work_center = WorkCenter.find_by_name(work_center_name)
        if not work_center:
            work_center_data = {
                'name': work_center_name,
                'description': f'Work center {work_center_name}',
                'hourly_cost': 0.0
            }
            work_center = WorkCenter.create(work_center_data)

        bom_obj.add_operation(operation_name, work_center.to_dict()['id'], time_required)

    return jsonify({'message': 'BOM created successfully', 'bom_id': bom_obj.to_dict()['id']}), 201

def get_boms():
    boms = BOM.get_all_boms()
    return jsonify(boms), 200

def get_bom(bom_id):
    bom = BOM.find_by_id(bom_id)
    if not bom:
        return jsonify({'error': 'BOM not found'}), 404

    bom_data = bom.to_dict()

    items = []
    bom_items = BOMItem.find_by_bom_id(str(bom_data['id']))
    for item in bom_items:
        raw_material = Product.find_by_id(item['raw_material_id'])
        items.append({
            'raw_material': {'id': str(raw_material['_id']), 'name': raw_material['name']},
            'quantity': item['quantity'],
            'unit': item['unit']
        })

    operations = []
    bom_operations = BOMOperation.find_by_bom_id(str(bom_data['id']))
    for op in bom_operations:
        work_center = WorkCenter.find_by_id(op['work_center_id'])
        operations.append({
            'work_center': {'id': str(work_center['_id']), 'name': work_center['name']},
            'operation_name': op['operation_name'],
            'duration': op['duration']
        })

    bom_data['items'] = items
    bom_data['operations'] = operations

    return jsonify(bom_data), 200

def update_bom(bom_id):
    data = request.get_json()
    required_fields = ['bom_id', 'product_name', 'items', 'operations']
    if not all(key in data for key in required_fields):
        return jsonify({'error': 'Missing fields'}), 400

    bom = BOM.find_by_id(bom_id)
    if not bom:
        return jsonify({'error': 'BOM not found'}), 404

    existing_bom = BOM.find_by_bom_id_excluding(data['bom_id'], str(bom['_id']))
    if existing_bom:
        return jsonify({'error': 'BOM ID already exists'}), 400

    update_data = {
        'bom_id': data['bom_id'],
        'product_name': data['product_name']
    }

    BOMItem.delete_by_bom_id(str(bom['_id']))
    BOMOperation.delete_by_bom_id(str(bom['_id']))

    for item in data['items']:
        component_name = item['component_name']
        quantity = item['quantity']
        unit = item['unit']
        
        component = Product.find_by_name_and_type(component_name, 'raw')
        if not component:
            component_data = {
                'name': component_name,
                'type': 'raw',
                'unit': unit
            }
            component_id = Product.create(component_data)
        else:
            component_id = str(component['_id'])
        
        BOMItem.create({
            'bom_id': str(bom['_id']),
            'raw_material_id': component_id,
            'quantity': quantity,
            'unit': unit
        })

    for op in data['operations']:
        BOMOperation.create({
            'bom_id': str(bom['_id']),
            'operation_name': op['name'],
            'work_center_id': op['work_center_id'],
            'time_required': op['time_required']
        })

    BOM.update_by_id(str(bom['_id']), update_data)
    return jsonify({'message': 'BOM updated'}), 200

def delete_bom(bom_id):
    bom = BOM.find_by_id(bom_id)
    if not bom:
        return jsonify({'error': 'BOM not found'}), 404

    BOMItem.delete_by_bom_id(str(bom['_id']))
    BOMOperation.delete_by_bom_id(str(bom['_id']))
    BOM.delete_by_id(bom_id)
    return jsonify({'message': 'BOM deleted'}), 200


def get_next_bom_id():
    last_bom = BOM.find_last_bom()
    if last_bom:
        last_id_num = int(last_bom['bom_id'].split('-')[1])
        next_id_num = last_id_num + 1
        next_bom_id = f'BOM-{next_id_num:03d}'
    else:
        next_bom_id = 'BOM-001'
    return jsonify({'next_bom_id': next_bom_id}), 200