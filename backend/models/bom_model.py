from database import mongo, MongoDocument
from datetime import datetime
from bson import ObjectId

class BOM:
    """MongoDB BOM (Bill of Materials) model"""
    
    def __init__(self, data=None):
        if data is None:
            data = {}
        self.data = data
        self.collection = mongo.db.boms
    
    @classmethod
    def generate_next_bom_id(cls):
        last_bom = mongo.db.boms.find_one(sort=[('bom_id', -1)])
        if last_bom and last_bom['bom_id']:
            last_id_num = int(last_bom['bom_id'].split('-')[1])
            next_id_num = last_id_num + 1
            return f"BOM-{next_id_num:03d}"
        return "BOM-001"

    @classmethod
    def create(cls, product_name, bom_id=None, items=None, operations=None):
        """Create a new BOM"""
        if bom_id is None:
            bom_id = cls.generate_next_bom_id()
        bom_data = {
            'bom_id': bom_id,
            'product_name': product_name,
            'items': items or [],
            'operations': operations or [],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'is_active': True
        }
        result = mongo.db.boms.insert_one(bom_data)
        bom_data['_id'] = result.inserted_id
        return cls(bom_data)
    
    @classmethod
    def find_by_id(cls, bom_id):
        """Find BOM by MongoDB ID"""
        if isinstance(bom_id, str):
            bom_id = ObjectId(bom_id)
        bom_data = mongo.db.boms.find_one({'_id': bom_id})
        return cls(bom_data) if bom_data else None
    
    @classmethod
    def find_by_bom_id(cls, bom_id):
        """Find BOM by custom BOM ID"""
        bom_data = mongo.db.boms.find_one({'bom_id': bom_id})
        return cls(bom_data) if bom_data else None
    
    @classmethod
    def find_by_product_name(cls, product_name):
        """Find BOMs by product name"""
        bom_data = mongo.db.boms.find({'product_name': product_name})
        return [cls(bom) for bom in bom_data]
    
    @classmethod
    def get_all_boms(cls, limit=None, skip=None):
        """Get all BOMs with pagination"""
        cursor = mongo.db.boms.find({})
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        boms = []
        for bom_data in cursor:
            boms.append(cls(bom_data).to_dict())
        return boms
    
    def to_dict(self):
        """Convert BOM to dictionary"""
        if not self.data:
            return None
        return {
            'id': str(self.data.get('_id')),
            'bom_id': self.data.get('bom_id'),
            'product_name': self.data.get('product_name'),
            'items': self.data.get('items', []),
            'operations': self.data.get('operations', []),
            'is_active': self.data.get('is_active', True),
            'created_at': self.data.get('created_at'),
            'updated_at': self.data.get('updated_at')
        }
    
    def add_item(self, raw_material_id, quantity, unit):
        """Add item to BOM"""
        new_item = {
            'raw_material_id': raw_material_id,
            'quantity': quantity,
            'unit': unit,
            'created_at': datetime.utcnow()
        }
        mongo.db.boms.update_one(
            {'_id': self.data['_id']},
            {
                '$push': {'items': new_item},
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
    
    def add_operation(self, operation_name, work_center_id, time_required):
        """Add operation to BOM"""
        new_operation = {
            'operation_name': operation_name,
            'work_center_id': work_center_id,
            'time_required': time_required,
            'created_at': datetime.utcnow()
        }
        mongo.db.boms.update_one(
            {'_id': self.data['_id']},
            {
                '$push': {'operations': new_operation},
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
    
    def update_items(self, items):
        """Update BOM items"""
        mongo.db.boms.update_one(
            {'_id': self.data['_id']},
            {
                '$set': {
                    'items': items,
                    'updated_at': datetime.utcnow()
                }
            }
        )
    
    def update_operations(self, operations):
        """Update BOM operations"""
        mongo.db.boms.update_one(
            {'_id': self.data['_id']},
            {
                '$set': {
                    'operations': operations,
                    'updated_at': datetime.utcnow()
                }
            }
        )
    
    def delete(self):
        """Delete BOM"""
        mongo.db.boms.delete_one({'_id': self.data['_id']})
    
    @classmethod
    def count_boms(cls, filter_dict=None):
        """Count BOMs matching filter"""
        return mongo.db.boms.count_documents(filter_dict or {})

class BOMItem:
    """MongoDB BOM Item model (embedded in BOM)"""
    
    @staticmethod
    def create_item(raw_material_id, quantity, unit):
        """Create a BOM item dictionary"""
        return {
            'raw_material_id': raw_material_id,
            'quantity': quantity,
            'unit': unit,
            'created_at': datetime.utcnow()
        }

class BOMOperation:
    """MongoDB BOM Operation model (embedded in BOM)"""
    
    @staticmethod
    def create_operation(operation_name, work_center_id, time_required):
        """Create a BOM operation dictionary"""
        return {
            'operation_name': operation_name,
            'work_center_id': work_center_id,
            'time_required': time_required,
            'created_at': datetime.utcnow()
        }