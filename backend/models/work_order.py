from database import mongo
from datetime import datetime
from bson import ObjectId

class WorkOrder:
    """MongoDB Work Order model"""
    
    def __init__(self, data=None):
        if data is None:
            data = {}
        self.data = data
        self.collection = mongo.db.work_orders
    
    @classmethod
    def create(cls, mo_id, operation_id, assigned_to=None, status='pending', **kwargs):
        """Create a new work order"""
        if isinstance(mo_id, str):
            mo_id = ObjectId(mo_id)
        if isinstance(operation_id, str):
            operation_id = ObjectId(operation_id)
        if assigned_to and isinstance(assigned_to, str):
            assigned_to = ObjectId(assigned_to)
        
        wo_data = {
            'mo_id': mo_id,
            'operation_id': operation_id,
            'assigned_to': assigned_to,
            'status': status,  # pending, in_progress, completed, cancelled
            'start_time': kwargs.get('start_time'),
            'end_time': kwargs.get('end_time'),
            'planned_duration': kwargs.get('planned_duration', 60),  # Duration in minutes
            'work_center': kwargs.get('work_center'),
            'notes': kwargs.get('notes', ''),
            'priority': kwargs.get('priority', 'medium'),  # low, medium, high
            'actual_duration': kwargs.get('actual_duration', 0),  # Actual duration in minutes
            'quality_check': kwargs.get('quality_check', False),  # Whether quality check is required
            'quality_status': kwargs.get('quality_status', 'pending'),  # pending, passed, failed
            'quality_notes': kwargs.get('quality_notes', ''),
            'materials_consumed': [],  # Array of material consumption records
            'time_logs': [],  # Array of time tracking entries
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = mongo.db.work_orders.insert_one(wo_data)
        wo_data['_id'] = result.inserted_id
        return cls(wo_data)
    
    @classmethod
    def find_by_id(cls, wo_id):
        """Find work order by ID"""
        if isinstance(wo_id, str):
            wo_id = ObjectId(wo_id)
        wo_data = mongo.db.work_orders.find_one({'_id': wo_id})
        return cls(wo_data) if wo_data else None
    
    @classmethod
    def find_by_mo_id(cls, mo_id, limit=None, skip=None):
        """Find work orders by manufacturing order ID"""
        if isinstance(mo_id, str):
            mo_id = ObjectId(mo_id)
        
        cursor = mongo.db.work_orders.find({'mo_id': mo_id}).sort('created_at', -1)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        work_orders = []
        for wo_data in cursor:
            work_orders.append(cls(wo_data).to_dict())
        return work_orders
    
    @classmethod
    def find_by_operation_id(cls, operation_id, limit=None, skip=None):
        """Find work orders by operation ID"""
        if isinstance(operation_id, str):
            operation_id = ObjectId(operation_id)
        
        cursor = mongo.db.work_orders.find({'operation_id': operation_id}).sort('created_at', -1)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        work_orders = []
        for wo_data in cursor:
            work_orders.append(cls(wo_data).to_dict())
        return work_orders
    
    @classmethod
    def find_by_assignee_id(cls, assignee_id, limit=None, skip=None):
        """Find work orders by assignee ID"""
        if isinstance(assignee_id, str):
            assignee_id = ObjectId(assignee_id)
        
        cursor = mongo.db.work_orders.find({'assigned_to': assignee_id}).sort('created_at', -1)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        work_orders = []
        for wo_data in cursor:
            work_orders.append(cls(wo_data).to_dict())
        return work_orders
    
    @classmethod
    def find_by_status(cls, status, limit=None, skip=None):
        """Find work orders by status"""
        cursor = mongo.db.work_orders.find({'status': status}).sort('created_at', -1)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        work_orders = []
        for wo_data in cursor:
            work_orders.append(cls(wo_data).to_dict())
        return work_orders
    
    @classmethod
    def find_by_work_center(cls, work_center, limit=None, skip=None):
        """Find work orders by work center"""
        cursor = mongo.db.work_orders.find({'work_center': work_center}).sort('created_at', -1)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        work_orders = []
        for wo_data in cursor:
            work_orders.append(cls(wo_data).to_dict())
        return work_orders
    
    @classmethod
    def find_by_quality_status(cls, quality_status, limit=None, skip=None):
        """Find work orders by quality status"""
        cursor = mongo.db.work_orders.find({'quality_status': quality_status}).sort('created_at', -1)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        work_orders = []
        for wo_data in cursor:
            work_orders.append(cls(wo_data).to_dict())
        return work_orders
    
    @classmethod
    def get_all_work_orders(cls, limit=None, skip=None):
        """Get all work orders with pagination"""
        cursor = mongo.db.work_orders.find({}).sort('created_at', -1)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        work_orders = []
        for wo_data in cursor:
            work_orders.append(cls(wo_data).to_dict())
        return work_orders
    
    def update_status(self, new_status, notes=None):
        """Update work order status"""
        update_data = {
            'status': new_status,
            'updated_at': datetime.utcnow()
        }
        
        # Update actual dates based on status
        if new_status == 'in_progress':
            update_data['start_time'] = datetime.utcnow()
        elif new_status == 'completed':
            update_data['end_time'] = datetime.utcnow()
            # Calculate actual duration if start_time exists
            if self.data.get('start_time'):
                actual_duration = (datetime.utcnow() - self.data['start_time']).total_seconds() / 60
                update_data['actual_duration'] = actual_duration
        
        if notes:
            update_data['notes'] = notes
        
        mongo.db.work_orders.update_one(
            {'_id': self.data['_id']},
            {'$set': update_data}
        )
    
    def assign_to_operator(self, assignee_id):
        """Assign work order to operator"""
        if isinstance(assignee_id, str):
            assignee_id = ObjectId(assignee_id)
        
        mongo.db.work_orders.update_one(
            {'_id': self.data['_id']},
            {
                '$set': {
                    'assigned_to': assignee_id,
                    'updated_at': datetime.utcnow()
                }
            }
        )
    
    def update_quality_status(self, quality_status, quality_notes=None):
        """Update quality check status"""
        update_data = {
            'quality_status': quality_status,
            'updated_at': datetime.utcnow()
        }
        
        if quality_notes:
            update_data['quality_notes'] = quality_notes
        
        mongo.db.work_orders.update_one(
            {'_id': self.data['_id']},
            {'$set': update_data}
        )
    
    def add_material_consumption(self, material_data):
        """Add material consumption record"""
        material_data['timestamp'] = datetime.utcnow()
        mongo.db.work_orders.update_one(
            {'_id': self.data['_id']},
            {
                '$push': {'materials_consumed': material_data},
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
    
    def add_time_log(self, time_log_data):
        """Add time tracking entry"""
        time_log_data['timestamp'] = datetime.utcnow()
        mongo.db.work_orders.update_one(
            {'_id': self.data['_id']},
            {
                '$push': {'time_logs': time_log_data},
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
    
    def to_dict(self):
        """Convert work order to dictionary"""
        if not self.data:
            return None
        return {
            'id': str(self.data.get('_id')),
            'mo_id': str(self.data.get('mo_id')) if self.data.get('mo_id') else None,
            'operation_id': str(self.data.get('operation_id')) if self.data.get('operation_id') else None,
            'assigned_to': str(self.data.get('assigned_to')) if self.data.get('assigned_to') else None,
            'status': self.data.get('status', 'pending'),
            'start_time': self.data.get('start_time'),
            'end_time': self.data.get('end_time'),
            'planned_duration': self.data.get('planned_duration', 60),
            'actual_duration': self.data.get('actual_duration', 0),
            'work_center': self.data.get('work_center'),
            'notes': self.data.get('notes', ''),
            'priority': self.data.get('priority', 'medium'),
            'quality_check': self.data.get('quality_check', False),
            'quality_status': self.data.get('quality_status', 'pending'),
            'quality_notes': self.data.get('quality_notes', ''),
            'materials_consumed': self.data.get('materials_consumed', []),
            'time_logs': self.data.get('time_logs', []),
            'created_at': self.data.get('created_at'),
            'updated_at': self.data.get('updated_at')
        }
    
    def delete(self):
        """Delete work order"""
        mongo.db.work_orders.delete_one({'_id': self.data['_id']})
    
    @classmethod
    def count_work_orders(cls, filter_dict=None):
        """Count work orders matching filter"""
        return mongo.db.work_orders.count_documents(filter_dict or {})
    
    @classmethod
    def get_status_summary(cls):
        """Get summary of work orders by status"""
        pipeline = [
            {
                '$group': {
                    '_id': '$status',
                    'count': {'$sum': 1}
                }
            }
        ]
        return list(mongo.db.work_orders.aggregate(pipeline))
    
    @classmethod
    def search_work_orders(cls, search_term, limit=None, skip=None):
        """Search work orders by notes or work center"""
        cursor = mongo.db.work_orders.find({
            '$or': [
                {'notes': {'$regex': search_term, '$options': 'i'}},
                {'work_center': {'$regex': search_term, '$options': 'i'}}
            ]
        }).sort('created_at', -1)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        work_orders = []
        for wo_data in cursor:
            work_orders.append(cls(wo_data).to_dict())
        return work_orders