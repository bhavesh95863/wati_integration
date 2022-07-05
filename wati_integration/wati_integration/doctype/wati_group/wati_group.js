// Copyright (c) 2022, Bhavesh Maheshwari and contributors
// For license information, please see license.txt

frappe.ui.form.on('Wati Group', {
	reference_doctype: function(frm) {
		frm.clear_table("wati_group_details")
		$.each(frm.doc.wati_group_details || [], function(i, d) {
			d.document_type = frm.doc.reference_doctype;
		});
		refresh_field("wati_group_details");
	}
});


frappe.ui.form.on("Wati Group Details", {
	wati_group_details_add: function(frm,cdt,cdn) {
		var row = locals[cdt][cdn];
		if (frm.doc.reference_doctype) {
			row.document_type = frm.doc.reference_doctype;
			refresh_field("document_type", cdn, "wati_group_details");
		} else {
			frm.script_manager.copy_from_first_row("wati_group_details", row, ["document_type"]);
		}
	},
	document_type: function(frm, cdt, cdn) {
		if(!frm.doc.document_type) {
			erpnext.utils.copy_value_in_all_rows(frm.doc, cdt, cdn, "wati_group_details", "document_type");
		}
	},
	group_member: function(frm,cdt,cdn) {
		var doc = locals[cdt][cdn];
		if (doc.group_member) {
			frappe.model.set_value(cdt,cdn,"mobile_no","")
			frappe.call({
				method:"wati_integration.wati_integration.doctype.wati_group.wati_group.get_mobile_no",
				args:{
					'group_member': doc.group_member,
					'document_type': doc.document_type
				},
				callback:function(r) {
					if(r.message){
						frappe.model.set_value(cdt,cdn,"mobile_no",r.message)
					}
				}
			})
		} else{
			frappe.model.set_value(cdt,cdn,"mobile_no","")
		}
	}
});