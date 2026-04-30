# Copyright (c) 2026, BWH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PayUWebhookLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		error: DF.LongText | None
		mihpayid: DF.Data | None
		payload: DF.Code | None
		payment_source: DF.Data | None
		processed_at: DF.Datetime | None
		status: DF.Literal["Pending", "Processed", "Failed"]
		txnid: DF.Data | None
	# end: auto-generated types

	@frappe.whitelist()
	def reprocess(self):
		frappe.only_for("System Manager")
		from payu.api import process_webhook

		frappe.db.set_value(
			"PayU Webhook Log",
			self.name,
			{"status": "Pending", "error": None, "processed_at": None},
		)
		frappe.enqueue(
			process_webhook,
			log_name=self.name,
			queue="short",
			job_id=f"payu_webhook_{self.name}",
			deduplicate=True,
		)
