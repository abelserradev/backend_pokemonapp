from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.models.user import UserCreate, UserLogin


secret_key = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
algorithm = "HS256"
acecess_token_expire_minutes = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

fake_users_db = {}

def create_user(user_data: UserCreate):
    user_id = len(fake_users_db) + 1
    hashed_password = get_password_hash(user_data.password)
    user = {
        "id": user_id,
        "email": user_data.email,
        "hashed_password": hashed_password,
    }
    fake_users_db[user_data.email] = user
    return {"message": "Usuario creado", "user": user}

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_user(user_data: dict):
    return {"message": "Usuario creado", "user": user_data}

def get_user(email: str):
    if email in fake_users_db:
        user_dict = fake_users_db[email]
        return user_dict
    return None

def authenticate_user(email: str, password: str):
    user = get_user(email)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt