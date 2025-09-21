from flask import request, jsonify
from models.inventory_model import Inventory
from models.stock_ledger_model import StockLedger
from models.mo_model import ManufacturingOrder

def update_inventory_on_completion(mo):
    # Subtract raw materials
    for comp in mo.required_components:
        inv = Inventory.find_by_item_name(comp['item'])
        if inv:
            new_quantity = inv['stock_quantity'] - comp['quantity']
            Inventory.update_by_id(str(inv['_id']), {'stock_quantity': new_quantity})
    
    # Add finished product
    # Only add finished product (raw materials handled per WO)
    product_inv = Inventory.find_by_item_name(mo['product_name'])
    if not product_inv:
        inv_data = {
            'item_name': mo['product_name'],
            'stock_quantity': 0
        }
        product_inv_id = Inventory.create(inv_data)
        product_inv = Inventory.find_by_id(product_inv_id)
    
    new_quantity = product_inv['stock_quantity'] + mo['quantity']
    Inventory.update_by_id(str(product_inv['_id']), {'stock_quantity': new_quantity})

    # Update ledger for finished product
    last_ledger = StockLedger.find_last_by_product_id(str(mo['product_id']))
    previous_balance = last_ledger['balance'] if last_ledger else 0
    new_balance = previous_balance + mo['quantity']
    
    ledger_data = {
        'product_id': str(mo['product_id']),
        'reference': f'MO-{mo["id"]}',
        'stock_in': mo['quantity'],
        'stock_out': 0,
        'balance': new_balance
    }
    StockLedger.create(ledger_data)

def get_inventory(item_name):
    inv = Inventory.find_by_item_name(item_name)
    if not inv:
        return {'error': 'Item not found'}
    return {'item_name': inv['item_name'], 'stock_quantity': inv['stock_quantity']}

def update_inventory():
    data = request.get_json()
    if not all(key in data for key in ['item_name', 'quantity_change']):
        return jsonify({'error': 'Missing fields'}), 400

    inv = Inventory.find_by_item_name(data['item_name'])
    if not inv:
        inv_data = {
            'item_name': data['item_name'],
            'stock_quantity': 0
        }
        inv_id = Inventory.create(inv_data)
        inv = Inventory.find_by_id(inv_id)

    new_quantity = inv['stock_quantity'] + data['quantity_change']
    Inventory.update_by_id(str(inv['_id']), {'stock_quantity': new_quantity})
    return jsonify({'message': 'Inventory updated'}), 200