from database import mongo, MongoDocument
from datetime import datetime
from bson import ObjectId

class Inventory:
    """MongoDB Inventory model"""
    
    def __init__(self, data=None):
        if data is None:
            data = {}
        self.data = data
        self.collection = mongo.db.inventory
    
    @classmethod
    def create(cls, item_name, stock_quantity=0, location='default', product_id=None):
        """Create a new inventory item"""
        inventory_data = {
            'item_name': item_name,
            'stock_quantity': stock_quantity,
            'location': location,
            'product_id': product_id,  # Reference to product if available
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'is_active': True
        }
        result = mongo.db.inventory.insert_one(inventory_data)
        inventory_data['_id'] = result.inserted_id
        return cls(inventory_data)
    
    @classmethod
    def find_by_id(cls, inventory_id):
        """Find inventory by MongoDB ID"""
        if isinstance(inventory_id, str):
            inventory_id = ObjectId(inventory_id)
        inventory_data = mongo.db.inventory.find_one({'_id': inventory_id})
        return cls(inventory_data) if inventory_data else None
    
    @classmethod
    def find_by_item_name(cls, item_name):
        """Find inventory by item name"""
        inventory_data = mongo.db.inventory.find_one({'item_name': item_name})
        return cls(inventory_data) if inventory_data else None
    
    @classmethod
    def find_by_product_id(cls, product_id):
        """Find inventory by product ID"""
        if isinstance(product_id, str):
            product_id = ObjectId(product_id)
        inventory_data = mongo.db.inventory.find_one({'product_id': product_id})
        return cls(inventory_data) if inventory_data else None
    
    @classmethod
    def find_by_location(cls, location, limit=None, skip=None):
        """Find inventory items by location"""
        cursor = mongo.db.inventory.find({'location': location})
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        inventory_items = []
        for inventory_data in cursor:
            inventory_items.append(cls(inventory_data).to_dict())
        return inventory_items
    
    @classmethod
    def get_all_inventory(cls, limit=None, skip=None):
        """Get all inventory items with pagination"""
        cursor = mongo.db.inventory.find({})
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        inventory_items = []
        for inventory_data in cursor:
            inventory_items.append(cls(inventory_data).to_dict())
        return inventory_items
    
    def to_dict(self):
        """Convert inventory to dictionary"""
        if not self.data:
            return None
        return {
            'id': str(self.data.get('_id')),
            'item_name': self.data.get('item_name'),
            'stock_quantity': self.data.get('stock_quantity', 0),
            'location': self.data.get('location', 'default'),
            'product_id': str(self.data.get('product_id')) if self.data.get('product_id') else None,
            'is_active': self.data.get('is_active', True),
            'created_at': self.data.get('created_at'),
            'updated_at': self.data.get('updated_at')
        }
    
    def update_stock(self, quantity):
        """Update stock quantity"""
        mongo.db.inventory.update_one(
            {'_id': self.data['_id']},
            {
                '$set': {
                    'stock_quantity': quantity,
                    'updated_at': datetime.utcnow()
                }
            }
        )
    
    def adjust_stock(self, adjustment):
        """Adjust stock quantity by adding/subtracting"""
        new_quantity = self.data.get('stock_quantity', 0) + adjustment
        self.update_stock(new_quantity)
        return new_quantity
    
    def update_location(self, new_location):
        """Update item location"""
        mongo.db.inventory.update_one(
            {'_id': self.data['_id']},
            {
                '$set': {
                    'location': new_location,
                    'updated_at': datetime.utcnow()
                }
            }
        )
    
    def delete(self):
        """Delete inventory item"""
        mongo.db.inventory.delete_one({'_id': self.data['_id']})
    
    @classmethod
    def count_inventory(cls, filter_dict=None):
        """Count inventory items matching filter"""
        return mongo.db.inventory.count_documents(filter_dict or {})
    
    @classmethod
    def search_inventory(cls, search_term, limit=None, skip=None):
        """Search inventory by item name"""
        cursor = mongo.db.inventory.find({
            'item_name': {'$regex': search_term, '$options': 'i'}
        })
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        inventory_items = []
        for inventory_data in cursor:
            inventory_items.append(cls(inventory_data).to_dict())
        return inventory_items