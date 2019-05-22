# Django settings for portal project.
import os
dirname = os.path.dirname(globals()["__file__"])

import sys 
reload(sys)  
sys.setdefaultencoding('utf8')

DEBUG = True
#TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'rivelo_portal',
        'USER': 'rivelo_portal',
        'PASSWORD': 'qwerty',
        'HOST': '127.0.0.1',
        'PORT': '3306',        
    },
    'catalog': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'rivelo',
        'USER': 'rivelo',
        'PASSWORD': 'Pnj5i5zjF6uC7nv',
        'HOST': '127.0.0.1',
        'PORT': '3306',        
    },
    
}

DATABASE_HOST = '';

#DATABASE_ROUTERS = ['portal.db_router.CatalogRouter', 'portal.db_router.OtherRouter']
DATABASE_ROUTERS = ['portal.db_router.DBRouter',]

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Helsinki'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
#LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'uk'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

PROJECT_DIR = os.path.join(dirname, '')
ICON_DIR = '/media/upload/icons/'
# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
#MEDIA_ROOT = ''
MEDIA_ROOT = os.path.join(dirname, 'media/')


# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
#MEDIA_URL = ''
MEDIA_URL = "/media/"

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
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
SECRET_KEY = '2k(1v$9uwuab9si23^+7y7s^jm6q)j5%8zdi3i-4!j^n8)ubo2'

# List of callables that know how to import templates from various sources.
'''
if DEBUG:
    TEMPLATE_LOADERS = [
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',      
    ]
else:
    TEMPLATE_LOADERS = [
        ('django.template.loaders.cached.Loader',(
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
            'forum.modules.template_loader.module_templates_loader',
            'forum.skins.load_template_source',
            )),
    ]
'''

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
)

ROOT_URLCONF = 'portal.urls'

'''
TEMPLATE_DIRS = (
    os.path.join(dirname, 'templates'),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)
'''

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(dirname, 'templates'), 
            #PROJECT_DIR.child('templates'),
            'c:/svn/portal/portal/templates/'
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                
                'social_django.context_processors.backends',  # <--
                'social_django.context_processors.login_redirect', # <--
            ], 
            'libraries':{
#                'extra_tags': 'portal.event_calendar.templatetags.extra_tags',
                'poll_extras': 'portal.templatetags.poll_extras',

            }
            #'loaders': [
                # insert your TEMPLATE_LOADERS here
#            'django.template.loaders.filesystem.Loader',
#            'django.template.loaders.cached.Loader',
#            'django.template.loaders.app_directories.Loader',
            #'forum.modules.template_loader.module_templates_loader',
            #'forum.skins.load_template_source',
            #],
        },
    },

]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'social_core.backends.facebook.FacebookOAuth2',
    'social_core.backends.google.GoogleOAuth2',
)

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
#    'social_django',
    'social.apps.django_app.default',
    
    'portal',
    'portal.news',
    'portal.gallery',
    'portal.event_calendar',
    'portal.funnies',
#    'portal.tools',
    'portal.accounting',
    
    'tinymce',	
)

#Hash for APP
CHK_APP_HASH = 'Rivelo256haSh+1234567890-2019'

# GOOGLE setting
RECAPTCHA_SECRET_KEY = "6LeptAUTAAAAAMWpC4bEiwcDvda48vC8IcCzQJNf"

#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#DEFAULT_FROM_EMAIL = 'rivelo@ymail.com'
EMAIL_USE_SSL = True
#EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'rivno100@gmail.com'
EMAIL_HOST_PASSWORD = 'rivelo2016'
EMAIL_PORT = 465

DEFAULT_DOMAIN = 'http://rivelo.com.ua'

SOCIAL_AUTH_FACEBOOK_KEY = '150792262235869'  # App ID
SOCIAL_AUTH_FACEBOOK_SECRET = 'b11f561cdaaec12dd209b7e2a72ad7b8'  # App Secret

SOCIAL_AUTH_LOGIN_ERROR_URL = '/settings/'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/settings/'
SOCIAL_AUTH_RAISE_EXCEPTIONS = False

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '72132850108-ocec45lqkjqdmdbva5thrv5h8fgfbhmp.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'mSNna6tYH_VXImgPCiKq6YXb'
LOGIN_REDIRECT_URL = 'http://localhost:8001/g/outh'

# Google OAuth2 (google-oauth2)
SOCIAL_AUTH_GOOGLE_OAUTH2_IGNORE_DEFAULT_SCOPE = True
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
'https://www.googleapis.com/auth/userinfo.email',
'https://www.googleapis.com/auth/userinfo.profile'
]

# Google+ SignIn (google-plus)
SOCIAL_AUTH_GOOGLE_PLUS_IGNORE_DEFAULT_SCOPE = True
SOCIAL_AUTH_GOOGLE_PLUS_SCOPE = [
'https://www.googleapis.com/auth/plus.login',
'https://www.googleapis.com/auth/userinfo.email',
'https://www.googleapis.com/auth/userinfo.profile'
]

SOCIAL_AUTH_GOOGLE_OAUTH2_USE_DEPRECATED_API = True
SOCIAL_AUTH_GOOGLE_PLUS_USE_DEPRECATED_API = True


FACEBOOK_EXTENDED_PERMISSIONS = ['email', 'user_birthday', 'user_location']

'''
SOCIAL_AUTH_PIPELINE = (
    'social_auth.backends.pipeline.social.social_auth_user',
    'social_auth.backends.pipeline.user.get_username',
    'social_auth.backends.pipeline.misc.save_status_to_session',
    'web.facebook.check_registered',
    'social_auth.backends.pipeline.user.create_user',
    'web.facebook.check_profile',
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.social.load_extra_data',
    'social_auth.backends.pipeline.user.update_user_details'
)
'''

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
