from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.models.user import UserCreate, UserLogin
from app.models.database import User
from app.service.auth import create_user, authenticate_user, create_access_token, get_current_user
from app.database import get_db
from datetime import timedelta

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

@router.post("/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        result = create_user(user, db)
        return {"message": "Usuario registrado exitosamente", "user": result["user"]}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Endpoint de login con OAuth2PasswordRequestForm (espera form-data).
    NOTA: El frontend Angular debe usar /api/login/json en su lugar.
    """
    try:
        user = authenticate_user(form_data.username, form_data.password, db)
        if not user:
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")
        
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user.email}, 
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {"id": user.id, "email": user.email}
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

@router.post("/login/json")
async def login_json(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Endpoint de login que acepta JSON (para aplicaciones SPA como Angular).
    """
    # Log temporal para debug
    print(f"🔵 LOGIN JSON - Email: {credentials.email}, Password length: {len(credentials.password)}")
    
    try:
        user = authenticate_user(credentials.email, credentials.password, db)
        if not user:
            print(f"❌ Login fallido para: {credentials.email}")
            raise HTTPException(
                status_code=401, 
                detail="Credenciales incorrectas"
            )
        
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user.email}, 
            expires_delta=access_token_expires
        )
        
        print(f"✅ Login exitoso: {user.email}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {"id": user.id, "email": user.email}
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Exception: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=401, 
            detail="Credenciales incorrectas"
        )

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/user/profile")
async def get_user_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "created_at": current_user.created_at
    }

    