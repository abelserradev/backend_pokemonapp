from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "tu_clave_secreta"  # Debería estar en .env

def create_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")