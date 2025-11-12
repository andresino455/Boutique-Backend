#!/usr/bin/env python
"""
Script para crear superusuario automáticamente en producción
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from decouple import config

User = get_user_model()

def create_superuser():
    """
    Crea un superusuario si no existe
    """
    # Obtener credenciales desde variables de entorno
    username = config('DJANGO_SUPERUSER_USERNAME', default='admin')
    email = config('DJANGO_SUPERUSER_EMAIL', default='admin@example.com')
    password = config('DJANGO_SUPERUSER_PASSWORD', default='admin123456')
    
    # Verificar si el usuario ya existe
    if User.objects.filter(username=username).exists():
        print(f"✓ El superusuario '{username}' ya existe")
        return
    
    try:
        # Crear superusuario
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            role='admin',  # Tu campo personalizado
            is_staff=True,
            is_active=True
        )
        print(f"✅ Superusuario '{username}' creado exitosamente")
        print(f"   Email: {email}")
        print(f"   ⚠️  Recuerda cambiar la contraseña después del primer login")
        
    except Exception as e:
        print(f"❌ Error al crear superusuario: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    create_superuser()