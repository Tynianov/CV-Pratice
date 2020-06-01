from .base import *

DEBUG = True

ALLOWED_HOSTS = ['cv-practice.herokuapp.com']


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'cv',
        'USER': 'root',
        'PASSWORD': '1',
        'HOST': 'localhost',
        'PORT': 3306,
    }
}
