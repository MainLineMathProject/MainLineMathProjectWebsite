import json
from os import environ

from flask import Flask


def create_app():
	app = Flask(__name__)
	# app.config['SERVER_NAME'] = '127.0.0.1:5000'

	app.config.from_pyfile('settings.py')

	from .views import views
	app.register_blueprint(views, url_prefix='/')

	return app
