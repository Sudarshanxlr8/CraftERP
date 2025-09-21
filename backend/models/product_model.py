from database import mongo, MongoDocument
from datetime import datetime
from bson import ObjectId

class Product:
    """MongoDB Product model"""
    
    def __init__(self, data=None):
        if data is None:
            data = {}
        self.data = data
        self.collection = mongo.db.products
    
    @classmethod
    def create(cls, name, product_type, unit, description=None, price=0.0):
        """Create a new product"""
        product_data = {
            'name': name,
            'type': product_type,  # 'raw' or 'finished'
            'unit': unit,  # 'pcs', 'kg', 'liters', etc.
            'description': description or '',
            'price': price,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'is_active': True
        }
        result = mongo.db.products.insert_one(product_data)
        product_data['_id'] = result.inserted_id
        return cls(product_data)
    
    @classmethod
    def find_by_id(cls, product_id):
        """Find product by MongoDB ID"""
        if isinstance(product_id, str):
            product_id = ObjectId(product_id)
        product_data = mongo.db.products.find_one({'_id': product_id})
        return cls(product_data) if product_data else None
    
    @classmethod
    def find_by_name(cls, name):
        """Find product by name"""
        product_data = mongo.db.products.find_one({'name': name})
        return cls(product_data) if product_data else None
    
    @classmethod
    def find_by_type(cls, product_type, limit=None, skip=None):
        """Find products by type (raw/finished)"""
        cursor = mongo.db.products.find({'type': product_type})
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        products = []
        for product_data in cursor:
            products.append(cls(product_data).to_dict())
        return products
    
    @classmethod
    def find_all(cls, limit=None, skip=None):
        """Get all products with pagination"""
        cursor = mongo.db.products.find({})
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        products = []
        for product_data in cursor:
            products.append(cls(product_data).to_dict())
        return products
    
    @classmethod
    def find_by_name_and_type(cls, name, product_type):
        """Find product by name and type"""
        product_data = mongo.db.products.find_one({'name': name, 'type': product_type})
        return cls(product_data) if product_data else None
    
    def to_dict(self):
        """Convert product to dictionary"""
        if not self.data:
            return None
        return {
            'id': str(self.data.get('_id')),
            'name': self.data.get('name'),
            'type': self.data.get('type'),
            'unit': self.data.get('unit'),
            'description': self.data.get('description', ''),
            'price': self.data.get('price', 0.0),
            'is_active': self.data.get('is_active', True),
            'created_at': self.data.get('created_at'),
            'updated_at': self.data.get('updated_at')
        }
    
    def update(self, update_data):
        """Update product"""
        update_data['updated_at'] = datetime.utcnow()
        mongo.db.products.update_one(
            {'_id': self.data['_id']},
            {'$set': update_data}
        )
    
    def delete(self):
        """Delete product"""
        mongo.db.products.delete_one({'_id': self.data['_id']})
    
    @classmethod
    def count_products(cls, filter_dict=None):
        """Count products matching filter"""
        return mongo.db.products.count_documents(filter_dict or {})
    
    @classmethod
    def search_products(cls, search_term, limit=None, skip=None):
        """Search products by name"""
        cursor = mongo.db.products.find({
            'name': {'$regex': search_term, '$options': 'i'}
        })
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        products = []
        for product_data in cursor:
            products.append(cls(product_data).to_dict())
        return products