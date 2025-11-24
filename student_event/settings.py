# student_event/settings.py
from pathlib import Path
import os
from urllib.parse import urlparse

# ---------------------------------------------------------------------
# Project base
# ---------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------
LOGIN_URL = 'loginindex'
LOGIN_REDIRECT_URL = 'studentdashboard'
AUTH_USER_MODEL = 'main.User'

# ---------------------------------------------------------------------
# Security / Debug
# ---------------------------------------------------------------------
SECRET_KEY = 'django-insecure-c02l$+ss##*v!1r8tvy93yv4$va0ht6%tx*9n@rkw7$-&rkh0j'
DEBUG = True  # keep True for dev; set False in production

# If you’re using a tunnel (Cloudflare/ngrok), put its full origin here, e.g.:
#   PUBLIC_ORIGIN=https://abc123.trycloudflare.com
PUBLIC_ORIGIN = os.environ.get("PUBLIC_ORIGIN", "").strip()


def _origin_to_host(origin: str) -> str:
    try:
        return urlparse(origin).hostname or ""
    except Exception:
        return ""


_public_host = _origin_to_host(PUBLIC_ORIGIN)

# Allow localhost, 127.0.0.1, and your tunnel host (if provided)
ALLOWED_HOSTS = list(filter(None, [
    "localhost",
    "127.0.0.1",
    _public_host,
]))

# Behind tunnels/reverse proxies, these help Django build correct absolute URLs
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ---------------------------------------------------------------------
# Installed apps / middleware
# ---------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main',
    'rest_framework',
    'corsheaders',
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

ROOT_URLCONF = 'student_event.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # using app templates (APP_DIRS=True)
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

WSGI_APPLICATION = 'student_event.wsgi.application'

# ---------------------------------------------------------------------
# CORS / CSRF for public phone access
# ---------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True  # dev convenience

CSRF_TRUSTED_ORIGINS = list(filter(None, [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://localhost:8000',
    'https://127.0.0.1:8000',
    PUBLIC_ORIGIN if PUBLIC_ORIGIN else None,
]))

# ---------------------------------------------------------------------
# Database (MySQL locally/prod, SQLite in CI)
# ---------------------------------------------------------------------
USE_SQLITE_FOR_CI = os.environ.get("GITHUB_ACTIONS") == "true" or os.environ.get("USE_SQLITE_FOR_CI") == "1"

if USE_SQLITE_FOR_CI:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "ci.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.environ.get("MYSQL_DATABASE", "student_event"),
            "USER": os.environ.get("MYSQL_USER", "campus_event"),
            "PASSWORD": os.environ.get("MYSQL_PASSWORD", "campus_event"),
            "HOST": os.environ.get("MYSQL_HOST", "localhost"),
            "PORT": os.environ.get("MYSQL_PORT", "3306"),
            "OPTIONS": {"init_command": "SET sql_mode='STRICT_TRANS_TABLES'"},
            "TEST": {
                "NAME": "test_student_event",
            },
        }
    }

# ---------------------------------------------------------------------
# I18N / TZ
# ---------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'main', 'static'),
]

# ---------------------------------------------------------------------
# Default PK
# ---------------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------------------------------------------------------------------
# Stripe test keys (mock API payments)
# ---------------------------------------------------------------------
# For a real project you’d move these to environment variables, but for
# your course project we keep defaults so it “just works” after paste.
STRIPE_PUBLISHABLE_KEY = os.environ.get(
    "STRIPE_PUBLISHABLE_KEY",
    "pk_test_51SVP6qDlKRJfGzqmYmRMyJcL50LDcEUbDnMSB50w3T1NUeVfYOkrxfRoRCUf1QnBFc3VoviUgBfb4Rrcp5cBl20H00x8eUVB6O",
)

STRIPE_SECRET_KEY = os.environ.get(
    "STRIPE_SECRET_KEY",
    "sk_test_51SVP6qDlKRJfGzqm9p9C2Ww89AWbaWjsRtzPdotvqTBHmNF4BCzEBRnY8ctl2O2ghvZi4vXvJxHPcJg1QYC6LDLd00UC0wxPN6",
)
