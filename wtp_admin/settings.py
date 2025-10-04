import os
from pathlib import Path

# NOTA: Asegúrate de que python-dotenv y load_dotenv() se ejecutan en manage.py 
# para que estas variables se carguen antes de leer settings.py.

# RUTA BASE
BASE_DIR = Path(__file__).resolve().parent.parent

# =========================================================
# SEGURIDAD Y ENTORNO (Leído desde .env)
# =========================================================

# 1. SECRET_KEY: Lee la variable 'SECRET_KEY' del entorno (del .env)
SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-unsafe-secret-key") # Usar un fallback seguro, aunque ya tienes la tuya

# 2. DEBUG: Lee la variable 'DEBUG' y la convierte a booleano.
# Usa 'False' como valor predeterminado si no se encuentra.
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

# 3. ALLOWED_HOSTS: Lee la variable 'ALLOWED_HOSTS' y la divide por comas.
# Si la variable no existe, usa la lista de fallback (desarrollo local).
ALLOWED_HOSTS_ENV = os.environ.get("ALLOWED_HOSTS")

if ALLOWED_HOSTS_ENV:
    ALLOWED_HOSTS = ALLOWED_HOSTS_ENV.split(',')
else:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# =========================================================
# CONFIGURACIÓN DE APLICACIONES Y MIDDLEWARE (Sin cambios)
# =========================================================

INSTALLED_APPS = [
    'jazzmin', 
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',  
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'wtp_admin.urls'

# TEMPLATES (Sin cambios)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'core' / 'templates' / 'core'], 
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

# WSGI
WSGI_APPLICATION = 'wtp_admin.wsgi.application'

# =========================================================
# BASE DE DATOS (Lectura dinámica desde .env)
# =========================================================

# Leer las variables de DB del entorno
DB_ENGINE = os.environ.get('DB_ENGINE')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')

# Si DEBUG=True o no se encuentra el HOST de la base de datos, usa SQLite (fallback local)
if DEBUG or not DB_HOST:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
# Si DEBUG=False y se encuentran las variables de DB, usa PostgreSQL (producción/Clever Cloud)
else:
    DATABASES = {
        'default': {
            'ENGINE': DB_ENGINE, # Leído del .env
            'NAME': DB_NAME,     # Leído del .env
            'USER': DB_USER,     # Leído del .env
            'PASSWORD': DB_PASSWORD, # Leído del .env
            'HOST': DB_HOST,     # Leído del .env
            'PORT': DB_PORT,     # Leído del .env
            'OPTIONS': {
                'sslmode': 'require',
            }
        }
    }
# -------------------------------------------------------------------------

# USUARIO PERSONALIZADO (Sin cambios)
AUTH_USER_MODEL = 'core.User'

# VALIDADORES DE CONTRASEÑA (Sin cambios)
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# LOCALIZACIÓN (Sin cambios)
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Caracas'
USE_I18N = True
USE_TZ = True

# ARCHIVOS ESTÁTICOS (Sin cambios)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'core' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# DEFAULT AUTO FIELD (Sin cambios)
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuración Opcional de Jazzmin (Sin cambios)
JAZZMIN_SETTINGS = {
    "site_title": "WTP - Admin System",
    "site_header": "WTP Admin",
    "site_brand": "WTP Admin",
    "copyright": "WTP Corp.",
}