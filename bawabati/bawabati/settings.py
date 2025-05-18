import os
from pathlib import Path
from dotenv import load_dotenv
import pymysql

# Load environment variables
pymysql.install_as_MySQLdb()
load_dotenv()

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-placeholder')
DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Strict HTTPS Configuration for Production
SECURE_SSL_REDIRECT = os.getenv('DJANGO_SECURE_SSL_REDIRECT', 'False') == 'True'
SESSION_COOKIE_SECURE = "X-CSRFToken"
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_NAME = "csrftoken"
SECURE_HSTS_SECONDS = 31536000 if SECURE_SSL_REDIRECT else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_REFERRER_POLICY = "no-referrer-when-downgrade"
X_FRAME_OPTIONS = "DENY"  # Prevent clickjacking
CONTENT_SECURITY_POLICY = "default-src 'self'; img-src 'self' data:; script-src 'self'; style-src 'self' 'unsafe-inline';"
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:8000',
]

CORS_ORIGIN_ALLOW_ALL = False

# Improved CORS Configuration
CORS_ORIGIN_WHITELIST = [
    "http://localhost:3000",
    'http://localhost:8000',
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    "Accept",
    "Accept-Encoding",
    "Authorization",
    "Content-Type",
    "DNT",
    "Origin",
    "User-Agent",
    "X-CSRFToken",
    "X-Requested-With",
]


# settings.py
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # Make sure this is above CSRF
    'django.middleware.csrf.CsrfViewMiddleware',  # CSRF Middleware must be here
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]



INSTALLED_APPS = [
    # Default Django apps
    'django.contrib.admin',        # Admin site
    'django.contrib.auth',         # Authentication
    'django.contrib.contenttypes', # Content types (required)
    'django.contrib.sessions',     # Session management
    'django.contrib.messages',     # Messaging
    'django.contrib.staticfiles',  # Static files

    # Third-party apps (like DRF and CORS)
    'rest_framework',
    'corsheaders',

    # Your local apps
    'bawabati_app',  # Replace with the name of your main app
    'students',
    'teachers',
    'courses',
    'grades',
    'crispy_forms',
    'crispy_bootstrap4',
]
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Database configuration for MySQL/MariaDB
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'bawabati_db2'),
        'USER': os.getenv('DB_USER', 'root'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'root'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'CONN_MAX_AGE': 600,  # Connection pooling for performance
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Password Validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]


# Static and Media Files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'EXCEPTION_HANDLER': 'bawabati_app.utils.custom_exception_handler',
}

# Debug Toolbar (Only for Local Development)
INTERNAL_IPS = ['127.0.0.1'] if DEBUG else []

# Secure Cookie Settings (CSRF and Session)
SESSION_COOKIE_HTTPONLY = False
CSRF_COOKIE_HTTPONLY = False  # Required for React
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
CSRF_HEADER_NAME = "HTTP_X_CSRFTOKEN"
# Secure Redirects
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'
ROOT_URLCONF = 'bawabati.urls'
CSRF_COOKIE_SAMESITE = 'lax' 
SESSION_COOKIE_SAMESITE = 'Lax'


 # Allow cross-site requests (especially for React)
