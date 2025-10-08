from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# URL de conexión para Railway
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("⚠️  DATABASE_URL no encontrada. Usando configuración de desarrollo...")
    # Configuración por defecto para desarrollo local
    DATABASE_URL = "mysql+pymysql://root:tu_password@localhost:3306/pokemon"

print(f"DEBUG - DATABASE_URL: {DATABASE_URL}")

try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    print("DEBUG - Database connection successful")
except Exception as e:
    print(f"DEBUG - Database connection error: {e}")
    raise

# Función para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()