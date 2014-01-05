from .base import *

DEBUG = False

ALLOWED_HOSTS = ['localhost', 'conceptgrapher.org']

COMPRESS_ENABLED = True

COMPRESS_OFFLINE = True

PG_PASSWORD = os.environ["PG_PASSWORD"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'cgdb',                     
        'USER': 'postgres',
        'PASSWORD': PG_PASSWORD,
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

