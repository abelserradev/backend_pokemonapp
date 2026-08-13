#!/bin/bash

# Fallar si hay un error (buena práctica en Docker)
set -e

PORT=${PORT:-3000}

echo "🚀 Starting API on port: $PORT"
echo "🌐 ENVIRONMENT: ${ENVIRONMENT:-production}"

if [ -n "${DATABASE_URL:-}" ]; then
  echo "🗄️ DATABASE_URL: (set)"
else
  echo "⚠️ DATABASE_URL not set"
fi

# Usamos exec para que Uvicorn tome el control del proceso (PID 1)
# Añadimos --proxy-headers para Cloudflare/Traefik
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --proxy-headers
