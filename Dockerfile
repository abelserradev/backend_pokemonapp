# Usar imagen oficial de Python
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar todo el código de la aplicación
COPY . .

# Hacer el script ejecutable
RUN chmod +x start.sh

# Exponer el puerto (Railway lo asigna dinámicamente)
EXPOSE $PORT

# Comando de inicio usando el script
CMD ["./start.sh"]