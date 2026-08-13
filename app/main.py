import asyncio
import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from app.routes import auth, pokemon
from fastapi.middleware.cors import CORSMiddleware
from app.database import get_db, engine, Base
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("pokemon-api")

# MySQL en Coolify tarda varios segundos en quedar listo tras un deploy; sin retry
# el create_all explotaba en import-time y el contenedor entraba en crash loop.
INTENTOS_BD_ARRANQUE = 5
ESPERA_ENTRE_INTENTOS_SEG = 3


def _crear_tablas_con_reintentos() -> None:
    ultimo_error: OperationalError | None = None
    for intento in range(1, INTENTOS_BD_ARRANQUE + 1):
        try:
            Base.metadata.create_all(bind=engine)
            return
        except OperationalError as err:
            ultimo_error = err
            logger.warning(
                "BD no lista (intento %s/%s), reintentando en %ss...",
                intento, INTENTOS_BD_ARRANQUE, ESPERA_ENTRE_INTENTOS_SEG,
            )
            time.sleep(ESPERA_ENTRE_INTENTOS_SEG)
    raise RuntimeError("MySQL no respondió durante el arranque") from ultimo_error


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # create_all es bloqueante (engine sync); lo mandamos a un hilo para no congelar el loop
    await asyncio.to_thread(_crear_tablas_con_reintentos)
    yield


app = FastAPI(lifespan=lifespan)

# Obtener los orígenes permitidos desde variable de entorno
allowed_origins = [
    o.strip()
    for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:4200").split(",")
    if o.strip()
]

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

@app.get("/health", responses={503: {"description": "Base de datos no disponible"}})
def health_check(db: Annotated[Session, Depends(get_db)]):
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        # El detalle va al log, no al cliente: str(e) puede exponer host interno y credenciales
        logger.exception("Health check: fallo la conexion a la base de datos")
        raise HTTPException(status_code=503, detail="Base de datos no disponible")
    return {
        "status": "healthy",
        "database": "connected",
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "development")
    }

# Para desarrollo local
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 3000))
    uvicorn.run(app, host="0.0.0.0", port=port)