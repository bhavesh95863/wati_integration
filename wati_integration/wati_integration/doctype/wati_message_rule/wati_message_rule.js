// Copyright (c) 2022, Bhavesh Maheshwari and contributors
// For license information, please see license.txt

frappe.ui.form.on('Wati Message Rule', {
	// refresh: function(frm) {

	// }
});


frappe.ui.form.on('Wati Message Rule', {
	setup_fieldname_select: function (frm) {
		// get the doctype to update fields
		if (!frm.doc.ref_doctype) {
			return;
		}

		frappe.model.with_doctype(frm.doc.ref_doctype, function () {
			let get_select_options = function (df, parent_field) {
				// Append parent_field name along with fieldname for child table fields
				let select_value = parent_field ? df.fieldname + ',' + parent_field : df.fieldname;

				return {
					value: select_value,
					label: df.fieldname + ' (' + __(df.label) + ')'
				};
			};


			let fields = frappe.get_doc('DocType', frm.doc.ref_doctype).fields;
			let options = $.map(fields, function (d) {
				return in_list(frappe.model.no_value_type, d.fieldtype)
					? null : get_select_options(d);
			});

			// set value changed options
			frm.set_df_property('fields', 'options', [''].concat(options));
			frm.set_df_property('mobile_no_field', 'options', [''].concat(options));

			frappe.meta.get_docfield("Template Variable", "document_variable",
				// set first option as blank to allow notification not to be defaulted to the owner
				frm.doc.name).options = [""].concat(options);

			frm.fields_dict.template_variable.grid.refresh();



		});
	},
	onload: function (frm) {
		frm.set_query('ref_doctype', function () {
			return {
				filters: {
					istable: 0
				}
			};
		});
	},
	setup:function(frm){
		frm.trigger('setup_fieldname_select')
	},
	refresh: function (frm) {
		frm.trigger('setup_fieldname_select')
		if ((!frm.doc.__islocal) && (!frappe.user.has_role("System Manager"))){
			let meta = frappe.get_meta("Message Rule");
			meta.fields.forEach(value => {
				if (!["Section Break", "Column Break"].includes(value.fieldtype)) {
					frm.set_df_property(value.fieldname,'read_only', 1);
				}
			});
		}
	},
	ref_doctype: function (frm,cdt,cdn) {
		frm.trigger('setup_fieldname_select')
		frappe.model.set_value(cdt,cdn,"message_template","")
	},
	message_template: function(frm,cdt,cdn) {
			frm.call("set_variable")
	}
});