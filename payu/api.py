from email.utils import formatdate

import frappe
from frappe.integrations.utils import make_post_request
from frappe.utils import get_url

from .utils import get_authorization_header, get_payu_credentials, get_endpoint

TEST_API_ENDPOINT = "https://apitest.payu.in/v2/payments"
PROD_API_ENDPOINT = ""


@frappe.whitelist()
def initiate_checkout(product_name: str, qty: int = 1):
	date = formatdate()
	credentials = get_payu_credentials()

	price = frappe.db.get_value("Website Item", product_name, "price")
	amount = price * qty

	txn = frappe.get_doc({"doctype": "PayU Transaction", "amount": amount, "currency": "INR"}).insert()

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
			"successAction": f"{get_url('/payment-success')}?event=success",
			"failureAction": f"{get_url('/payment-success')}?event=failure",
			"cancelAction": f"{get_url('/payment-success')}?event=cancel",
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
	response = make_post_request(get_endpoint("payments"), headers=headers, data=body)

	result = response["result"]

	txn.checkout_url = result["checkoutUrl"]
	txn.save()

	return {"checkout_url": txn.checkout_url}


@frappe.whitelist(allow_guest=True)
def webhook():
	data = frappe.form_dict
	frappe.errprint(data)

	if data["payment_source"] != "apiIntInvoice":
		return

	invioce_id = data["udf1"]

	pl = frappe.get_doc("PayU Payment Link", {"invoice_id": invioce_id})
	pl.status = data["status"].capitalize()

	if pl.status == "Success":
		pl.status = "Paid"

	# pl.customer_email = data["email"]
	pl.save(ignore_permissions=True)


# {
# 	"mihpayid": "403993715537310009",
# 	"mode": "CC",
# 	"status": "success",
# 	"key": "GegYQb",
# 	"txnid": "124359",
# 	"amount": "1499.00",
# 	"addedon": "2026-04-28 11:45:35",
# 	"productinfo": "BWH Cohort",
# 	"firstname": "",
# 	"lastname": "",
# 	"address1": "",
# 	"address2": "",
# 	"city": "",
# 	"state": "",
# 	"country": "",
# 	"zipcode": "",
# 	"email": "hussain@frappe.io",
# 	"phone": "917887887654",
# 	"udf1": "",
# 	"udf2": "",
# 	"udf3": "",
# 	"udf4": "",
# 	"udf5": "",
# 	"udf6": "",
# 	"udf7": "",
# 	"udf8": "",
# 	"udf9": "",
# 	"udf10": "",
# 	"card_token": "",
# 	"card_no": "XXXXXXXXXXXX2346",
# 	"field0": "",
# 	"field1": "185974255639459260",
# 	"field2": "191910",
# 	"field3": "1499.00",
# 	"field4": "",
# 	"field5": "00",
# 	"field6": "02",
# 	"field7": "AUTHPOSITIVE",
# 	"field8": "AUTHORIZED",
# 	"field9": "Transaction is Successful",
# 	"payment_source": "apiIntInvoice",
# 	"cardToken": "",
# 	"authenticationMethod": "",
# 	"PG_TYPE": "CC-PG",
# 	"error": "E000",
# 	"error_Message": "No Error",
# 	"net_amount_debit": "1499",
# 	"discount": "0.00",
# 	"offer_key": "",
# 	"offer_availed": "",
# 	"unmappedstatus": "captured",
# 	"hash": "07db5247e59bd82fe1248eb3f32d2eb625b15e5ff267927a7f99052637b54fa4b2d2e0fb0dfa26351e4615c5d4c4a78b15ce02a1da6c48930d626870acfac6d9",
# 	"bank_ref_no": "185974255639459260",
# 	"bank_ref_num": "185974255639459260",
# 	"bankcode": "CC",
# 	"surl": "https://uatoneapi.payu.in/paymentLink/postBackParam.do",
# 	"curl": "https://uatoneapi.payu.in/paymentLink/postBackParam.do",
# 	"furl": "https://uatoneapi.payu.in/paymentLink/postBackParam.do",
# 	"card_hash": "515a2cb0f0e6711f6a3d2c4704cc691d212d4dc0e065c7c8d3441a6b5fc23e97",
# 	"cmd": "payu.api.webhook",
# }

# https://clear-wave-5534.arbok.mrkaran.dev/api/method/payu.api.webhook
