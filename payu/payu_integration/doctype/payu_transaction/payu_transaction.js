// Copyright (c) 2026, BWH and contributors
// For license information, please see license.txt

frappe.ui.form.on("PayU Transaction", {
	refresh(frm) {
        const btn = frm.add_custom_button("Sync from PayU", () => {
            frm.call({
                method: "sync_from_payu",
                doc: frm.doc,
                btn
            }).then(() => {
                frappe.show_alert("Transaction Synced!")
            })
        })
	},
});
