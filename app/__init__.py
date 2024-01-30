from dotenv import load_dotenv

from flask import Flask


def create_app():
	app = Flask(__name__)
	# app.config['SERVER_NAME'] = '127.0.0.1:5000'

	load_dotenv()
	app.config.from_pyfile('settings.py')

	with app.app_context():
		from .views import views
		app.register_blueprint(views, url_prefix='/')

	return app
