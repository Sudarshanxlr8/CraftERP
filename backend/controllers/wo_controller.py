from flask import request, jsonify, g

from models.mo_model import ManufacturingOrder
from models.user_model import User
from controllers.inventory_controller import update_inventory_on_completion
from models.stock_ledger_model import StockLedger
from models.inventory_model import Inventory
from models import WorkOrder
from models.product_model import Product
from flask import g

def create_wo(mo_id):
    data = request.get_json()
    if not 'assigned_to' in data:
        return jsonify({'error': 'Missing assigned_to'}), 400

    mo = ManufacturingOrder.find_by_id(mo_id)
    if not mo:
        return jsonify({'error': 'MO not found'}), 404

    wo_data = {
        'mo_id': mo_id,
        'assigned_to': data['assigned_to']
    }
    
    wo_id = WorkOrder.create(wo_data)
    return jsonify({'message': 'WO created', 'id': str(wo_id)}), 201

def update_wo_status(wo_id):
    data = request.get_json()
    if not 'status' in data:
        return jsonify({'error': 'Missing status'}), 400

    wo = WorkOrder.find_by_id(wo_id)
    if not wo:
        return jsonify({'error': 'WO not found'}), 404

    old_status = wo['status']
    update_data = {
        'status': data['status'],
        'comments': data.get('comments', wo['comments'])
    }

    WorkOrder.update_by_id(str(wo['_id']), update_data)

    # If newly completed, consume proportional raw materials
    if data['status'] == 'completed' and old_status != 'completed':
        mo = ManufacturingOrder.find_by_id(wo['mo_id'])
        work_orders = ManufacturingOrder.get_work_orders(str(mo['_id']))
        num_wos = len(work_orders)
        if num_wos == 0:
            return jsonify({'error': 'No work orders'}), 500

        # Proportional consumption
        portion = 1.0 / num_wos
        for comp in mo['required_components']:
            item_name = comp['item']
            quantity_to_consume = comp['quantity'] * portion

            # Update inventory
            inv = Inventory.find_by_item_name(item_name)
            if inv:
                new_quantity = inv['stock_quantity'] - quantity_to_consume
                Inventory.update_by_id(str(inv['_id']), {'stock_quantity': new_quantity})

            # Update ledger
            product = Product.find_by_name(item_name)
            if product:
                last_ledger = StockLedger.find_last_by_product_id(str(product['_id']))
                previous_balance = last_ledger['balance'] if last_ledger else 0
                new_balance = previous_balance - quantity_to_consume
                
                ledger_data = {
                    'product_id': str(product['_id']),
                    'reference': f'WO-{str(wo["_id"])}',
                    'stock_in': 0,
                    'stock_out': quantity_to_consume,
                    'balance': new_balance
                }
                StockLedger.create(ledger_data)

    # Check if all WOs for MO are completed
    work_orders = ManufacturingOrder.get_work_orders(str(mo['_id']))
    all_completed = all(w['status'] == 'completed' for w in work_orders)
    if all_completed:
        ManufacturingOrder.update_by_id(str(mo['_id']), {'status': 'completed'})
        # Update inventory for finished product
        update_inventory_on_completion(mo)

    return jsonify({'message': 'WO updated'}), 200


def get_assigned_work_orders():
    work_orders = WorkOrder.find_by_assigned_to(g.user['id'])
    return jsonify(work_orders), 200

def get_work_orders():
    work_orders = WorkOrder.find_all()
    return jsonify(work_orders), 200