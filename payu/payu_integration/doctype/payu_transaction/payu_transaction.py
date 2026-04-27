# Copyright (c) 2026, BWH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from email.utils import formatdate
from payu.utils import get_authorization_header

from frappe.integrations.utils import make_post_request


class PayUTransaction(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		checkout_url: DF.Data | None
		mihpayid: DF.Data | None
		status: DF.Literal["Pending", "Success"]
	# end: auto-generated types

	@frappe.whitelist()
	def sync_from_payu(self):
		frappe.only_for("System Manager")
		self._sync_from_payu()


	def _sync_from_payu(self):
		API_ENDPOINT = "https://test.payu.in/v3/transaction"

		date = formatdate()
		payload = {
			"txnId":[self.name]
		}
		body = frappe.as_json(payload)

		headers = {
			"Content-Type": "application/json",
			"accept": "application/json",
			"Info-Command": "verify_payment",
			"date": date,
			"authorization": get_authorization_header(body, date)
		}

		response = make_post_request(API_ENDPOINT, headers=headers, data=body)

		frappe.errprint(response)

		result = response['result'][0]

		self.mihpayid = result['mihpayId']
		self.status = result['status'].capitalize() # success -> "Success"
		self.save(ignore_permissions=True)
