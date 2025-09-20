import jwt
from datetime import datetime, timedelta
from config import Config

def encode_jwt(payload):
    payload['exp'] = datetime.utcnow() + timedelta(hours=1)
    return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')

def decode_jwt(token):
    try:
        return jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None