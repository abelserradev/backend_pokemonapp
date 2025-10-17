#!/usr/bin/env python3
"""
Script para iniciar el servidor en modo producción.
Usa variables de entorno del sistema (Railway, etc.)
"""

import os
import subprocess
import sys

def main():
    # Establecer entorno de producción
    os.environ["ENVIRONMENT"] = "production"
    
    print("🚀 Iniciando servidor en modo PRODUCCIÓN")
    print("☁️  Usando variables de entorno del sistema")
    print("🗄️  Base de datos: MySQL (Railway)")
    print("-" * 50)
    
    try:
        # Iniciar uvicorn
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", os.getenv("PORT", "8000")
        ])
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido")

if __name__ == "__main__":
    main()
