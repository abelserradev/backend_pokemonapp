from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.models.database import Base
import os
from dotenv import load_dotenv

# Cargar variables de entorno según el entorno
environment = os.getenv("ENVIRONMENT", "development")

# Producción: contenedor Docker, Railway, Coolify, etc. (sin .env.local)
if (
    environment == "production"
    or os.getenv("RAILWAY_ENVIRONMENT")
    or os.getenv("DOCKER_CONTAINER")
    or os.getenv("PORT")
):
    # PORT: compatibilidad con despliegues que solo inyectan PORT (p. ej. PaaS)
    environment = "production"
    print("☁️ Producción: variables desde el sistema / contenedor")
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

# pool_pre_ping: tras un reinicio de MySQL el pool conserva sockets muertos y el
# primer request explota con 2006/2013; el ping los descarta antes de usarlos.
# pool_recycle: MySQL mata conexiones idle a las 8h (wait_timeout); reciclamos antes.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=1800,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Función para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()