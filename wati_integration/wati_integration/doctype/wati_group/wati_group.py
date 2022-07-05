# Copyright (c) 2022, Bhavesh Maheshwari and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class WatiGroup(Document):
	pass



@frappe.whitelist()
def get_mobile_no(group_member,document_type):
	mobile_no_field_map = {
		"Employee": "cell_number",
		"Customer": "mobile_no",
		"Supplier": "mobile_no",
		"Lead": "mobile_no"
	}
	if frappe.db.exists(document_type,group_member):		
		return frappe.db.get_value(document_type,group_member,mobile_no_field_map.get(document_type))
	