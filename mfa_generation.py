import os

import pyotp
import qrcode
from dotenv import load_dotenv

load_dotenv()

secret = os.environ["MFA_SECRET"]

totp_auth = (pyotp.totp.TOTP(secret)
.provisioning_uri(
	name='Admin Page',
	issuer_name='MLMP')
)

qrcode.make(totp_auth).save("qr_auth.png")
