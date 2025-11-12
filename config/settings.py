"""
Django settings for config project.
Configurado para desarrollo y producción (Render)
"""
from datetime import timedelta
from pathlib import Path
import os
import dj_database_url
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================================
# SEGURIDAD
# ==============================================================================

# ⚠️ CAMBIO 1: SECRET_KEY desde variable de entorno
# En desarrollo usa la que tienes, en producción usa una segura desde Render
SECRET_KEY = config(
    'SECRET_KEY', 
    default='django-insecure-@0$wiv#1+5j2^d47&83o=t4vxn(a3+fua(o#*htoj6=oc@q^mv'
)

# ⚠️ CAMBIO 2: DEBUG desde variable de entorno
# En desarrollo: True, en producción: False
DEBUG = config('DEBUG', default=True, cast=bool)

# ⚠️ CAMBIO 3: ALLOWED_HOSTS controlado
# En desarrollo permite todo, en producción solo dominios específicos
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS', 
    default='localhost,127.0.0.1'
).split(',')

# Agregar dominios de Render automáticamente en producción
if not DEBUG:
    ALLOWED_HOSTS += ['.onrender.com']

# ==============================================================================
# MODELO DE USUARIO PERSONALIZADO
# ==============================================================================

AUTH_USER_MODEL = 'users.CustomUser'

# ==============================================================================
# APLICACIONES
# ==============================================================================

INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Terceros
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    
    # Apps propias
    'users',
    'products',
    'orders',
    'payments',
    'reviews',
]

# ==============================================================================
# MIDDLEWARE
# ==============================================================================

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # ✅ Debe estar PRIMERO
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ⚠️ NUEVO: Para archivos estáticos
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# ==============================================================================
# TEMPLATES
# ==============================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ==============================================================================
# BASE DE DATOS
# ==============================================================================

# ⚠️ CAMBIO 4: Base de datos dinámica
# En desarrollo: tu PostgreSQL local
# En producción: PostgreSQL de Render
DATABASES = {
    'default': dj_database_url.config(
        default=config(
            'DATABASE_URL',
            default='postgresql://postgres:79815451@localhost:5432/ecommerce_db'
        ),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# ==============================================================================
# VALIDACIÓN DE CONTRASEÑAS
# ==============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ==============================================================================
# INTERNACIONALIZACIÓN
# ==============================================================================

LANGUAGE_CODE = 'es-es'  # Cambiado a español
TIME_ZONE = 'America/La_Paz'  # Zona horaria de Bolivia
USE_I18N = True
USE_TZ = True

# ==============================================================================
# ARCHIVOS ESTÁTICOS (CSS, JavaScript, Images)
# ==============================================================================

# ⚠️ CAMBIO 5: Configuración de archivos estáticos para producción
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# WhiteNoise para servir archivos estáticos en producción
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Directorios adicionales para archivos estáticos
STATICFILES_DIRS = [
    # os.path.join(BASE_DIR, 'static'),  # Descomenta si tienes carpeta static/
]

# ==============================================================================
# ARCHIVOS MEDIA (Uploads de usuarios)
# ==============================================================================

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ==============================================================================
# CORS (Cross-Origin Resource Sharing)
# ==============================================================================

# ⚠️ CAMBIO 6: CORS controlado por ambiente
if DEBUG:
    # Desarrollo: Permite todos los orígenes
    CORS_ALLOW_ALL_ORIGINS = True
else:
    # Producción: Solo dominios específicos
    CORS_ALLOWED_ORIGINS = config(
        'CORS_ALLOWED_ORIGINS',
        default='https://tu-frontend.onrender.com'
    ).split(',')

CORS_ALLOW_CREDENTIALS = True

# ==============================================================================
# REST FRAMEWORK
# ==============================================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# ==============================================================================
# SIMPLE JWT
# ==============================================================================

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# ==============================================================================
# CONFIGURACIONES DE SEGURIDAD PARA PRODUCCIÓN
# ==============================================================================

if not DEBUG:
    # ⚠️ CAMBIO 7: Configuraciones de seguridad
    SECURE_SSL_REDIRECT = True  # Redirigir HTTP a HTTPS
    SESSION_COOKIE_SECURE = True  # Cookies solo por HTTPS
    CSRF_COOKIE_SECURE = True  # CSRF cookies solo por HTTPS
    SECURE_BROWSER_XSS_FILTER = True  # Protección XSS
    SECURE_CONTENT_TYPE_NOSNIFF = True  # Prevenir sniffing de tipo MIME
    SECURE_HSTS_SECONDS = 31536000  # HTTP Strict Transport Security (1 año)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    X_FRAME_OPTIONS = 'DENY'  # Prevenir clickjacking

# ==============================================================================
# LOGGING (Para debugging en producción)
# ==============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ==============================================================================
# DEFAULT PRIMARY KEY
# ==============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'