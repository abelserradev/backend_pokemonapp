# Usar imagen oficial de Python
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# database.py usa esto para no cargar .env.local dentro del contenedor
ENV DOCKER_CONTAINER=1
ENV ENVIRONMENT=production

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar todo el código de la aplicación
COPY . .

# Hacer el script ejecutable
RUN chmod +x start.sh

# Puerto por defecto; en runtime PORT viene de env (Coolify, compose, etc.)
EXPOSE 8000

CMD ["./start.sh"]