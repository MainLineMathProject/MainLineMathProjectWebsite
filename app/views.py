import json

import requests
import werkzeug.datastructures.headers
from akismet import Akismet
from flask import Blueprint, render_template, send_from_directory, redirect, request, url_for
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

views = Blueprint('views', __name__)

with open(".local_keys/sendgrid.key") as fp:
	sg = SendGridAPIClient(fp.read())

akismet = Akismet('d806ad6390dc', blog="https://www.mainlinemathproject.org/",
                  application_user_agent="MainlineMathProject Website/1.0.0")


@views.route("/assets/<path:path>")
def static_dir(path):
	return send_from_directory("assets", path)


@views.route('/sitemap.xml')
@views.route('/robots.txt')
def sitemap_and_robots():
	return send_from_directory("assets", request.path[1:])


@views.route("/<path:path>.html/", methods=['GET'])
def html_redirect(path):
	return redirect(f"/{path}")


@views.route('/', methods=['GET'])
def index():
	email_sent = 'email_sent' in request.args and request.args.get("email_sent")
	is_spam = 'is_spam' in request.args and request.args.get("is_spam")
	return render_template("index.html", email_sent=email_sent, is_spam=is_spam)


@views.route('/about/', methods=['GET'])
def about():
	return render_template("about.html")


@views.route('/leadership/', methods=['GET'])
def leadership():
	return render_template("leadership.html")


@views.route('/tutors/', methods=['GET'])
def tutors():
	return render_template("tutors.html")


@views.route('/tutor_data/', methods=['GET'])
def get_tutor_data():
	with open("app/assets/json/tutor_data.json") as fp:
		return json.load(fp)


@views.route('/contacts/', methods=['GET'])
def contacts():
	return render_template("contacts.html")


@views.route('/contacts/', methods=['POST'])
@views.route('/', methods=['POST'])
def contact_form_submitted():
	name = request.form.get("name")
	email = request.form.get("email")
	subject = request.form.get("subject")
	message = request.form.get("message")

	headers: werkzeug.datastructures.headers.Headers = request.headers
	is_spam = bool(akismet.check(
		user_ip=request.remote_addr,
		user_agent=headers.get("User-Agent"),
		comment_author_email=request.form.get("email"),
		comment_content=request.form.get("subject") + " " + request.form.get("message")
	))

	email_sent = False
	if is_spam:
		print("SPAM DETECTED! EMAIL NOT SENT!")
	else:
		message = Mail(
			from_email='mlmp.automated@gmail.com',
			to_emails=['mainlinemathproject@gmail.com', email],
			subject=f'Contact form filled by {name}!',
			html_content=f"A contact form was filled out with details:" +
			             "".join(f"<br>{key.title()}: {value}" for key, value in request.form.items())
		)
		try:
			sg.send(message)
			email_sent = True
		except Exception as e:
			print(e)

	return redirect(url_for(".index", email_sent=email_sent, is_spam=is_spam))


@views.route('/signup/', methods=['GET'])
def signup():
	return render_template("signup.html")
