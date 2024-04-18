import io
import json
import os
import random
import string
from urllib.parse import parse_qs
from urllib.parse import urlparse

import cloudinary
import cloudinary.uploader
import cloudinary.api
import google.auth
import google.auth
import gspread
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

import requests as req

BLOB_READ_WRITE_TOKEN = os.environ["BLOB_READ_WRITE_TOKEN"]

failed_img_url = "https://cdn.bootstrapstudio.io/placeholders/1400x800.png"

google_service_account_key = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_KEY"])
google_creds, _ = google.auth.load_credentials_from_dict(google_service_account_key)
google_drive_service = build('drive', 'v3', credentials=google_creds)

cloudinary_key = json.loads(os.environ["CLOUDINARY_KEY"])
cloudinary.config(
	cloud_name=cloudinary_key["cloud-name"],
	api_key=cloudinary_key["api-key"],
	api_secret=cloudinary_key["api-secret"],
	secure=True
)

VERBOSE = True


def vprint(print_string, end="\n"):
	if VERBOSE:
		print(print_string, end=end)


def download_file_from_drive(real_file_id):
	try:
		request = google_drive_service.files().get_media(fileId=real_file_id)
		file = io.BytesIO()
		downloader = MediaIoBaseDownload(file, request)
		done = False
		while done is False:
			status, done = downloader.next_chunk()
	except HttpError as error:
		print(F'An error occurred while downloading a file: {error}')
		file = None
	return file.getvalue()


def random_string(n=16):
	return "".join(random.choice(string.ascii_lowercase) for _ in range(n))


def fix_tutor_photo(old_photo_url):
	try:
		file_id = parse_qs(urlparse(old_photo_url).query)["id"][0]
		file = download_file_from_drive(file_id)
		file_name = random_string()

		try:
			cloudinary.uploader.upload((file_name, file), public_id=file_name)
			results = cloudinary.CloudinaryImage(file_name).image(
				gravity="face", crop="thumb", aspect_ratio="1", height=256, fetch_format="auto"
			)
			new_photo_url = results.split("=")[2].split("\"")[1]
			vprint(" success!")
		except cloudinary.exceptions.Error as error:
			vprint(f"CLOUDINARY ERROR WITH {old_photo_url} IMAGE!!!")
			new_photo_url = failed_img_url
	except KeyError as e:
		vprint(f"DOWNLOAD ERROR WITH {old_photo_url} IMAGE!!!")
		new_photo_url = failed_img_url

	return new_photo_url


def download_file(real_file_id):
	try:
		file_id = real_file_id

		request = google_drive_service.files().get_media(fileId=file_id)
		file = io.BytesIO()
		downloader = MediaIoBaseDownload(file, request)
		done = False
		while done is False:
			status, done = downloader.next_chunk()
	except HttpError as error:
		print(F'An error occurred while downloading a file: {error}')
		file = None
	return file.getvalue()


def grab_tutor_data():
	def jsonify_tutor(name, grade, subjects, photo):
		last_name, first_name = name.split(", ")
		return {
			"first_name": first_name,
			"last_name": last_name,
			"grade": grade,
			"subjects": subjects.split(", "),
			"photo": photo
		}

	gc = gspread.service_account_from_dict(google_service_account_key)

	sheet = gc.open_by_key("1d-VCm9gh9UweCaPjTE5taCtWGpJ4hOeKP0smgr3nKTQ").get_worksheet(0)

	names = sheet.col_values(2)[1:]
	grades = sheet.col_values(5)[1:]
	teachable_subjects = sheet.col_values(8)[1:]

	photos = sheet.col_values(9)[1:]

	tutor_data = {f"{''.join(names[i].split(', '))}{grades[i][0:2]}": jsonify_tutor(
		names[i],
		grades[i],
		teachable_subjects[i],
		photos[i]
	) for i, _ in enumerate(names)}

	return tutor_data


def update_tutor_data():
	tutor_data = grab_tutor_data()

	# Failed attempt at threading:

	# with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
	# 	future_to_tutor_id = {executor.submit(fix_tutor_photo, tutor["photo"]): tutor_id
	# 	                      for tutor_id, tutor in tutor_data.items()}
	# 	for future in concurrent.futures.as_completed(future_to_tutor_id):
	# 		tutor_id = future_to_tutor_id[future]
	# 		try:
	# 			tutor_data[future_to_tutor_id[future]] = future.result()
	# 		except Exception as e:
	# 			print(f"failed {tutor_id}")
	# 		print(f"Fixed tutor photo: {tutor_id}...")

	for tutor_id, tutor in tutor_data.items():
		vprint(f"Fixing tutor photo {tutor_id}... ", end="")
		tutor["photo"] = fix_tutor_photo(tutor["photo"])

	tutor_list = list(tutor_data.values())
	tutor_list.sort(key=lambda x: x["grade"][0:2], reverse=True)

	req.put(f"https://blob.vercel-storage.com/tutor_data.json", data=json.dumps(tutor_list), headers={
		"access": "public",
		"authorization": f"Bearer {BLOB_READ_WRITE_TOKEN}",
		"x-api-version": "4",
		"x-content-type": 'application/json',
		"x-cache-control-max-age": f"{24 * 60 * 60}",  # Cached for 1 day
		"x-add-random-suffix": "false"
	})


if __name__ == "__main__":
	update_tutor_data()
	print("Finished!")
