#!/bin/bash

# Obtener el puerto de Railway o usar 8000 por defecto
PORT=${PORT:-8000}

echo "Starting server on port: $PORT"

# Ejecutar uvicorn con el puerto correcto
uvicorn app.main:app --host 0.0.0.0 --port $PORT