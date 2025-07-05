# settings.py - Minimal Headless Configuration for Django Oscar 4.0
import os
from pathlib import Path
from datetime import timedelta


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-your-secret-key-here-change-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

# Application definition - Minimal for headless
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.flatpages',

    # Oscar Core Apps (Minimal for headless backend)
    'oscar.config.Shop',
    'oscar.apps.catalogue.apps.CatalogueConfig',
    'oscar.apps.partner.apps.PartnerConfig',
    'oscar.apps.basket.apps.BasketConfig',
    'oscar.apps.payment.apps.PaymentConfig',
    'oscar.apps.order.apps.OrderConfig',
    'oscar.apps.customer.apps.CustomerConfig',
    'oscar.apps.address.apps.AddressConfig',
    'oscar.apps.shipping.apps.ShippingConfig',
    'oscar.apps.checkout.apps.CheckoutConfig',
    'oscar.apps.search.apps.SearchConfig',
    'oscar.apps.voucher.apps.VoucherConfig',
    'oscar.apps.offer.apps.OfferConfig',
    'oscar.apps.wishlists.apps.WishlistsConfig',
    'oscar.apps.analytics.apps.AnalyticsConfig',
    'oscar.apps.communication.apps.CommunicationConfig',
    'oscar.apps.catalogue.reviews.apps.CatalogueReviewsConfig',    
    # Admin dashboard (minimal - only if you need admin interface)
    'oscar.apps.dashboard.apps.DashboardConfig',
    'oscar.apps.dashboard.catalogue.apps.CatalogueDashboardConfig',
    'oscar.apps.dashboard.reports.apps.ReportsDashboardConfig',
    'oscar.apps.dashboard.orders.apps.OrdersDashboardConfig',
    'oscar.apps.dashboard.users.apps.UsersDashboardConfig',
    'oscar.apps.dashboard.pages.apps.PagesDashboardConfig',
    'oscar.apps.dashboard.vouchers.apps.VouchersDashboardConfig',
    'oscar.apps.dashboard.offers.apps.OffersDashboardConfig',
    'oscar.apps.dashboard.communications.apps.CommunicationsDashboardConfig',
    'oscar.apps.dashboard.shipping.apps.ShippingDashboardConfig',
    'oscar.apps.dashboard.partners.apps.PartnersDashboardConfig',
    'oscar.apps.dashboard.ranges.apps.RangesDashboardConfig',
    'oscar.apps.dashboard.reviews.apps.ReviewsDashboardConfig',



    # 'oscar.apps.dashboard.analytics.apps.AnalyticsDashboardConfig',

    

    
    # Third-party apps required by Oscar
    'widget_tweaks',
    'haystack',
    'treebeard',
    'sorl.thumbnail',
    
    # API & GraphQL
    'rest_framework',
    'rest_framework_simplejwt',
    'graphene_django',
    'corsheaders',
    'django_filters',
    'channels',  # For real-time features
    
    # Custom apps
    'api',
    'booking',
    'payments',
]
#STRIPE
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "sk_test_51KabcXYZ...")
ASGI_APPLICATION = 'backend.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
# Oscar settings
OSCAR_SLUG_MAP = {
    'catalogue.Product': 'name',  # ✅ Đúng
    'catalogue.Category': 'name',
}
OSCAR_SLUG_FUNCTION = 'oscar.core.utils.default_slugifier'
OSCAR_SLUG_BLACKLIST = ['create', 'update', 'delete', 'list', 'detail', 'search']
OSCAR_SLUG_MAX_LENGTH = 255  # Tối đa 255 ký tự


OSCAR_DELETE_IMAGE_FILES = True  # Xóa file ảnh khi xóa product/category
OSCAR_SLUG_ALLOW_UNICODE = True  # Hỗ trợ slug tiếng Việt
OSCAR_REQUIRED_ADDRESS_FIELDS = ['first_name', 'last_name', 'line1', 'line4', 'country']
OSCAR_PRODUCTS_PER_PAGE = 20
OSCAR_RECENTLY_VIEWED_PRODUCTS = 10
OSCAR_OFFERS_PER_PAGE = 20
OSCAR_DYNAMIC_CLASS_LOADER = 'oscar.core.loading.default_class_loader'
# Ghi nhớ sản phẩm đã xem gần đây
OSCAR_RECENTLY_VIEWED_PRODUCTS = 10  # số sản phẩm tối đa
OSCAR_RECENTLY_VIEWED_COOKIE_NAME = 'oscar_recently_viewed_products'
OSCAR_RECENTLY_VIEWED_COOKIE_LIFETIME = 604800  # 7 ngày = 7*24*60*60 giây
OSCAR_RECENTLY_VIEWED_COOKIE_SECURE = False  # True nếu dùng HTTPS
OSCAR_ACCOUNTS_REDIRECT_URL = 'customer:summary'
OSCAR_ACCOUNTS_LOGIN_REDIRECT_URL = 'customer:summary'
OSCAR_ACCOUNTS_LOGOUT_REDIRECT_URL = 'customer:login'
OSCAR_ACCOUNTS_LOGIN_URL = 'customer:login'
OSCAR_ACCOUNTS_LOGOUT_URL = 'customer:logout'
OSCAR_ACCOUNTS_REGISTER_URL = 'customer:register'
OSCAR_ACCOUNTS_PASSWORD_RESET_URL = 'customer:password_reset'
OSCAR_ACCOUNTS_PASSWORD_CHANGE_URL = 'customer:password_change'
OSCAR_ACCOUNTS_PROFILE_URL = 'customer:profile'
OSCAR_ACCOUNTS_PROFILE_EDIT_URL = 'customer:profile_edit'
OSCAR_EAGER_ALERTS = True  # hoặc True nếu bạn muốn alert ngay lập tức
OSCAR_HOMEPAGE = 'catalogue:index'

