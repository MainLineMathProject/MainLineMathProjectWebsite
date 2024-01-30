from os import environ

SECRET_KEY = environ.get('SECRET_KEY')
SENDGRID_API_KEY = environ.get('SENDGRID_API_KEY')
GOOGLE_SERVICE_ACCOUNT_KEY = environ.get('GOOGLE_SERVICE_ACCOUNT_KEY')