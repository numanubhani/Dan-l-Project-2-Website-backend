"""
Django settings for vpulse_backend project.

Works for both LOCAL and PYTHONANYWHERE:
- Local: run as-is (no env vars). Uses 127.0.0.1, localhost, DEBUG=True, SQLite, local static/media.
- PythonAnywhere: set env vars in Web → your app → Environment variables (see DEPLOY_PYTHONANYWHERE.md).
"""

from pathlib import Path
import os

def _get_env(key, default=None, cast=None):
    """Read from environment; use python-decouple if available (e.g. .env or PA env vars)."""
    try:
        from decouple import config
        return config(key, default=default, cast=cast)
    except Exception:
        val = os.environ.get(key, default)
        if cast and val is not None:
            return cast(val) if callable(cast) else val
        return val

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Admin site configuration
ADMIN_SITE_HEADER = "VPulse Admin"
ADMIN_SITE_TITLE = "VPulse Administration"
ADMIN_INDEX_TITLE = "Welcome to VPulse Admin Panel"


# ---------- Local vs PythonAnywhere (same settings file) ----------
# SECURITY: override SECRET_KEY and set DEBUG=False on PythonAnywhere.
SECRET_KEY = _get_env('SECRET_KEY', 'django-insecure-vpulse-dev-key-change-in-production-2024')
DEBUG = _get_env('DEBUG', True, lambda v: str(v).lower() in ('1', 'true', 'yes'))

# Hosts: always allow local; add production host(s) from env (e.g. yourname.pythonanywhere.com).
_ALLOWED = _get_env('ALLOWED_HOSTS', 'muhammadnumansubhan1.pythonanywhere.com')
ALLOWED_HOSTS = ['127.0.0.1', 'localhost'] + [h.strip() for h in _ALLOWED.split(',') if h.strip()]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'drf_spectacular',
    'corsheaders',
    'accounts',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'vpulse_backend.urls'

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

WSGI_APPLICATION = 'vpulse_backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static and media files (local: project dirs; PythonAnywhere: set STATIC_ROOT/MEDIA_ROOT in env)
STATIC_URL = '/static/'
STATIC_ROOT = _get_env('STATIC_ROOT', str(BASE_DIR / 'staticfiles'))

MEDIA_URL = '/media/'
MEDIA_ROOT = Path(_get_env('MEDIA_ROOT', str(BASE_DIR / 'media')))

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# drf-spectacular Settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'VPulse API',
    'DESCRIPTION': 'VPulse Video Betting and Content Platform API Documentation',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/',
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]
# Add production frontend URL(s) via env, e.g. CORS_EXTRA_ORIGINS=https://yoursite.com,https://www.yoursite.com
_extra_origins = _get_env('CORS_EXTRA_ORIGINS', '')
if _extra_origins:
    CORS_ALLOWED_ORIGINS.extend(origin.strip() for origin in _extra_origins.split(',') if origin.strip())

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_ALL_ORIGINS = DEBUG  # Allow all origins in development only

