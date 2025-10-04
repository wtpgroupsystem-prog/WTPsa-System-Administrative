#!/usr/bin/env bash
# Este script está optimizado para entornos de producción como Render/Clever Cloud.
# Ejecuta las tareas necesarias para preparar la aplicación Django antes de iniciar el servidor.

# 1. Instalar dependencias
echo "Instalando dependencias de Python..."
# Se asume que tienes un requirements.txt en la raíz
pip install -r requirements.txt

# 2. Recolectar archivos estáticos
# Esta etapa es crucial para Whitenoise.
echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

# 3. Ejecutar migraciones
# Asegura que la estructura de la base de datos esté actualizada.
echo "Ejecutando migraciones de la base de datos..."
python manage.py migrate