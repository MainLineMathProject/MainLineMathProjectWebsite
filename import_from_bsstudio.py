import json
import os
import shutil

from dotenv import load_dotenv
from imagekitio import ImageKit
from imagekitio.models.CreateFolderRequestOptions import CreateFolderRequestOptions
from imagekitio.models.DeleteFolderRequestOptions import DeleteFolderRequestOptions
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions

load_dotenv()

source_directory = 'bsstudio_export/'

assets_destination = 'app/assets/'
html_destination = 'app/templates/'
sitemap_robots_destination = 'app/assets/'

image_directory = 'app/assets/img/'

imagekit_key = json.loads(os.environ["IMAGEKIT_KEY"])
imagekit = ImageKit(
	private_key=imagekit_key['private-key'],
	public_key=imagekit_key['public-key'],
	url_endpoint=imagekit_key['url-endpoint']
)


VERBOSE = True


def vprint(print_string):
	if VERBOSE:
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
	# if os.path.isdir(html_destination):
	# 	# 	pass
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


if __name__ == "__main__":
	update_assets_folder()
	update_html_templates()
	update_sitemap_robots()

	upload_images_to_imagekit()
	change_image_references_to_imagekit()
	remove_local_images()

	print("Finished!")
