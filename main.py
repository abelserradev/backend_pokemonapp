"""
Punto de entrada principal para Railway.
Este archivo permite a Railway detectar automáticamente la aplicación FastAPI.
"""
from app.main import app

if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

