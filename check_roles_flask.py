from backend.app import app
from backend.database import db
from backend.models.user_model import User

with app.app_context():
    # Check what roles exist in the database
    print("Roles found in database:")
    roles = db.session.query(User.role).distinct().order_by(User.role).all()
    for role in roles:
        print(f"- {role[0]}")
    
    # Check if there are any operators
    print(f"\nUsers with 'operator' in role:")
    operators = User.query.filter(User.role.ilike('%operator%')).order_by(User.username).all()
    for op in operators:
        print(f"- {op.username}: {op.role}")
    
    # Check all users
    print(f"\nAll users:")
    all_users = User.query.order_by(User.username).all()
    for user in all_users:
        print(f"- {user.username}: {user.role}")