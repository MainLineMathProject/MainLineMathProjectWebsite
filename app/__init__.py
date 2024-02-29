from dotenv import load_dotenv

from flask import Flask


def create_app():
	app = Flask(__name__)

	load_dotenv()
	app.config.from_pyfile('settings.py')

	with app.app_context():
		from .views import views
		app.register_blueprint(views, url_prefix='/')

	return app
