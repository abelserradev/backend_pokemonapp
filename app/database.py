from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.models.database import Base
import os
from dotenv import load_dotenv

# Cargar variables de entorno según el entorno
environment = os.getenv("ENVIRONMENT", "development")

# En Railway, siempre usar variables de entorno del sistema
if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("PORT"):
    # Estamos en Railway - usar variables de entorno del sistema
    environment = "production"
    print("🚂 Detectado Railway - usando variables de entorno del sistema")
elif environment == "development":
    # Desarrollo local - cargar desde .env.local
    load_dotenv(".env.local")
    print("🏠 Modo desarrollo local - usando .env.local")
else:
    # Producción local - cargar desde variables de entorno
    load_dotenv()
    print("☁️ Modo producción local - usando variables de entorno")

# URL de conexión - Prioridad: variables de entorno > SQLite local
DATABASE_URL = (
    os.getenv("MYSQL_DATABASE") or 
    os.getenv("DATABASE_URL") or 
    os.getenv("MYSQL_URL") or 
    os.getenv("MYSQL_DATABASE_URL") or
    "sqlite:///./pokemon_local.db"  # Fallback: Base de datos local SQLite
)

# Limpiar espacios en blanco
if DATABASE_URL:
    DATABASE_URL = DATABASE_URL.strip()

# Convertir mysql:// a mysql+pymysql:// automáticamente
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    raise

# Función para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()