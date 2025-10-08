from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.routes import auth, pokemon
from fastapi.middleware.cors import CORSMiddleware
from app.database import get_db, engine, Base
import os
from dotenv import load_dotenv

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Obtener los orígenes permitidos desde variable de entorno
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:4200").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # URLs permitidas desde .env
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(pokemon.router, prefix="/api/pokemon", tags=["Pokemon"])

@app.get("/")
def home():
    return {"message": "¡Bienvenido al backend de Pokemon"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Probar conexión a la BD
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
            "environment": os.getenv("RAILWAY_ENVIRONMENT", "development")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Para desarrollo local
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)