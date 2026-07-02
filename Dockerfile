FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 1. Definimos el directorio de trabajo donde está el código
WORKDIR /app/ProyectoColegio

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    libcairo2 \
    libcairo2-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-xlib-2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# 2. Copiamos el archivo de dependencias desde tu local hacia el WORKDIR
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copiamos todo el contenido de ProyectoColegio hacia el WORKDIR actual (/app/ProyectoColegio)
COPY . .

# 4. Ajustamos permisos
RUN adduser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app
    
USER appuser

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]