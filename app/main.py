from fastapi import FastAPI
from app.routes import auth
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # URL del frontend Angular
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router, prefix="/api")


@app.get("/")
def home():
    return{"message": "¡Bienvenido al backend de Pokemon"}