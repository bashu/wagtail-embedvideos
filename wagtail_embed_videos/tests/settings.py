import os

WAGTAIL_ROOT = os.path.dirname(__file__)
STATIC_ROOT = os.path.join(WAGTAIL_ROOT, 'test-static')
MEDIA_ROOT = os.path.join(WAGTAIL_ROOT, 'test-media')
MEDIA_URL = '/media/'


DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DATABASE_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('DATABASE_NAME', 'wagtail'),
        'USER': os.environ.get('DATABASE_USER', None),
        'PASSWORD': os.environ.get('DATABASE_PASS', None),
        'HOST': os.environ.get('DATABASE_HOST', None),

        'TEST': {
            'NAME': os.environ.get('DATABASE_NAME', None),
        }
    }
}


SECRET_KEY = 'not needed'

ROOT_URLCONF = 'wagtail.tests.urls'

STATIC_URL = '/static/'
STATIC_ROOT = STATIC_ROOT

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

USE_TZ = True

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
                'django.template.context_processors.request',
                'wagtail.tests.context_processors.do_not_use_static_url',
                'wagtail.contrib.settings.context_processors.settings',
            ],
        },
    },
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'APP_DIRS': True,
        'OPTIONS': {
            'extensions': [
                'wagtail.core.jinja2tags.core',
                'wagtail.admin.jinja2tags.userbar',
                'wagtail.images.jinja2tags.images',
            ],
        },
    },
]

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'wagtail.core.middleware.SiteMiddleware',

    'wagtail.redirects.middleware.RedirectMiddleware',
)

INSTALLED_APPS = (
    # Install wagtailredirects with its appconfig
    # Theres nothing special about wagtailredirects, we just need to have one
    # app which uses AppConfigs to test that hooks load properly
    'wagtail.forms',
    'wagtail.redirects',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.docs',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail.core',
    'wagtail.contrib.wagtailapi',

    'modelcluster',
    'compressor',
    'taggit',
    'rest_framework',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'embed_video',
    'wagtail_embed_videos',
)


# Using DatabaseCache to make sure that the cache is cleared between tests.
# This prevents false-positives in some wagtail core tests where we are
# changing the 'wagtail_root_paths' key which may cause future tests to fail.
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache',
    }
}

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',  # don't use the intentionally slow default password hasher
)

COMPRESS_ENABLED = False  # disable compression so that we can run tests on the content of the compress tag


WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail.search.backends.db',
    }
}

if 'ELASTICSEARCH_URL' in os.environ:
    WAGTAILSEARCH_BACKENDS['elasticsearch'] = {
        'BACKEND': 'wagtail.search.backends.elasticsearch',
        'URLS': [os.environ['ELASTICSEARCH_URL']],
        'TIMEOUT': 10,
        'max_retries': 1,
        'AUTO_UPDATE': False,
    }


WAGTAIL_SITE_NAME = "Test Site"
