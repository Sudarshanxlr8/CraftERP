import re

def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_password(password):
    return len(password) >= 6

def validate_role(role):
    allowed_roles = ['Administrator', 'Manufacturing Manager', 'Operator', 'Inventory Manager']
    return role in allowed_roles