from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# URL de conexión para Railway
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    # Reemplaza estos valores con los de tu Railway
    "mysql+pymysql://root:xJCPnVfqugVbCHiMieNZkDOcHzWDKzWX@mysql.railway.internal:3306/railway"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Función para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

        