from pydantic import BaseModel, validator

class UserCreate(BaseModel):
    email: str
    password: str
    
    @validator('password')
    def validate_password_length(cls, v):
        # Truncar automáticamente si es muy larga
        if len(v.encode('utf-8')) > 72:
            v = v.encode('utf-8')[:72].decode('utf-8', errors='ignore')
        if len(v) < 6:
            raise ValueError('La contraseña debe tener al menos 6 caracteres')
        return v
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Email inválido')
        return v.lower()

class UserResponse(BaseModel):
    id: int
    email: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str