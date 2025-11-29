#!/bin/bash

# Script de inicialización para Render
# Ejecuta migraciones y poblamiento de datos iniciales

set -e

echo "=== Inicializando aplicación Django ==="

# 1. Ejecutar migraciones
echo "[1/3] Ejecutando migraciones..."
python manage.py migrate --noinput

# 2. Poblar datos iniciales (herramientas, admin, etc.)
echo "[2/3] Poblando datos iniciales..."
python manage.py populate_initial_data || true

# 3. Recolectar archivos estáticos
echo "[3/3] Recolectando archivos estáticos..."
python manage.py collectstatic --noinput || true

echo "=== ✅ Inicialización completada ==="
echo ""
echo "Iniciando servidor gunicorn..."

# Ejecutar gunicorn
exec gunicorn identificador_web.wsgi:application --bind 0.0.0.0:8000
