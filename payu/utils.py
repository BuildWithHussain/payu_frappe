import frappe
from hashlib import sha512


def get_payu_credentials():
	settings = frappe.get_cached_doc("PayU Settings")
	key = settings.key
	salt = settings.get_password("salt")

	return {
		"key": key,
		"salt": salt
	}


def get_authorization_header(body: str, date: str) -> str:
	credentials = get_payu_credentials()
	key = credentials["key"]
	salt = credentials["salt"]

	signature = sha512(f"{body}|{date}|{salt}".encode()).hexdigest()

	return f'hmac username="{key}", algorithm="sha512", headers="date", signature="{signature}"'

