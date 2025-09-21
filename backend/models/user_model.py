from database import mongo, MongoDocument
from datetime import datetime, timedelta
import random
from bson import ObjectId

class User:
    """MongoDB User model"""
    
    def __init__(self, data=None):
        if data is None:
            data = {}
        self.data = data
        self.collection = mongo.db.users
    
    @classmethod
    def create(cls, username, email, password_hash, role="operator"):
        """Create a new user"""
        user_data = {
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'role': role,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'is_active': True,
            'last_login': None
        }
        result = mongo.db.users.insert_one(user_data)
        user_data['_id'] = result.inserted_id
        return cls(user_data)
    
    @classmethod
    def find_by_username(cls, username):
        """Find user by username"""
        user_data = mongo.db.users.find_one({'username': username})
        return cls(user_data) if user_data else None
    
    @classmethod
    def find_by_email(cls, email):
        """Find user by email"""
        user_data = mongo.db.users.find_one({'email': email})
        return cls(user_data) if user_data else None
    
    @classmethod
    def find_by_id(cls, user_id):
        """Find user by ID"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        user_data = mongo.db.users.find_one({'_id': user_id})
        return cls(user_data) if user_data else None
    
    def to_dict(self):
        """Convert user to dictionary"""
        if not self.data:
            return None
        return {
            'id': str(self.data.get('_id')),
            'username': self.data.get('username'),
            'email': self.data.get('email'),
            'role': self.data.get('role'),
            'is_active': self.data.get('is_active', True),
            'last_login': self.data.get('last_login'),
            'created_at': self.data.get('created_at'),
            'updated_at': self.data.get('updated_at')
        }
    
    def update_last_login(self):
        """Update user's last login time"""
        mongo.db.users.update_one(
            {'_id': self.data['_id']},
            {'$set': {'last_login': datetime.utcnow()}}
        )
    
    def update_password(self, new_password_hash):
        """Update user password"""
        mongo.db.users.update_one(
            {'_id': self.data['_id']},
            {'$set': {
                'password_hash': new_password_hash,
                'updated_at': datetime.utcnow()
            }}
        )
    
    @classmethod
    def get_all_users(cls, limit=None, skip=None):
        """Get all users with pagination"""
        cursor = mongo.db.users.find({})
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        users = []
        for user_data in cursor:
            users.append(cls(user_data).to_dict())
        return users
    
    @classmethod
    def count_users(cls, filter_dict=None):
        """Count users matching filter"""
        return mongo.db.users.count_documents(filter_dict or {})

class OtpToken:
    """MongoDB OTP Token model"""
    
    def __init__(self, data=None):
        if data is None:
            data = {}
        self.data = data
        self.collection = mongo.db.otp_tokens
    
    @classmethod
    def create(cls, user_id):
        """Create a new OTP token"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        otp_data = {
            'user_id': user_id,
            'otp_code': str(random.randint(100000, 999999)),
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(minutes=15),
            'is_used': False
        }
        result = mongo.db.otp_tokens.insert_one(otp_data)
        otp_data['_id'] = result.inserted_id
        return cls(otp_data)
    
    @classmethod
    def find_by_user_id(cls, user_id):
        """Find OTP token by user ID"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        otp_data = mongo.db.otp_tokens.find_one({
            'user_id': user_id,
            'is_used': False
        })
        return cls(otp_data) if otp_data else None
    
    @classmethod
    def find_by_otp_code(cls, otp_code):
        """Find OTP token by code"""
        otp_data = mongo.db.otp_tokens.find_one({
            'otp_code': otp_code,
            'is_used': False
        })
        return cls(otp_data) if otp_data else None
    
    def is_valid(self):
        """Check if OTP token is valid"""
        if not self.data:
            return False
        return (
            datetime.utcnow() <= self.data.get('expires_at') and 
            not self.data.get('is_used', False)
        )
    
    def mark_as_used(self):
        """Mark OTP token as used"""
        mongo.db.otp_tokens.update_one(
            {'_id': self.data['_id']},
            {'$set': {'is_used': True}}
        )
    
    def delete(self):
        """Delete OTP token"""
        mongo.db.otp_tokens.delete_one({'_id': self.data['_id']})