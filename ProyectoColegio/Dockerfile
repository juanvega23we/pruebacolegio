FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 1. Ya estamos en el Root Directory (ProyectoColegio), así que el WORKDIR es simplemente /app
WORKDIR /app

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

# 2. Como requirements.txt ahora está en la misma carpeta que el Dockerfile, se copia directo
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copiamos todo el contenido de la carpeta actual al WORKDIR (/app)
COPY . .

# 4. Permisos
RUN adduser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app
    
USER appuser

# 5. Render usa puertos distintos internamente. 
# Si usas Gunicorn (que es lo ideal en producción), el puerto suele ser 10000.
EXPOSE 10000
ENV PYTHONPATH=/app:$PYTHONPATH
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:10000"]