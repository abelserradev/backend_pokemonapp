from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from app.models.user import UserCreate
from app.models.database import User
from app.database import get_db
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración desde variables de entorno
secret_key = os.getenv("SECRET_KEY", "default-secret-key-change-this")
algorithm = "HS256"
access_token_expire_minutes = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

def create_user(user_data: UserCreate, db: Session):
    # Verificar si el usuario ya existe
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise ValueError("El usuario ya existe")
    
    hashed_password = get_password_hash(user_data.password)
    
    # Crear nuevo usuario
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {"message": "Usuario creado", "user": {"id": db_user.id, "email": db_user.email}}

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_user_by_email(email: str, db: Session):
    return db.query(User).filter(User.email == email).first()

def authenticate_user(email: str, password: str, db: Session):
    print(f"🔍 Autenticando: {email}")
    user = get_user_by_email(email, db)
    if not user:
        print(f"❌ Usuario no existe: {email}")
        return False
    
    print(f"✅ Usuario encontrado: {user.email}")
    is_valid = verify_password(password, user.hashed_password)
    print(f"🔑 Password válida: {is_valid}")
    
    if not is_valid:
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

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user