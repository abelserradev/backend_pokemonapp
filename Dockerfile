# Usar imagen oficial de Python
FROM python:3.11-slim

WORKDIR /app

# database.py usa esto para no cargar .env.local dentro del contenedor
ENV DOCKER_CONTAINER=1 \
    ENVIRONMENT=production

# Usuario dedicado antes del COPY final (--chown evita RUN chown -R)
RUN addgroup --system app && adduser --system --ingroup app --home /app app

COPY requirements.txt .

# pip con versión fija: Hadolint DL3013 exige pin en cada pip install
RUN pip install --no-cache-dir "pip==25.0.1" && \
    pip install --no-cache-dir -r requirements.txt

COPY --chown=app:app . .

RUN chmod +x start.sh

EXPOSE 3000

USER app

CMD ["./start.sh"]
