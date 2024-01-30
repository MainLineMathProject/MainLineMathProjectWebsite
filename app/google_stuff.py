from __future__ import print_function

import io
import random
import string

import google.auth
import gspread
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

service_account_key = "./.keys/mainlinemathproject-bade1ac06345.json"
creds, _ = google.auth.load_credentials_from_file(service_account_key)
service = build('drive', 'v3', credentials=creds)


# grabify_enabled = True
# def grabify(message):
# 	if grabify_enabled:
# 		requests.get("https://grabify.link/777G68", headers={
# 			'User-Agent': str(message)
# 		})



