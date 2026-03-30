#!/bin/bash

# Obtener el puerto de Railway o usar 8000 por defecto
PORT=${PORT:-8000}

echo "🚀 Starting API on port: $PORT"
echo "🌐 ENVIRONMENT: ${ENVIRONMENT:-production}"
# No volcar credenciales: solo si hay URL de BD configurada
if [ -n "${DATABASE_URL:-}" ]; then
  echo "🗄️ DATABASE_URL: (set)"
else
  echo "⚠️ DATABASE_URL not set"
fi

# Ejecutar uvicorn con el puerto correcto
uvicorn app.main:app --host 0.0.0.0 --port $PORT