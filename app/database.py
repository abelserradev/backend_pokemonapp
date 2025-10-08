from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.models.database import Base
import os
from dotenv import load_dotenv

load_dotenv()

# URL de conexión para Railway
DATABASE_URL = (
    os.getenv("MYSQL_DATABASE") or 
    os.getenv("DATABASE_URL") or 
    os.getenv("MYSQL_URL") or 
    os.getenv("MYSQL_DATABASE_URL")
)

# Limpiar espacios en blanco
if DATABASE_URL:
    DATABASE_URL = DATABASE_URL.strip()

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Convertir mysql:// a mysql+pymysql:// automáticamente
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    print(f"❌ Error al crear engine de base de datos: {e}")
    raise

# Función para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()