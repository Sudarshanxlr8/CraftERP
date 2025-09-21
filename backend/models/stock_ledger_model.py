from database import mongo
from datetime import datetime
from bson import ObjectId

class StockLedger:
    """MongoDB Stock Ledger model for tracking inventory movements"""
    
    def __init__(self, data=None):
        if data is None:
            data = {}
        self.data = data
        self.collection = mongo.db.stock_ledger
    
    @classmethod
    def create(cls, product_id, reference, stock_in=0, stock_out=0, balance=None):
        """Create a new stock ledger entry"""
        if isinstance(product_id, str):
            product_id = ObjectId(product_id)
        
        # Calculate balance if not provided
        if balance is None:
            # Get last balance for this product
            last_entry = cls.get_last_entry(product_id)
            if last_entry:
                balance = last_entry['balance'] + stock_in - stock_out
            else:
                balance = stock_in - stock_out
        
        ledger_data = {
            'product_id': product_id,
            'reference': reference,  # e.g., 'MO-123' or 'WO-456'
            'stock_in': stock_in,
            'stock_out': stock_out,
            'balance': balance,
            'created_at': datetime.utcnow()
        }
        result = mongo.db.stock_ledger.insert_one(ledger_data)
        ledger_data['_id'] = result.inserted_id
        return cls(ledger_data)
    
    @classmethod
    def find_by_id(cls, ledger_id):
        """Find stock ledger entry by ID"""
        if isinstance(ledger_id, str):
            ledger_id = ObjectId(ledger_id)
        ledger_data = mongo.db.stock_ledger.find_one({'_id': ledger_id})
        return cls(ledger_data) if ledger_data else None
    
    @classmethod
    def find_by_product_id(cls, product_id, limit=None, skip=None):
        """Find all ledger entries for a specific product"""
        if isinstance(product_id, str):
            product_id = ObjectId(product_id)
        
        cursor = mongo.db.stock_ledger.find({'product_id': product_id}).sort('created_at', -1)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        ledger_entries = []
        for ledger_data in cursor:
            ledger_entries.append(cls(ledger_data).to_dict())
        return ledger_entries
    
    @classmethod
    def find_by_reference(cls, reference, limit=None, skip=None):
        """Find ledger entries by reference (e.g., 'MO-123')"""
        cursor = mongo.db.stock_ledger.find({'reference': reference}).sort('created_at', -1)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        ledger_entries = []
        for ledger_data in cursor:
            ledger_entries.append(cls(ledger_data).to_dict())
        return ledger_entries
    
    @classmethod
    def get_last_entry(cls, product_id):
        """Get the last ledger entry for a product"""
        if isinstance(product_id, str):
            product_id = ObjectId(product_id)
        
        ledger_data = mongo.db.stock_ledger.find_one(
            {'product_id': product_id},
            sort=[('created_at', -1)]
        )
        return cls(ledger_data).to_dict() if ledger_data else None
    
    @classmethod
    def get_current_balance(cls, product_id):
        """Get current balance for a product"""
        last_entry = cls.get_last_entry(product_id)
        return last_entry['balance'] if last_entry else 0
    
    @classmethod
    def get_all_ledger_entries(cls, limit=None, skip=None):
        """Get all ledger entries with pagination"""
        cursor = mongo.db.stock_ledger.find({}).sort('created_at', -1)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        ledger_entries = []
        for ledger_data in cursor:
            ledger_entries.append(cls(ledger_data).to_dict())
        return ledger_entries
    
    def to_dict(self):
        """Convert stock ledger entry to dictionary"""
        if not self.data:
            return None
        return {
            'id': str(self.data.get('_id')),
            'product_id': str(self.data.get('product_id')),
            'reference': self.data.get('reference'),
            'stock_in': self.data.get('stock_in', 0),
            'stock_out': self.data.get('stock_out', 0),
            'balance': self.data.get('balance', 0),
            'created_at': self.data.get('created_at')
        }
    
    @classmethod
    def get_ledger_summary(cls, product_id, start_date=None, end_date=None):
        """Get ledger summary for a product within date range"""
        if isinstance(product_id, str):
            product_id = ObjectId(product_id)
        
        match_stage = {'product_id': product_id}
        
        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter['$gte'] = start_date
            if end_date:
                date_filter['$lte'] = end_date
            match_stage['created_at'] = date_filter
        
        pipeline = [
            {'$match': match_stage},
            {
                '$group': {
                    '_id': '$product_id',
                    'total_stock_in': {'$sum': '$stock_in'},
                    'total_stock_out': {'$sum': '$stock_out'},
                    'entries_count': {'$sum': 1},
                    'last_entry_date': {'$max': '$created_at'}
                }
            }
        ]
        
        result = list(mongo.db.stock_ledger.aggregate(pipeline))
        return result[0] if result else None
    
    @classmethod
    def search_ledger_entries(cls, search_term, limit=None, skip=None):
        """Search ledger entries by reference"""
        cursor = mongo.db.stock_ledger.find({
            'reference': {'$regex': search_term, '$options': 'i'}
        }).sort('created_at', -1)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        ledger_entries = []
        for ledger_data in cursor:
            ledger_entries.append(cls(ledger_data).to_dict())
        return ledger_entries
    
    @classmethod
    def count_ledger_entries(cls, filter_dict=None):
        """Count ledger entries matching filter"""
        return mongo.db.stock_ledger.count_documents(filter_dict or {})
    
    def delete(self):
        """Delete ledger entry"""
        mongo.db.stock_ledger.delete_one({'_id': self.data['_id']})