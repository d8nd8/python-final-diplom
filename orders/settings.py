import os
from pathlib import Path
from dotenv import load_dotenv
from django.templatetags.static import static
import sys

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

DB_ENGINE = os.getenv("DB_ENGINE", "django.db.backends.sqlite3")
DB_NAME = os.getenv("DB_NAME", "db.sqlite3")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "")
DB_PORT = os.getenv("DB_PORT", "")
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-test-key-for-testing")
DEBUG = os.getenv("DEBUG", "False") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0").split(",")

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.import_export",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "drf_spectacular",
    "django_filters",
    "rest_framework",
    "import_export",
    "social_django",
    "backend",
]

AUTH_USER_MODEL = "backend.User"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "orders.urls"

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "orders.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": DB_ENGINE,
        "NAME": DB_NAME,
        "USER": DB_USER,
        "PASSWORD": DB_PASSWORD,
        "HOST": DB_HOST,
        "PORT": DB_PORT,
    }
}

# Test database configuration
if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


TIME_ZONE = "Europe/Moscow"
USE_TZ = True
USE_I18N = True
LOCALE_PATHS = [os.path.join(BASE_DIR, "locale")]
LANGUAGE_CODE = "ru"
USE_L10N = False
DATE_INPUT_FORMATS = ["%d.%m.%Y"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "user": "100/hour",
        "anon": "10/minute",
    },
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
    ],
}


SPECTACULAR_SETTINGS = {
    "TITLE": "Netology shop API",
    "DESCRIPTION": "Документация API для дипломной работы",
    "VERSION": "0.0.1",
    "SECURITY_SCHEMES": {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Введите JWT токен как: Bearer <token>",
        }
    },
    "SECURITY": [
        {"bearerAuth": []},
    ],
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_SETTINGS": {"filter": True, "displayRequestDuration": True},
    "COMPONENT_SPLIT_REQUEST": True,
}

UNFOLD = {
    "SITE_URL": "/",
    "SITE_HEADER": "Админ-панель",
    "SITE_SYMBOL": "shopping_cart",
    "STYLES": [
        lambda request: static("css/styles.css"),
    ],
    "SCRIPTS": [
        lambda request: static("js/scripts.js"),
    ],
    "BORDER_RADIUS": "10px",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Пользователи",
                "items": [
                    {
                        "title": "Пользователи",
                        "icon": "person",
                        "link": lambda request: "/admin/backend/user/",
                    },
                    {
                        "title": "Контакты",
                        "icon": "contact_mail",
                        "link": lambda request: "/admin/backend/contact/",
                    },
                ]
            },
            {
                "title": "Магазины",
                "items": [
                    {
                        "title": "Магазины",
                        "icon": "store",
                        "link": lambda request: "/admin/backend/shop/",
                    },
                    {
                        "title": "Категории",
                        "icon": "category",
                        "link": lambda request: "/admin/backend/category/",
                    },
                ]
            },
            {
                "title": "Товары",
                "items": [
                    {
                        "title": "Товары",
                        "icon": "inventory",
                        "link": lambda request: "/admin/backend/product/",
                    },
                    {
                        "title": "Информация о товарах",
                        "icon": "info",
                        "link": lambda request: "/admin/backend/productinfo/",
                    },
                    {
                        "title": "Параметры",
                        "icon": "settings",
                        "link": lambda request: "/admin/backend/parameter/",
                    },
                    {
                        "title": "Параметры товаров",
                        "icon": "tune",
                        "link": lambda request: "/admin/backend/productparameter/",
                    },
                ]
            },
            {
                "title": "Заказы",
                "items": [
                    {
                        "title": "Заказы",
                        "icon": "shopping_cart",
                        "link": lambda request: "/admin/backend/order/",
                    },
                    {
                        "title": "Элементы заказов",
                        "icon": "list",
                        "link": lambda request: "/admin/backend/orderitem/",
                    },
                ]
            },
            {
                "title": "Корзина",
                "items": [
                    {
                        "title": "Корзины",
                        "icon": "shopping_basket",
                        "link": lambda request: "/admin/backend/cart/",
                    },
                    {
                        "title": "Элементы корзин",
                        "icon": "list",
                        "link": lambda request: "/admin/backend/cartitem/",
                    },
                ]
            },
            {
                "title": "Токены",
                "items": [
                    {
                        "title": "Токены подтверждения",
                        "icon": "key",
                        "link": lambda request: "/admin/backend/emailconfirmtoken/",
                    },
                ]
            },
        ],
    },
    "COLORS": {
        "primary": {
            "50": "248 250 245",
            "100": "240 245 235",
            "200": "225 235 215",
            "300": "200 220 185",
            "400": "175 205 155",
            "500": "150 190 125",
            "600": "125 175 105",
            "700": "100 160 85",
            "800": "75 145 65",
            "900": "50 130 45",
            "950": "35 115 35",
        },
        "base": {
            "50": "251 251 248",
            "100": "241 241 236",
            "200": "225 226 220",
            "300": "205 206 199",
            "400": "174 175 168",
            "500": "143 144 137",
            "600": "113 114 107",
            "700": "89 90 84",
            "800": "54 55 50",
            "900": "31 32 38",
            "950": "30 31 28",
        },
    },
}

# Social Authentication Settings
AUTHENTICATION_BACKENDS = (
    'social_core.backends.github.GithubOAuth2',
    'social_core.backends.vk.VKOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

# Social Auth URLs
LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/admin/'
LOGOUT_URL = '/admin/logout/'
LOGOUT_REDIRECT_URL = '/admin/login/'

# Social Auth Pipeline
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

# Social Auth Settings
SOCIAL_AUTH_RAISE_EXCEPTIONS = False
SOCIAL_AUTH_LOGIN_ERROR_URL = '/admin/login/'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/admin/'
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/admin/'
SOCIAL_AUTH_DISCONNECT_REDIRECT_URL = '/admin/'

# GitHub OAuth2
SOCIAL_AUTH_GITHUB_KEY = os.getenv('GITHUB_OAUTH2_KEY', '')
SOCIAL_AUTH_GITHUB_SECRET = os.getenv('GITHUB_OAUTH2_SECRET', '')

# VK OAuth2
SOCIAL_AUTH_VK_OAUTH2_KEY = os.getenv('VK_OAUTH2_KEY', '')
SOCIAL_AUTH_VK_OAUTH2_SECRET = os.getenv('VK_OAUTH2_SECRET', '')

# User model fields
SOCIAL_AUTH_USER_MODEL = 'backend.User'
SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ['username', 'first_name', 'email']

# Admin logout redirect
ADMIN_LOGOUT_REDIRECT_URL = '/admin/login/'

# Django admin settings
ADMIN_SITE_HEADER = "Netology Shop Admin"
ADMIN_SITE_TITLE = "Netology Shop Admin Portal"
ADMIN_INDEX_TITLE = "Welcome to Netology Shop Admin Portal"

# Django logout settings
LOGOUT_REDIRECT_URL = '/admin/login/'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Celery settings
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 минут
