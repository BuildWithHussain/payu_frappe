// Copyright (c) 2026, BWH and contributors
// For license information, please see license.txt

frappe.ui.form.on("PayU Webhook Log", {
	refresh(frm) {
		if (frm.is_new()) return;

		if (frm.doc.status === "Failed" || frm.doc.status === "Pending") {
			frm.add_custom_button(__("Reprocess"), () => {
				frm.call("reprocess").then(() => {
					frappe.show_alert({ message: __("Reprocessing queued"), indicator: "blue" });
					frm.reload_doc();
				});
			});
		}
	},
});
