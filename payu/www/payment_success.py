import frappe


def get_context(context):
	frappe.local.response_headers.set("Cache-Control", "public, max-age=0, must-revalidate")

	event = frappe.form_dict.get("event")
	txn_name = frappe.form_dict.get("txnId") or frappe.form_dict.get("txnid")

	context.no_cache = 1
	context.payment = frappe._dict(
		{
			"heading": "Payment Status",
			"message": "Payment response could not be processed.",
		}
	)

	if not txn_name:
		return

	txn = frappe.get_doc("PayU Transaction", txn_name)
	txn._sync_from_payu()

	if txn.status == "Success":
		context.payment.heading = "Payment Successful"
		context.payment.message = "Payment verified and completed successfully."
		return

	context.payment.heading = "Payment Failed" if event == "failure" else "Payment Cancelled"
	context.payment.message = "Payment was not completed."
