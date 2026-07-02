# Usamos una imagen base ligera
FROM python:3.11-slim

# Evita que Python genere archivos .pyc y permite ver logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Establecemos el directorio de trabajo
WORKDIR /app

# Instalamos dependencias del sistema necesarias para librerías como Cairo (para PDF/imágenes)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    libcairo2 \
    libcairo2-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Instalamos dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiamos todo el proyecto al contenedor
COPY . .

# Recolectamos los archivos estáticos (genera el manifiesto que necesita WhiteNoise)
RUN python manage.py collectstatic --noinput

# Creamos un usuario no root para mayor seguridad
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app
    
USER appuser

# Exponemos el puerto que Render asigna automáticamente
EXPOSE 10000

# Ejecutamos Gunicorn
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn --chdir /app config.wsgi:application --bind 0.0.0.0:10000"]