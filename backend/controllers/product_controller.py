from flask import request, jsonify
from models.product_model import Product

def create_product():
    data = request.get_json()
    required_fields = ['name', 'type', 'unit']
    if not all(key in data for key in required_fields):
        return jsonify({'error': 'Missing fields'}), 400

    if data['type'] not in ['raw', 'finished']:
        return jsonify({'error': 'Invalid type (must be "raw" or "finished")'}), 400

    product_data = {
        'name': data['name'],
        'type': data['type'],
        'unit': data['unit']
    }
    
    product_id = Product.create(product_data)
    return jsonify({'message': 'Product created', 'id': str(product_id)}), 201

def get_products():
    products = Product.find_all()
    result = [{
        'id': str(p['id']),
        'name': p['name'],
        'type': p['type'],
        'unit': p['unit'],
        'created_at': p['created_at'].isoformat()
    } for p in products]
    return jsonify(result), 200