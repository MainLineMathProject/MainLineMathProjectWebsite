import os

from flask import Blueprint, render_template, send_from_directory, redirect, request, url_for, current_app
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

views = Blueprint('views', __name__)

sg = SendGridAPIClient(current_app.config['SENDGRID_API_KEY'])

mlmp_email = "mainlinemathproject@gmail.com"
if os.environ.get('FLASK_ENV') == 'development':
	mlmp_email = os.environ.get('DEV_EMAIL')


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
	return render_template("index.html", email_sent=email_sent)


@views.route('/about/', methods=['GET'])
def about():
	return render_template("about.html")


@views.route('/leadership/', methods=['GET'])
def leadership():
	return render_template("leadership.html")


@views.route('/tutors/', methods=['GET'])
def tutors():
	return render_template("tutors.html")


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

	email_sent = False
	# print(dict(request.form))
	if request.form.get("g-recaptcha-response") == "":
		print("SPAM DETECTED! EMAIL NOT SENT!")
	else:
		form_responses = request.form.to_dict()
		form_responses.pop("g-recaptcha-response")
		message = Mail(
			from_email='mlmp.automated@gmail.com',
			to_emails=[mlmp_email, email],
			subject=f'Contact form filled by {name}!',
			html_content=f"A contact form was filled out with details:" +
			             "".join(f"<br>{key.title()}: {value}" for key, value in form_responses.items())
		)
		try:
			sg.send(message)
			email_sent = True
		except Exception as e:
			print(e)

	return redirect(url_for(".index", email_sent=email_sent))


@views.route('/signup/', methods=['GET'])
def signup():
	return render_template("signup.html")
