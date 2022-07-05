// Copyright (c) 2022, Bhavesh Maheshwari and contributors
// For license information, please see license.txt

frappe.ui.form.on('Send Wati Message', {
	message_template: function(frm,cdt,cdn) {
		var doc = locals[cdt][cdn];
		frm.call({
			method:"get_variables",
			doc: frm.doc,
			callback:function(r){
				frm.refresh_field("send_message_variables");
			}
		})
	}
});
