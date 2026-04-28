# Copyright (c) 2026, BWH and contributors
# For license information, please see license.txt

from email.utils import formatdate

import frappe
from frappe.integrations.utils import make_post_request
from frappe.model.document import Document

from payu.utils import get_authorization_header


class PayUTransaction(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount: DF.Currency
		checkout_url: DF.Data | None
		currency: DF.Link | None
		mihpayid: DF.Data | None
		status: DF.Literal["Pending", "Success", "Failure", "Cancelled"]
	# end: auto-generated types

	@frappe.whitelist()
	def sync_from_payu(self):
		frappe.only_for("System Manager")
		self._sync_from_payu()


	def _sync_from_payu(self):
		response = get_transactions_from_payu([self.name])
		result = response['result'][0]

		self.mihpayid = result['mihpayId']
		self.status = result['status'].capitalize() # success -> "Success"
		self.save(ignore_permissions=True)


def get_transactions_from_payu(txn_ids: list[str]):
	API_ENDPOINT = "https://test.payu.in/v3/transaction"

	date = formatdate()
	payload = {
		"txnId":txn_ids
	}
	body = frappe.as_json(payload)

	headers = {
		"Content-Type": "application/json",
		"accept": "application/json",
		"Info-Command": "verify_payment",
		"date": date,
		"authorization": get_authorization_header(body, date)
	}

	return make_post_request(API_ENDPOINT, headers=headers, data=body)