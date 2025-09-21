from database import mongo
from datetime import datetime
from bson import ObjectId

class WorkCenter:
    """MongoDB Work Center model"""
    
    def __init__(self, data=None):
        if data is None:
            data = {}
        self.data = data
        self.collection = mongo.db.work_centers
    
    @classmethod
    def create(cls, name, description=None, hourly_cost_rate=0.0, status='active', capacity=1, efficiency=1.0):
        """Create a new work center"""
        wc_data = {
            'name': name,
            'description': description or '',
            'hourly_cost_rate': hourly_cost_rate,
            'status': status,  # active, inactive, maintenance
            'capacity': capacity,
            'efficiency': efficiency,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = mongo.db.work_centers.insert_one(wc_data)
        wc_data['_id'] = result.inserted_id
        return cls(wc_data)
    
    @classmethod
    def find_by_id(cls, wc_id):
        """Find work center by ID"""
        if isinstance(wc_id, str):
            wc_id = ObjectId(wc_id)
        wc_data = mongo.db.work_centers.find_one({'_id': wc_id})
        return cls(wc_data) if wc_data else None
    
    @classmethod
    def find_by_name(cls, name):
        """Find work center by name"""
        wc_data = mongo.db.work_centers.find_one({'name': name})
        return cls(wc_data) if wc_data else None
    
    @classmethod
    def find_all(cls, limit=None, skip=None):
        """Get all work centers with pagination"""
        cursor = mongo.db.work_centers.find({}).sort('created_at', -1)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        work_centers = []
        for wc_data in cursor:
            work_centers.append(cls(wc_data).to_dict())
        return work_centers
    
    @classmethod
    def update_by_id(cls, wc_id, update_data):
        """Update work center by ID"""
        if isinstance(wc_id, str):
            wc_id = ObjectId(wc_id)
        update_data['updated_at'] = datetime.utcnow()
        mongo.db.work_centers.update_one(
            {'_id': wc_id},
            {'$set': update_data}
        )
    
    def to_dict(self):
        """Convert work center to dictionary"""
        if not self.data:
            return None
        return {
            'id': str(self.data.get('_id')),
            'name': self.data.get('name'),
            'description': self.data.get('description', ''),
            'hourly_cost_rate': self.data.get('hourly_cost_rate', 0.0),
            'status': self.data.get('status', 'active'),
            'capacity': self.data.get('capacity', 1),
            'efficiency': self.data.get('efficiency', 1.0),
            'created_at': self.data.get('created_at'),
            'updated_at': self.data.get('updated_at')
        }
    
    def delete(self):
        """Delete work center"""
        mongo.db.work_centers.delete_one({'_id': self.data['_id']})
    
    @classmethod
    def count_work_centers(cls, filter_dict=None):
        """Count work centers matching filter"""
        return mongo.db.work_centers.count_documents(filter_dict or {})