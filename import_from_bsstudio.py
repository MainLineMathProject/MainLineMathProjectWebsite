import io
import json
import os
import random
import shutil
import string
from urllib.parse import parse_qs
from urllib.parse import urlparse

import cloudinary
import cloudinary.uploader
import google.auth
import google.auth
import gspread
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from imagekitio import ImageKit
from imagekitio.models.CreateFolderRequestOptions import CreateFolderRequestOptions
from imagekitio.models.DeleteFolderRequestOptions import DeleteFolderRequestOptions
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions

source_directory = 'C:/Users/josep/OneDrive/Documents/BootstrapStudioDesigns/exports/'

assets_destination = 'C:/Users/josep/PycharmProjects/MainLineMathProjectWebsite/app/assets/'
html_destination = 'C:/Users/josep/PycharmProjects/MainLineMathProjectWebsite/app/templates/'
sitemap_robots_destination = 'C:/Users/josep/PycharmProjects/MainLineMathProjectWebsite/app/assets/'

failed_img_url = "https://cdn.bootstrapstudio.io/placeholders/1400x800.png"

google_service_account_key = "./.local_keys/mainlinemathproject-bade1ac06345.json"
google_creds, _ = google.auth.load_credentials_from_file(google_service_account_key)
google_drive_service = build('drive', 'v3', credentials=google_creds)

cloudinary.config(
	cloud_name="dlmvik29e",
	api_key="556959486252824",
	api_secret="H6ewqmkZDtFwHcc8s6pk0CRWQlQ"
)

imagekit = ImageKit(
	private_key='private_SeCd2DxPQ/Db/68Szo9UcttTvns=',
	public_key='public_4a7f/gFoCLvr9q/CVpGB7yKPdMA=',
	url_endpoint='https://ik.imagekit.io/mainlinemathproject'
)

image_directory = 'C:/Users/josep/PycharmProjects/MainLineMathProjectWebsite/app/assets/img/'

VERBOSE_STEPS = True


def vprint(print_string):
	if VERBOSE_STEPS:
		print(print_string)


def get_parent_folder(child_name):
	if child_name.endswith("/"):
		child_name = child_name[:-1]
	return os.path.dirname(child_name)


def update_assets_folder():
	if os.path.isdir(assets_destination):
		shutil.rmtree(assets_destination)
	shutil.move(os.path.join(source_directory, 'assets'), get_parent_folder(assets_destination))
	vprint("Updated assets folder...")


def update_html_templates():
	if os.path.isdir(html_destination):
		pass
	html_files = [file for file in os.listdir(source_directory) if file.endswith('.html')]
	for html_file in html_files:
		shutil.move(os.path.join(source_directory, html_file), os.path.join(html_destination, html_file))
	vprint("Updated templates...")


def update_sitemap_robots():
	txt_xml_files = [file for file in os.listdir(source_directory) if (file.endswith('.txt') or file.endswith('.xml'))]
	for txt_xml_file in txt_xml_files:
		shutil.move(os.path.join(source_directory, txt_xml_file),
		            os.path.join(sitemap_robots_destination, txt_xml_file))
	vprint("Updated sitemap.xml & robots.txt...")


def upload_images_to_imagekit():
	for root, _, files in os.walk(image_directory):
		if root == image_directory:
			continue
		folder_name = root.removeprefix(image_directory)

		imagekit.delete_folder(
			options=DeleteFolderRequestOptions(
				folder_path=folder_name
			)
		)
		imagekit.create_folder(
			options=CreateFolderRequestOptions(
				folder_name=folder_name,
				parent_folder_path="/"
			)
		)
		for file in files:
			if file == root:
				continue
			file_name = file
			file_path = os.path.join(root, file)
			imagekit.upload(
				file=open(file_path, "rb"),
				file_name=file_name,
				options=UploadFileRequestOptions(
					use_unique_file_name=False,
					folder=folder_name,
					overwrite_file=True
				)
			)
		vprint(f"Uploaded image folder: {folder_name}...")
	vprint(f"Uploaded local images to imagekitio...")


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


def change_image_references_to_imagekit():
	for file in os.listdir("app/templates"):
		with open(f"app/templates/{file}", "r") as fp:
			file_text = fp.read()

		file_text = file_text.replace("/assets/img/", "https://ik.imagekit.io/mainlinemathproject/")

		with open(f"app/templates/{file}", "w") as fp:
			fp.write(file_text)
	print("Converted image references to imagekitio...")


def remove_local_images():
	for file in os.listdir("app/assets/img"):
		path = "app/assets/img/" + file
		if os.path.isdir(path):
			shutil.rmtree(path)
		else:
			os.remove(path)
	print("Removed local image files...")


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
		except cloudinary.exceptions.Error as error:
			print(f"CLOUDINARY ERROR WITH {old_photo_url} IMAGE!!!")
			new_photo_url = failed_img_url
	except KeyError as e:
		print(f"DOWNLOAD ERROR WITH {old_photo_url} IMAGE!!!")
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

	gc = gspread.service_account(google_service_account_key)

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
		tutor["photo"] = fix_tutor_photo(tutor["photo"])
		vprint(f"Fixed tutor photo {tutor_id}...")

	if not os.path.isdir("app/assets/json"):
		os.mkdir("app/assets/json")

	tutor_list = list(tutor_data.values())
	tutor_list.sort(key=lambda x: x["grade"][0:2], reverse=True)

	with open("app/assets/json/tutor_data.json", "w") as fp:
		json.dump(tutor_list, fp, indent=2)


update_assets_folder()
update_html_templates()
update_sitemap_robots()

upload_images_to_imagekit()
change_image_references_to_imagekit()
remove_local_images()

update_tutor_data()

print("Finished!")
