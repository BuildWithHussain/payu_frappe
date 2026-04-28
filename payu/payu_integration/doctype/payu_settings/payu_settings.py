# Copyright (c) 2026, BWH and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class PayUSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		client_id: DF.Data | None
		client_secret: DF.Password | None
		key: DF.Data | None
		mid: DF.Data | None
		salt: DF.Password | None
		test_mode: DF.Check
	# end: auto-generated types

	pass
