#!/usr/bin/env bash
# Salir en caso de error
set -o errexit

# Instalar dependencias del sistema
apt-get update
apt-get install -y libcairo2-dev pkg-config python3-dev

# Instalar dependencias de Python
pip install -r ProyectoColegio/requirements.txt