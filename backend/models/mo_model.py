from database import mongo
from datetime import datetime, date
from bson import ObjectId

class ManufacturingOrder:
    """MongoDB Manufacturing Order model"""
    
    def __init__(self, data=None):
        if data is None:
            data = {}
        self.data = data
        self.collection = mongo.db.manufacturing_orders
    
    @classmethod
    def create(cls, bom_id, quantity, schedule_start, deadline, assignee_id, status='planned', **kwargs):
        """Create a new manufacturing order"""
        if isinstance(bom_id, str):
            bom_id = ObjectId(bom_id)
        if isinstance(assignee_id, str):
            assignee_id = ObjectId(assignee_id)
        
        mo_data = {
            'bom_id': bom_id,
            'quantity': quantity,
            'status': status,  # 'planned', 'in_progress', 'completed', 'cancelled'
            'schedule_start': schedule_start if isinstance(schedule_start, date) else datetime.fromisoformat(schedule_start).date(),
            'deadline': deadline if isinstance(deadline, date) else datetime.fromisoformat(deadline).date(),
            'assignee_id': assignee_id,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'notes': kwargs.get('notes', ''),
            'priority': kwargs.get('priority', 'medium'),  # low, medium, high
            'actual_start_date': kwargs.get('actual_start_date'),
            'actual_end_date': kwargs.get('actual_end_date'),
            'completed_quantity': kwargs.get('completed_quantity', 0),
            'scrap_quantity': kwargs.get('scrap_quantity', 0),
            'work_orders': [],  # Array of work order IDs
            'material_consumptions': [],  # Array of material consumption records
            'quality_checks': []  # Array of quality check records
        }
        result = mongo.db.manufacturing_orders.insert_one(mo_data)
        mo_data['_id'] = result.inserted_id
        return cls(mo_data)
    
    @classmethod
    def find_by_id(cls, mo_id):
        """Find manufacturing order by ID"""
        if isinstance(mo_id, str):
            mo_id = ObjectId(mo_id)
        mo_data = mongo.db.manufacturing_orders.find_one({'_id': mo_id})
        return cls(mo_data) if mo_data else None
    
    @classmethod
    def find_by_bom_id(cls, bom_id, limit=None, skip=None):
        """Find manufacturing orders by BOM ID"""
        if isinstance(bom_id, str):
            bom_id = ObjectId(bom_id)
        
        cursor = mongo.db.manufacturing_orders.find({'bom_id': bom_id}).sort('created_at', -1)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        mo_orders = []
        for mo_data in cursor:
            mo_orders.append(cls(mo_data).to_dict())
        return mo_orders
    
    @classmethod
    def find_by_assignee_id(cls, assignee_id, limit=None, skip=None):
        """Find manufacturing orders by assignee ID"""
        if isinstance(assignee_id, str):
            assignee_id = ObjectId(assignee_id)
        
        cursor = mongo.db.manufacturing_orders.find({'assignee_id': assignee_id}).sort('created_at', -1)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        mo_orders = []
        for mo_data in cursor:
            mo_orders.append(cls(mo_data).to_dict())
        return mo_orders
    
    @classmethod
    def find_by_status(cls, status, limit=None, skip=None):
        """Find manufacturing orders by status"""
        cursor = mongo.db.manufacturing_orders.find({'status': status}).sort('created_at', -1)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        mo_orders = []
        for mo_data in cursor:
            mo_orders.append(cls(mo_data).to_dict())
        return mo_orders
    
    @classmethod
    def find_by_date_range(cls, start_date, end_date, limit=None, skip=None):
        """Find manufacturing orders within date range"""
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date)
        
        cursor = mongo.db.manufacturing_orders.find({
            'schedule_start': {'$gte': start_date},
            'deadline': {'$lte': end_date}
        }).sort('schedule_start', 1)
        
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        mo_orders = []
        for mo_data in cursor:
            mo_orders.append(cls(mo_data).to_dict())
        return mo_orders
    
    @classmethod
    def get_all_manufacturing_orders(cls, limit=None, skip=None):
        """Get all manufacturing orders with pagination"""
        cursor = mongo.db.manufacturing_orders.find({}).sort('created_at', -1)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        mo_orders = []
        for mo_data in cursor:
            mo_orders.append(cls(mo_data).to_dict())
        return mo_orders
    
    def update_status(self, new_status, notes=None):
        """Update manufacturing order status"""
        update_data = {
            'status': new_status,
            'updated_at': datetime.utcnow()
        }
        
        # Update actual dates based on status
        if new_status == 'in_progress':
            update_data['actual_start_date'] = datetime.utcnow()
        elif new_status == 'completed':
            update_data['actual_end_date'] = datetime.utcnow()
        
        if notes:
            update_data['notes'] = notes
        
        mongo.db.manufacturing_orders.update_one(
            {'_id': self.data['_id']},
            {'$set': update_data}
        )
    
    def update_quantity(self, completed_quantity, scrap_quantity=0):
        """Update completed and scrap quantities"""
        mongo.db.manufacturing_orders.update_one(
            {'_id': self.data['_id']},
            {
                '$set': {
                    'completed_quantity': completed_quantity,
                    'scrap_quantity': scrap_quantity,
                    'updated_at': datetime.utcnow()
                }
            }
        )
    
    def add_work_order(self, work_order_id):
        """Add work order to manufacturing order"""
        if isinstance(work_order_id, str):
            work_order_id = ObjectId(work_order_id)
        
        mongo.db.manufacturing_orders.update_one(
            {'_id': self.data['_id']},
            {
                '$push': {'work_orders': work_order_id},
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
    
    def add_material_consumption(self, material_data):
        """Add material consumption record"""
        material_data['timestamp'] = datetime.utcnow()
        mongo.db.manufacturing_orders.update_one(
            {'_id': self.data['_id']},
            {
                '$push': {'material_consumptions': material_data},
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
    
    def add_quality_check(self, quality_check_data):
        """Add quality check record"""
        quality_check_data['timestamp'] = datetime.utcnow()
        mongo.db.manufacturing_orders.update_one(
            {'_id': self.data['_id']},
            {
                '$push': {'quality_checks': quality_check_data},
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
    
    def to_dict(self):
        """Convert manufacturing order to dictionary"""
        if not self.data:
            return None
        return {
            'id': str(self.data.get('_id')),
            'bom_id': str(self.data.get('bom_id')) if self.data.get('bom_id') else None,
            'quantity': self.data.get('quantity'),
            'status': self.data.get('status'),
            'schedule_start': self.data.get('schedule_start'),
            'deadline': self.data.get('deadline'),
            'assignee_id': str(self.data.get('assignee_id')) if self.data.get('assignee_id') else None,
            'notes': self.data.get('notes', ''),
            'priority': self.data.get('priority', 'medium'),
            'actual_start_date': self.data.get('actual_start_date'),
            'actual_end_date': self.data.get('actual_end_date'),
            'completed_quantity': self.data.get('completed_quantity', 0),
            'scrap_quantity': self.data.get('scrap_quantity', 0),
            'work_orders': [str(wo_id) for wo_id in self.data.get('work_orders', [])],
            'material_consumptions': self.data.get('material_consumptions', []),
            'quality_checks': self.data.get('quality_checks', []),
            'created_at': self.data.get('created_at'),
            'updated_at': self.data.get('updated_at')
        }
    
    def delete(self):
        """Delete manufacturing order"""
        mongo.db.manufacturing_orders.delete_one({'_id': self.data['_id']})
    
    @classmethod
    def count_manufacturing_orders(cls, filter_dict=None):
        """Count manufacturing orders matching filter"""
        return mongo.db.manufacturing_orders.count_documents(filter_dict or {})
    
    @classmethod
    def get_status_summary(cls):
        """Get summary of manufacturing orders by status"""
        pipeline = [
            {
                '$group': {
                    '_id': '$status',
                    'count': {'$sum': 1},
                    'total_quantity': {'$sum': '$quantity'}
                }
            }
        ]
        return list(mongo.db.manufacturing_orders.aggregate(pipeline))
    
    @classmethod
    def search_manufacturing_orders(cls, search_term, limit=None, skip=None):
        """Search manufacturing orders by notes or reference"""
        cursor = mongo.db.manufacturing_orders.find({
            '$or': [
                {'notes': {'$regex': search_term, '$options': 'i'}},
                {'reference': {'$regex': search_term, '$options': 'i'}}
            ]
        }).sort('created_at', -1)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        mo_orders = []
        for mo_data in cursor:
            mo_orders.append(cls(mo_data).to_dict())
        return mo_orders