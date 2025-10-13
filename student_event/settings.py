"""
Django settings for student_event project.
"""

from pathlib import Path
import os

# ---------- Basic project paths ----------
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------- Auth redirects ----------
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'student_dashboard'

# ---------- Security / Debug ----------
SECRET_KEY = 'django-insecure-c02l$+ss##*v!1r8tvy93yv4$va0ht6%tx*9n@rkw7$-&rkh0j'
DEBUG = True
ALLOWED_HOSTS: list[str] = []

# ---------- Installed apps ----------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',   # DRF
    'main',             # your app
]

# ---------- CSRF (local dev) ----------
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# ---------- Middleware ----------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'student_event.urls'
WSGI_APPLICATION = 'student_event.wsgi.application'

# ---------- Templates ----------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # App templates are used (main/templates)
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ---------- Database (SQLite for dev) ----------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ---------- i18n ----------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ---------- Static files ----------
# Collected static
STATIC_URL = 'static/'
# App/static for development (your CSS/JS inside main/static)
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'main', 'static'),
]

# ---------- Media (uploaded files e.g., QR images) ----------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ---------- Primary key & custom user ----------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'main.User'
