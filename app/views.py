import os
import time

import pyotp
import requests as req
from flask import Blueprint, render_template, send_from_directory, redirect, request, url_for, current_app, Response
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

if os.environ.get('FLASK_ENV') == 'development':
	from dotenv import load_dotenv

	load_dotenv()

views = Blueprint('views', __name__)

sg = SendGridAPIClient(os.environ['SENDGRID_API_KEY'])

mlmp_email = "mainlinemathproject@gmail.com"
if os.environ.get('FLASK_ENV') == 'development':
	mlmp_email = os.environ.get('DEV_EMAIL')

EMAIL_VERIFICATION_API_KEY = os.environ["EMAIL_VERIFICATION_API_KEY"]

BLOB_READ_WRITE_TOKEN = os.environ["BLOB_READ_WRITE_TOKEN"]

# MFA_SECRET = os.environ["MFA_SECRET"]
# totp = pyotp.TOTP(MFA_SECRET)


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
	def email_is_spam(email_to_check):
		email_verification_response = req.get(f"https://www.ipqualityscore.com/api/json/email/"
		                                      f"{EMAIL_VERIFICATION_API_KEY}/{email_to_check}").json()
		email_score = email_verification_response["overall_score"]
		return email_score <= 1

	name = request.form.get("name")
	email = request.form.get("email")
	subject = request.form.get("subject")
	message = request.form.get("message")

	email_sent = False
	if request.form.get("g-recaptcha-response") == "" or email_is_spam(email):
		current_log = req.get("https://3zh9uaj4n3dl5zbo.public.blob.vercel-storage.com/contact_form_log.txt").text

		new_log = f"{time.asctime()}-----{name}-----{email}-----{subject}-----{message}"

		req.put(f"https://blob.vercel-storage.com/contact_form_log.txt", data=current_log + "\n" + new_log, headers={
			"access": "public",
			"authorization": f"Bearer {BLOB_READ_WRITE_TOKEN}",
			"x-api-version": "4",
			"x-content-type": 'text/plain',
			"x-add-random-suffix": "false"
		})
	else:
		form_responses = request.form.to_dict()
		form_responses.pop("g-recaptcha-response")
		if "submit" in form_responses:
			form_responses.pop("submit")
		message = Mail(
			from_email='mlmp.automated@gmail.com',
			to_emails=[mlmp_email],
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


# @views.route('/admin-login/', methods=['GET'])
# def admin_login():
# 	return render_template("admin-login.html")
#
#
# valid_admin_creds = []


# @views.route('/admin-login/', methods=['POST'])
# def admin_login_submitted():
# 	if totp.verify(request.form["otp-code"]):
# 		auth_code = pyotp.random_base32()
# 		valid_admin_creds.append((request.remote_addr, auth_code))
# 		return redirect(url_for(".admin", auth=auth_code))
# 	else:
# 		return redirect(url_for(".index"))


# @views.route('/admin/', methods=['GET'])
# def admin():
# 	if 'auth' in request.args and (request.remote_addr, request.args.get("auth")) in valid_admin_creds:
# 		return render_template("admin.html")
# 	else:
# 		return redirect(url_for(".index"))


# @views.route('/admin-logout/', methods=['POST'])
# def admin_logout():
# 	auth_code = request.data.decode()
# 	creds = (request.remote_addr, auth_code)
#
# 	if creds in valid_admin_creds:
# 		valid_admin_creds.remove(creds)
#
# 	return redirect(url_for(".index"))