OSCAR_EMAILS_PER_PAGE = 20  # hoặc số phù hợp với bạn, ví dụ 10, 30
OSCAR_ORDERS_PER_PAGE = 20  # hoặc giá trị bạn muốn, ví dụ 10, 25, 50
OSCAR_ADDRESSES_PER_PAGE = 20  # hoặc số lượng khác tùy ý
OSCAR_NOTIFICATIONS_PER_PAGE = 20  # hoặc số bạn muốn, ví dụ 10, 25, 50
OSCAR_REVIEWS_PER_PAGE = 20  # hoặc số bạn muốn, ví dụ 10, 30
OSCAR_DASHBOARD_ITEMS_PER_PAGE = 20  # hoặc số bạn muốn
OSCAR_STOCK_ALERTS_PER_PAGE = 20

OSCAR_SHOP_TAGLINE = "Hệ thống bán hàng và dịch vụ điện lạnh của bạn"



OSCAR_SEARCH_FACETS = {
    'fields': {
        'product_class': {
            'name': 'Loại sản phẩm',
            'field': 'product_class',
        },
        'rating': {
            'name': 'Đánh giá',
            'field': 'rating',
        },
        'category': {
            'name': 'Danh mục',
            'field': 'category',
        },
    },
    'queries': {
        'price_range': {
            'name': 'Khoảng giá',
            'field': 'price',
            'queries': [
                ('0–500K', '[0 TO 500000]'),
                ('500K–1 triệu', '[500000 TO 1000000]'),
                ('1–2 triệu', '[1000000 TO 2000000]'),
                ('2 triệu trở lên', '[2000000 TO *]'),
            ]
        },
    },
}



MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'oscar.apps.basket.middleware.BasketMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'oscar.apps.search.context_processors.search_form',
                'oscar.apps.checkout.context_processors.checkout',
                'oscar.core.context_processors.metadata',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'webdienlanh',
        'USER': 'vandai94vn',
        'PASSWORD': 'kakanhatoi',  # Ghi đúng mật khẩu
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# Password validation
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
LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS Configuration for headless
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "https://yourdomain.com",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = DEBUG

CORS_ALLOWED_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
        'rest_framework.filters.SearchFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

# GraphQL Configuration
# settings.py
GRAPHENE = {
    'SCHEMA': 'api.schema.schema',  # Path to your GraphQL schema
    'MIDDLEWARE': [
        'graphql_jwt.middleware.JSONWebTokenMiddleware',
    ],
}

# File upload settings
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Max file size (10MB)
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# Oscar Configuration
OSCAR_SHOP_NAME = 'My Headless Shop'
OSCAR_DEFAULT_CURRENCY = 'VND'
OSCAR_FROM_EMAIL = 'noreply@myshop.com'
OSCAR_ALLOW_ANON_CHECKOUT = True

# Haystack Configuration (simple backend for development)
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}

# Thumbnail settings
THUMBNAIL_FORMAT = 'JPEG'
THUMBNAIL_KEY_PREFIX = 'thumbnail'

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# VNPAY Configuration
VNPAY_CONFIG = {
    'TMN_CODE': os.getenv('VNPAY_TMN_CODE', 'your_tmn_code'),
    'SECRET_KEY': os.getenv('VNPAY_SECRET_KEY', 'your_secret_key'),
    'PAYMENT_URL': os.getenv('VNPAY_PAYMENT_URL', 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html'),
    'RETURN_URL': os.getenv('VNPAY_RETURN_URL', 'http://localhost:3000/payment/return'),
    'VERSION': '2.1.0',
}

# Authentication Backends
AUTHENTICATION_BACKENDS = [
    'oscar.apps.customer.auth_backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Email Configuration (console for development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Site ID
SITE_ID = 1

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO',
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

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Production settings
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    SECRET_KEY = os.getenv('SECRET_KEY', SECRET_KEY)
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')