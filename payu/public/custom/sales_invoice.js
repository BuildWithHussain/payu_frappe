frappe.ui.form.on('Sales Invoice', {
	refresh(frm) {
		frm.add_custom_button("PayU Payment Link", () => {
            frappe.new_doc("PayU Payment Link", {
                "description": `Payment for ${frm.doc.name}`,
                "amount": frm.doc.outstanding_amount,
                "customer_name": frm.doc.customer,
            })
        }, "Create")
	}
})