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

# Uvicorn usa PORT del entorno (Coolify suele 3000)
EXPOSE 3000

CMD ["./start.sh"]