from os import environ

SECRET_KEY = environ.get('SECRET_KEY')
SENDGRID_API_KEY = environ.get('SENDGRID_API_KEY')
AKISMET_KEY = environ.get('AKISMET_KEY')