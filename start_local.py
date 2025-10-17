#!/usr/bin/env python3
"""
Script para iniciar el servidor en modo desarrollo local.
Usa automáticamente .env.local
"""

import os
import subprocess
import sys

def main():
    # Establecer entorno de desarrollo
    os.environ["ENVIRONMENT"] = "development"
    
    print("🚀 Iniciando servidor en modo DESARROLLO LOCAL")
    print("📁 Usando archivo: .env.local")
    print("🗄️  Base de datos: SQLite local")
    print("🌐 URL: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("-" * 50)
    
    try:
        # Iniciar uvicorn
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido")

if __name__ == "__main__":
    main()
