# Copyright (c) 2022, Bhavesh Maheshwari and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import re
import json
import requests
from frappe.model.document import Document
from frappe.utils import today, getdate, cint, now, add_days, parse_val, cstr,nowdate
from frappe.utils.safe_exec import get_safe_globals
from frappe import _
from urllib.parse import urlencode


class WatiMessageRule(Document):
	def validate(self):
		# if self.rule_based_on == "Sales Order":
		# 	self.set_sales_order_field_name()
		# if self.rule_based_on == "Other":
		self.validate_mobile_no_field()
		# if self.rule_based_on == "Group":
		# 	self.validate_group_field()
		# self.set_variable()
		if self.conditions:
			self.validate_condition()

	def validate_condition(self):
		temp_doc = frappe.new_doc(self.ref_doctype)
		if self.conditions:
			try:
				frappe.safe_eval(self.conditions, None, get_context(temp_doc.as_dict()))
			except Exception:
				frappe.throw(_("The Condition '{0}' is invalid").format(self.conditions))

	def validate_mobile_no_field(self):
		if not self.mobile_no_field:
			frappe.throw("Select Mobile No Field Name.")

	def validate_group_field(self):
		if not self.group_id:
			frappe.throw("Select Group No Field Name.")

	def set_sales_order_field_name(self):
		meta = frappe.get_meta(self.ref_doctype)
		so_field_exists = False
		so_field_name = ''
		if not self.ref_doctype == "Sales Order":
			for field in meta.fields:
				if field.options == "Sales Order":
					so_field_name = field.fieldname
					so_field_exists = True
					break
			self.sales_order_field = so_field_name
			if not so_field_exists:
				frappe.throw("Selected Doctype {0} Does Not Have Sales Order Field. Select Only Doctype Which Have Sales Order Field".format(self.ref_doctype))
		else:
			self.sales_order_field = "name"

	@frappe.whitelist()
	def set_variable(self):
		if self.message_template:
			template_doc = frappe.get_doc("Message Template",self.message_template)
			for variable in template_doc.template_variables.split(','):
				if not frappe.db.exists("Template Variable",{"template_variable": variable,"parenttype":"Wati Message Rule","ref_doctype":self.ref_doctype,"parent":self.name}):
					self.append("template_variable",dict(
						template_variable = variable,
						ref_doctype = self.ref_doctype
					))
		else:
			self.template_variable = []

def get_context(doc):
	return {"doc": doc, "nowdate": nowdate, "frappe": frappe._dict(utils=get_safe_globals().get("frappe").get("utils"))}




def send_message_for_event(doc, method):
	try:
		if (frappe.flags.in_import and frappe.flags.mute_emails) or frappe.flags.in_patch or frappe.flags.in_install:
			return
		get_message_rule(doc, doc.doctype, method)
	except Exception as e:
		frappe.log_error(title='Wati Error Log', message=frappe.get_traceback())

def get_message_rule(self, doctype, method):
    event_map = {
        "on_submit": "Submit",
        "after_insert": "New",
        "on_cancel": "Cancel",
        "after_save": "Save"
    }
    if not self.flags.in_insert:
        # value change is not applicable in insert
        event_map['on_change'] = 'Value Change'
    based_on = event_map.get(method)
    if not based_on:
        return
    rules = frappe.get_all("Wati Message Rule", filters={
                           "based_on": based_on, "ref_doctype": doctype, "enable":1}, fields=["*"])
    if rules:
        evalute_message_rule(self, based_on, rules)


def evalute_message_rule(self, based_on, rules):
    for rule in rules:
        context = get_context(self)
        if context and rule.conditions:
            if not frappe.safe_eval(rule.conditions, None, context):
                return
        if based_on == "Value Change" and not self.is_new():
            if not frappe.db.has_column(self.doctype, rule.fields):
                continue
            else:
                doc_before_save = self.get_doc_before_save()
                field_value_before_save = doc_before_save.get(
                    rule.fields) if doc_before_save else None
                field_value_before_save = parse_val(field_value_before_save)
                if (self.get(rule.fields) == field_value_before_save):
                    # value not changed
                    continue
                else:
                    send_message_using_template(self,rule)
        else:
            send_message_using_template(self,rule)

def send_message_using_template(self,rule):
	rule = frappe.get_doc("Wati Message Rule",rule.name)
	data = []
	for field in rule.template_variable:
		data.append({
			'name': field.get('template_variable'),
			'value': self.get(field.get('document_variable'))
		})
	send_whatsapp_message(rule.message_template,self.get(rule.mobile_no_field),json.dumps(data),self.name,self.doctype)

def send_whatsapp_message(template,mobile,data,document,doctype):
	wati_setting = frappe.get_doc("Wati Setting","Wati Setting")
	if not wati_setting.url or not wati_setting.get('whatsapp_number') or not wati_setting.get('token'):
		frappe.throw(_("Url,Whatsapp Number And Token Mandatory in wati setting for send whatsapp message"))
	base_url = f"{wati_setting.get('url')} /api/v1/sendTemplateMessage/{mobile}?whatsappNumber={wati_setting.get('whatsapp_number')}"
	base_url = wati_setting.get('url') + "/api/v1/sendTemplateMessage/" + mobile + "?whatsappNumber=" + wati_setting.get('whatsapp_number')
	payload = json.dumps({
	"template_name": template,
	"broadcast_name": template,
	"parameters": data
	})
	headers = {
	'Authorization': 'Bearer ' + wati_setting.get("token"),
	'Content-Type': 'application/json',
	'Cookie': 'affinity=1640466569.646.162034.484452'
	}
	response = requests.request("POST", base_url, data=payload, headers=headers)
	frappe.get_doc(dict(
		doctype = "Wati Message Log",
		mobile_no = mobile,
		url = base_url,
		payload = payload,
		headers = json.dumps(headers),
		status_code = response.status_code,
		response = response.text,
		document = document,
		ref_doctype = doctype

	)).insert(ignore_permissions = True)
	frappe.msgprint(_('Whatsapp Message sent on {0}').format(mobile), alert=True, indicator='green')