import sys
import os
from datetime import datetime
from flask import Flask
from flask_pymongo import PyMongo
import re

# Add backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from utils.password_helper import hash_password


# Flask + Mongo setup
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/odoo_manufacturing"  # Update DB name if needed
mongo = PyMongo(app)


# --------- Email Validation ----------
def validate_email(email: str) -> bool:
    """Basic email format validation"""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None


# --------- Create/Update Admin ---------
def create_admin_user():
    """Create or update the admin user with static data"""
    print("Creating/Updating admin user...")

    # Static admin data as requested
    email = "admin@gmail.com"
    username = "admin"
    password = "admin123"
    role = "Administrator"
    
    if not validate_email(email):
        raise ValueError(f"Invalid email format: {email}")

    admin_user = mongo.db.users.find_one({'username': username})

    if admin_user:
        print("Admin user already exists. Updating role and permissions...")
        mongo.db.users.update_one(
            {'username': username},
            {'$set': {
                'role': role,
                'email': email,
                'is_active': True,
                'updated_at': datetime.utcnow(),
                'first_name': 'System',
                'last_name': 'Administrator',
                'department': 'IT',
                'phone': '+1-555-0100'
            }}
        )
        print("✅ Admin user updated successfully!")
    else:
        admin_data = {
            'username': username,
            'email': email,
            'password_hash': hash_password(password),
            'role': role,
            'is_active': True,
            'first_name': 'System',
            'last_name': 'Administrator',
            'department': 'IT',
            'phone': '+1-555-0100',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = mongo.db.users.insert_one(admin_data)
        print(f"✅ Admin user created with ID: {result.inserted_id}")


# --------- Seed Sample Users ---------
def create_sample_users():
    """Seed Manufacturing Manager, Operator, Inventory Manager"""
    print("\nCreating sample users...")

    sample_users = [
        {
            'username': 'manufacturing_manager',
            'email': 'manager@cracterp.com',
            'password': 'manager123',
            'role': 'manufacturing_manager'
        },
        {
            'username': 'operator',
            'email': 'operator@cracterp.com',
            'password': 'operator123',
            'role': 'operator'
        },
        {
            'username': 'inventory_manager',
            'email': 'inventory@cracterp.com',
            'password': 'inventory123',
            'role': 'inventory_manager'
        }
    ]

    for user in sample_users:
        if not validate_email(user['email']):
            print(f"❌ Invalid email format for {user['username']}: {user['email']}")
            continue

        existing_user = mongo.db.users.find_one({'username': user['username']})
        if existing_user:
            print(f"User '{user['username']}' already exists. Skipping...")
            continue

        new_user = {
            'username': user['username'],
            'email': user['email'],
            'password_hash': hash_password(user['password']),
            'role': user['role'],
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = mongo.db.users.insert_one(new_user)
        print(f"✅ User '{user['username']}' created with ID: {result.inserted_id}")


# --------- Main Runner ---------
def main():
    print("=== CraftERP Admin & User Seeder ===")
    try:
        print(f"Connected to database: {mongo.db.name}")
    except:
        print("Connected to MongoDB database")
    print("=" * 50)

    try:
        create_admin_user()
        create_sample_users()

        print("\n" + "=" * 50)
        print("🎉 Seeding completed successfully!")
        print("Login credentials:")
        print("Admin: admin@gmail.com / admin123")
        print("Manufacturing Manager: manufacturing_manager / manager123")
        print("Operator: operator / operator123")
        print("Inventory Manager: inventory_manager / inventory123")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

    return True


if __name__ == '__main__':
    with app.app_context():
        success = main()
        sys.exit(0 if success else 1)
