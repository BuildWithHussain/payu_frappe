// Copyright (c) 2026, BWH and contributors
// For license information, please see license.txt

frappe.ui.form.on("PayU Payment Link", {
	refresh(frm) {
        frm.add_custom_button("Copy Link", () => {
            frappe.utils.copy_to_clipboard(frm.doc.url)
        })
	},
});


