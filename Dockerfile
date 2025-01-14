FROM python:3.12-alpine

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ACCESS_LOG_PATH=/logs/access.log \
    ERROR_LOG_PATH=/logs/error.log

# Installation des dépendances système
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev python3-dev

# Create Apache logs directory
RUN mkdir -p /var/log/apache2 && \
    chmod 755 /var/log/apache2

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

EXPOSE 8000

CMD ["python", "src/main.py"]