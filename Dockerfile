FROM python:3.12-alpine

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LOG_FILE_PATH=/app/logs/access.log

# Installation des dépendances système
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev python3-dev

# Création du répertoire de logs avec les bonnes permissions
RUN mkdir -p /app/logs && \
    chmod 777 /app/logs

WORKDIR /app

# Définition du volume pour les logs
VOLUME ["/app/logs"]

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

EXPOSE 8000

# Création du fichier de log vide avec les bonnes permissions
RUN touch /app/logs/access.log && \
    chmod 666 /app/logs/access.log

CMD ["python", "src/main.py"]