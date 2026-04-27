# Copyright (c) 2026, BWH and contributors
# For license information, please see license.txt

# import frappe
from frappe.website.website_generator import WebsiteGenerator


class WebsiteItem(WebsiteGenerator):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		currency: DF.Link | None
		is_published: DF.Check
		price: DF.Currency
		product_image: DF.AttachImage | None
		route: DF.Data | None
	# end: auto-generated types

	pass
