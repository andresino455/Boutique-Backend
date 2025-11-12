#!/usr/bin/env bash
# exit on error
set -o errexit

echo "📦 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

echo "📚 Configurando NLTK..."
python nltk_setup.py

echo "📁 Recolectando archivos estáticos..."
python manage.py collectstatic --no-input

echo "🗄️ Ejecutando migraciones..."
python manage.py migrate

echo "👤 Creando superusuario..."
python create_superuser.py

echo "✅ Build completado!"