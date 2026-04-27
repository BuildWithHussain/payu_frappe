from email.utils import formatdate

import frappe
from frappe.utils import get_url
from frappe.integrations.utils import make_post_request

from .utils import get_authorization_header, get_payu_credentials


TEST_API_ENDPOINT = "https://apitest.payu.in/v2/payments"
PROD_API_ENDPOINT = ""


@frappe.whitelist()
def initiate_checkout(amount: float):
	date = formatdate()
	credentials = get_payu_credentials()

	txn = frappe.get_doc(
		{
			"doctype": "PayU Transaction",
		}
	).insert()

	payload = {
		"accountId": credentials["key"],
		"txnId": txn.name,
		"referenceId": "b5f2d8785768087678fm9",
		"order": {
			"productInfo": "Test Product",
			"orderedItem": [{"itemId": "ITEM001", "description": "Test Product Description", "quantity": 1}],
			"paymentChargeSpecification": {"price": amount},
		},
		"additionalInfo": {"txnFlow": "nonseamless"},
		"callBackActions": {
			"successAction": f"{get_url('/api/method/payu.api.success_callback')}",
			"failureAction": "https://example.com/failure",
			"cancelAction": "https://example.com/cancel",
		},
		"billingDetails": {
			"firstName": "John",
			"lastName": "Doe",
			"phone": "9876543210",
			"email": "john.doe@example.com",
			"address": {
				"address1": "123 Main Street",
				"city": "Mumbai",
				"state": "Maharashtra",
				"country": "India",
				"zipCode": "400001",
			},
		},
	}

	body = frappe.as_json(payload)
	headers = {
		"date": date,
		"authorization": get_authorization_header(body, date),
		"content-type": "application/json",
		"accept": "application/json",
	}

	response = make_post_request(TEST_API_ENDPOINT, headers=headers, data=body)

	result = response["result"]

	txn.checkout_url = result["checkoutUrl"]
	txn.save()

	return {"checkout_url": txn.checkout_url}


@frappe.whitelist(allow_guest=True)
def success_callback():
	params = frappe.form_dict
	txn_name = params.get("txnId")
	txn = frappe.get_doc("PayU Transaction", txn_name)
	txn._sync_from_payu()

	if txn.status == "Success":
		frappe.redirect_to_message("hello", "<h1>Success!</h1>")

	frappe.throw("something went wrong!!")
