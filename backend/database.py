from flask_pymongo import PyMongo
from pymongo import MongoClient
from datetime import datetime
import os

# Initialize PyMongo
mongo = PyMongo()

# Database collections will be accessed through mongo.db
# Example: mongo.db.users, mongo.db.boms, mongo.db.products

def get_db():
    """Get the MongoDB database instance"""
    return mongo.db

def init_db(app):
    """Initialize MongoDB with Flask app"""
    mongo.init_app(app)
    
    # Create indexes for better performance
    db = mongo.db
    
    # Create indexes for common queries
    if db is not None:
        # Users collection indexes
        db.users.create_index("username", unique=True)
        db.users.create_index("email", unique=True)
        
        # Products collection indexes
        db.products.create_index("product_code", unique=True)
        db.products.create_index("name")
        
        # BOM collection indexes
        db.boms.create_index("bom_id", unique=True)
        db.boms.create_index("product_id")
        
        # Manufacturing Orders collection indexes
        db.manufacturing_orders.create_index("order_number", unique=True)
        db.manufacturing_orders.create_index("status")
        
        # Inventory collection indexes
        db.inventory.create_index("product_id")
        db.inventory.create_index("location")
        
        # Stock Ledger collection indexes
        db.stock_ledger.create_index("product_id")
        db.stock_ledger.create_index("transaction_date")

class MongoDocument:
    """Base class for MongoDB documents with common methods"""
    
    @classmethod
    def find_by_id(cls, collection, document_id):
        """Find document by ID"""
        return collection.find_one({"_id": document_id})
    
    @classmethod
    def find_all(cls, collection, filter_dict=None, limit=None, skip=None):
        """Find all documents with optional filter"""
        cursor = collection.find(filter_dict or {})
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        return list(cursor)
    
    @classmethod
    def insert_one(cls, collection, document):
        """Insert a single document"""
        document['created_at'] = datetime.utcnow()
        document['updated_at'] = datetime.utcnow()
        result = collection.insert_one(document)
        return result.inserted_id
    
    @classmethod
    def update_one(cls, collection, filter_dict, update_dict):
        """Update a single document"""
        update_dict['$set']['updated_at'] = datetime.utcnow()
        result = collection.update_one(filter_dict, update_dict)
        return result.modified_count
    
    @classmethod
    def delete_one(cls, collection, filter_dict):
        """Delete a single document"""
        result = collection.delete_one(filter_dict)
        return result.deleted_count
    
    @classmethod
    def count_documents(cls, collection, filter_dict=None):
        """Count documents matching filter"""
        return collection.count_documents(filter_dict or {})