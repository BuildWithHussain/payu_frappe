# Copyright (c) 2026, BWH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from payu.utils import get_endpoint, get_access_token, get_payu_credentials
from frappe.integrations.utils import make_post_request


class PayUPaymentLink(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount: DF.Currency
		customer_email: DF.Data | None
		customer_name: DF.Data | None
		customer_phone: DF.Data | None
		description: DF.SmallText
		invoice_id: DF.Data | None
		status: DF.Literal["Unpaid", "Paid", "Expired"]
		url: DF.Data | None
	# end: auto-generated types

	def before_insert(self):
		payment_link_endpoint = get_endpoint("payment_links")
		token = get_access_token("create_payment_links")

		headers = {
			"merchantId": get_payu_credentials().mid,
			"Content-Type": "application/json",
			"Authorization": f"Bearer {token}"
		}

		self.invoice_id = frappe.generate_hash(length=16)

		payload = {
			"subAmount": self.amount,
			"source": "API",
			"description": self.description,
			"udf": {
				"udf1": self.invoice_id
			}
		}

		response = make_post_request(payment_link_endpoint, headers=headers, json=payload)

		result = response["result"]
		self.url = result["paymentLink"]

