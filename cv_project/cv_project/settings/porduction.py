from .base import *

DEBUG = True

ALLOWED_HOSTS = ['cv-practice.herokuapp.com']

DATABASES = {
    'default': dj_database_url.config(
        default=dj_database_url.config('DATABASE_URL')
    )
}
