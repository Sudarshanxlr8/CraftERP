from flask import request, jsonify
from models.stock_ledger_model import StockLedger

def get_stock_ledger(product_id):
    ledgers = StockLedger.find_by_product_id(product_id)
    result = [{
        'date': l['created_at'].isoformat(),
        'product_id': l['product_id'],
        'reference': l['reference'],
        'stock_in': l['stock_in'],
        'stock_out': l['stock_out'],
        'balance': l['balance']
    } for l in ledgers]
    return jsonify(result), 200