from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.models.user import UserCreate, UserLogin
from app.service.auth import create_user, authenticate_user, create_access_token
from datetime import timedelta

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/register")
async def register(user: UserCreate):
    try:
        result = create_user(user)
        return {"message": "Usuario registrado exitosamente", "user": result["user"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        print(f"Intentando login para: {form_data.username}")  # Debug log
        user = authenticate_user(form_data.username, form_data.password)
        if not user:
            print("Usuario no encontrado o contraseña incorrecta")  # Debug log
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")
        
        access_token_expires = timedelta(minutes=30)  # Corregido: usar valor directo
        access_token = create_access_token(
            data={"sub": user["email"]}, 
            expires_delta=access_token_expires
        )
        
        print(f"Login exitoso para: {user['email']}")  # Debug log
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
    except Exception as e:
        print(f"Error en login: {str(e)}")  # Debug log
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

    