# Django settings for translate project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

TOKEN_TIMEOUT_DAYS = 3650
SESSION_COOKIE_AGE = 60*60*24*3650

#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = 'admin@pujia8.com'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.mxhichina.com'
EMAIL_HOST_USER = 'admin@pujia8.com'
EMAIL_HOST_PASSWORD = 'SEZsqDxUDpkr31tEuQkzeFILgEOaBa'
EMAIL_PORT = 25

REDACTOR_OPTIONS = {'lang': 'zh_cn', 'cleanup': 'true', 'path': '/static/redactor/'}
REDACTOR_UPLOAD = 'uploads/'


AUTH_PROFILE_MODULE = 'account.Profile'

ALLOWED_HOSTS = '*'

#CACHE_BACKEND = 'file://D:/Django/pujiahh/cache'

# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#         'LOCATION': '127.0.0.1:11211',
#     }
# }

ADMINS = (
    ('Pluto', 'plutokamin@gmail.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'translate.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Shanghai'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'zh-CN'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = './static/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/static/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = './static/'

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)


# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'h5w5n-m9u2^^5j0$vj80@x%2p&jrn68sw%=6z5z!hcvosc#_l-'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "django.contrib.auth.context_processors.auth",
)

ROOT_URLCONF = 'urls'

import os
TEMPLATE_DIRS = (
    os.path.dirname(__file__) + '/templates',
)

LOCALE_PATHS = (
    os.path.dirname(__file__) + '/locale',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'tokenapi.backends.TokenBackend',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.comments',
    'django.contrib.admin',
    'django.contrib.flatpages',
    'django.contrib.sitemaps',
    'tokenapi',
    'south',
    'tagging',
    'easy_thumbnails',
    'account',
    'pagination',
    'request',
    'articles',
    'redactor',
    'games',
    'link',
    'gravatar',
    'forum',
    'checkin',
    'wish',
    'weixin',
    'gallery',
    'gallery_app',
    'pujia_comments',
    'tail',
    'api',
    'webgames',
    'gifts',
    'adm',
    'payment',
    'emoji',
    'flow',
)


AUTO_GENERATE_AVATAR_SIZES = (48, )

ROOT_URL = '/'
LOGIN_REDIRECT_URL = ROOT_URL
LOGIN_URL = "%saccount/login/" % ROOT_URL
LOGOUT_URL = "%saccount/logout/" % ROOT_URL
REGISTER_URL = '%saccount/register/' % ROOT_URL#registration_register
CHANGE_PSWD_URL = '%saccount/password/change/' % ROOT_URL#registration_register

CTX_CONFIG = {
    'LBFORUM_TITLE': 'LBForum',
    'LBFORUM_SUB_TITLE': 'A forum engine written in Python using Django',
    'FORUM_PAGE_SIZE': 30,
    'TOPIC_PAGE_SIZE': 15,

    #URLS....
    'LOGIN_URL': LOGIN_URL,
    'LOGOUT_URL': LOGOUT_URL,
    'REGISTER_URL': REGISTER_URL,
    'CHANGE_PSWD_URL': CHANGE_PSWD_URL,
    }

