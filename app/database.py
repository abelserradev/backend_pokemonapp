from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.models.database import Base
import os
from dotenv import load_dotenv

load_dotenv()

# Debug: Mostrar TODAS las variables de entorno disponibles
print("🔍 DEBUG - TODAS las variables de entorno disponibles:")
for key, value in os.environ.items():
    print(f"  {key}: {value}")

print(f"🔍 DEBUG - Total de variables: {len(os.environ)}")

# URL de conexión para Railway
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL no encontrada en variables de entorno")
    print("🔍 Variables disponibles:", list(os.environ.keys()))
    print("🔍 Intentando usar variables alternativas...")
    
    # Intentar otras variables comunes de Railway
    DATABASE_URL = os.getenv("MYSQL_URL") or os.getenv("DATABASE_URL") or os.getenv("MYSQL_DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ No se encontró ninguna variable de base de datos")
        raise ValueError("DATABASE_URL environment variable is not set")
    else:
        print(f"✅ Usando variable alternativa: {DATABASE_URL[:50]}...")

# Convertir mysql:// a mysql+pymysql:// automáticamente
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)
    print("✅ URL convertida a pymysql driver")

print(f"DEBUG - DATABASE_URL: {DATABASE_URL[:50]}...")  # Solo mostrar los primeros 50 caracteres por seguridad

try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    print("✅ Database engine creado exitosamente")
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