import hmac
from hashlib import sha512

import frappe
from frappe.integrations.utils import make_post_request

ENDPOINT_MAPPING = {
	"token": {
		"live": "",
		"test": "https://uat-accounts.payu.in/oauth/token"
	},
	"payments": {
		"live": "",
		"test": "https://apitest.payu.in/v2/payments"
	},
	"payment_links": {
		"live": "",
		"test": "https://uatoneapi.payu.in/payment-links"
	},
	"refunds": {
		"live": "https://info.payu.in/merchant/postservice.php?form=2",
		"test": "https://test.payu.in/merchant/postservice.php?form=2"
	}
}

def get_endpoint(name: str) -> str:
	test_mode = frappe.get_cached_value("PayU Settings", None, "test_mode")

	mode = "live"
	if test_mode:
		mode = "test"

	return ENDPOINT_MAPPING[name][mode]


def get_payu_credentials():
	settings = frappe.get_cached_doc("PayU Settings")

	return frappe._dict(
		{
			"key": settings.key,
			"salt": settings.get_password("salt"),
			"client_id": settings.client_id,
			"client_secret": settings.get_password("client_secret"),
			"mid": settings.mid
		}
	)


def get_authorization_header(body: str, date: str) -> str:
	credentials = get_payu_credentials()
	key = credentials["key"]
	salt = credentials["salt"]

	signature = sha512(f"{body}|{date}|{salt}".encode()).hexdigest()

	return f'hmac username="{key}", algorithm="sha512", headers="date", signature="{signature}"'


def verify_webhook_hash(data: dict) -> bool:
	"""Verify a webhook payload from PayU using the reverse hash formula.

	sha512(SALT|status||||||udf5|udf4|udf3|udf2|udf1|email|firstname|productinfo|amount|txnid|key)
	If `additional_charges` is in the payload, it is prepended to the string.
	Ref: https://docs.payu.in/docs/hashing-request-and-response
	"""
	received_hash = data.get("hash") or ""
	if not received_hash:
		return False

	credentials = get_payu_credentials()

	parts = [
		credentials["salt"],
		data.get("status", ""),
		"", "", "", "", "",
		data.get("udf5", ""),
		data.get("udf4", ""),
		data.get("udf3", ""),
		data.get("udf2", ""),
		data.get("udf1", ""),
		data.get("email", ""),
		data.get("firstname", ""),
		data.get("productinfo", ""),
		data.get("amount", ""),
		data.get("txnid", ""),
		credentials["key"],
	]

	additional_charges = data.get("additional_charges")
	if additional_charges:
		parts.insert(0, additional_charges)

	computed_hash = sha512("|".join(parts).encode()).hexdigest()

	return hmac.compare_digest(computed_hash, received_hash)


def get_access_token(scope: str) -> str:
	token_endpoint = get_endpoint("token")
	credentials = get_payu_credentials()

	cache_key = f"payu_oauth_token:{scope}"
	token = frappe.cache.get_value(cache_key)

	if token:
		return token

	response = make_post_request(
		token_endpoint,
		data={
			"client_id": credentials["client_id"],
			"client_secret": credentials["client_secret"],
			"grant_type": "client_credentials",
			"scope": scope,
		},
	)

	frappe.cache.set_value(
		cache_key,
		response["access_token"],
		expires_in_sec=response["expires_in"]-20
	)

	return response["access_token"]
