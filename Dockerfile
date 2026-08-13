# Usar imagen oficial de Python
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# database.py usa esto para no cargar .env.local dentro del contenedor
ENV DOCKER_CONTAINER=1
ENV ENVIRONMENT=production

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias (como root; la app corre como usuario no privilegiado)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Usuario dedicado: reduce superficie si el contenedor es comprometido
RUN addgroup --system app && adduser --system --ingroup app --home /app app

# Copiar todo el código de la aplicación
COPY . .

RUN chmod +x start.sh && chown -R app:app /app

# Uvicorn usa PORT del entorno (Coolify suele 3000)
EXPOSE 3000

USER app

CMD ["./start.sh"]
