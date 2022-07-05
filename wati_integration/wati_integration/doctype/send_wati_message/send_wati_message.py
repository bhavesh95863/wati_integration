# Copyright (c) 2022, Bhavesh Maheshwari and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document
from frappe.utils import now_datetime
from wati_integration.wati_integration.doctype.wati_message_rule.wati_message_rule import send_whatsapp_message


class SendWatiMessage(Document):
	@frappe.whitelist()
	def get_variables(self):
		if self.message_template:
			self.send_message_variables = []
			message_template_doc = frappe.get_doc(
				"Message Template", self.message_template)
			for row in message_template_doc.template_variables.split(','):
				self.append("send_message_variables", dict(
					template_variable=row
				))
		else:
			self.send_message_variables = []

	def on_submit(self):
		if self.when_to_send == "Now":
			send_message(self)
		else:
			self.status = "Scheduled"

@frappe.whitelist()
def cron_job_for_schedule_message():
	from datetime import datetime
	from datetime import timedelta
	from_time = now_datetime()
	to_time = now_datetime() + timedelta(minutes = 1)
	send_sms_data = frappe.db.sql("""SELECT name
FROM `tabSend SMS`
WHERE docstatus=1
  AND sent=0
  AND schedule_date_and_time BETWEEN %s AND %s""",(from_time,to_time),as_dict=1)
	# filters = [
	# 	["docstatus","=",1],
	# 	["sent","=",0],
	# 	["schedule_date_and_time","between",[cstr(from_time),cstr(to_time)]]
	# ]
	# send_sms_data = frappe.get_all("Send SMS",filters=filters,fields=["name"])
	# print(send_sms_data)
	
	frappe.enqueue(enqueue_send_message, send_sms_data=send_sms_data,queue="long")

def enqueue_send_message(send_sms_data):
	for row in send_sms_data:
		send_sms_doc = frappe.get_doc("Send SMS",row.name)
		send_message(send_sms_doc)
		frappe.db.set_value("Send SMS",row.name,"sent",1)

def send_message(doc):
	if doc.message_send_to == "All Supplier":
		send_message_supplier(doc)
	if doc.message_send_to == "All Employee":
		send_message_employee(doc)
	if doc.message_send_to == "All Customer":
		send_message_customer(doc)
	if doc.message_send_to == "All Lead":
		send_message_lead(doc)
	if doc.message_send_to == "Group":
		send_message_group(doc)
	
def send_message_supplier(doc):
	suppliers_detail = frappe.get_all("Supplier",filters={"disabled":0},fields=["name","mobile_no"])
	for row in suppliers_detail:
		message_template_data = get_template_data(doc)
		if row.get('mobile_no'):
			send_whatsapp_message(doc.message_template, row.get('mobile_no'), message_template_data, doc.name,doc.doctype)

def send_message_employee(doc):
	employees_detail = frappe.get_all("Employee",filters={"status":'Active'},fields=["name","cell_number as 'mobile_no'"])
	for row in employees_detail:
		message_template_data = get_template_data(doc)
		if row.get('mobile_no'):
			send_whatsapp_message(doc.message_template, row.get('mobile_no'), message_template_data, doc.name,doc.doctype)

def send_message_customer(doc):
	customer_details = frappe.get_all("Customer",filters={"disabled":0},fields=["name","mobile_no"])
	for row in customer_details:
		message_template_data = get_template_data(doc)
		if row.get('mobile_no'):
			send_whatsapp_message(doc.message_template, row.get('mobile_no'), message_template_data, doc.name,doc.doctype)

def send_message_lead(doc):
	lead_details = frappe.get_all("Lead",filters={},fields=["name","mobile_no"])
	for row in lead_details:
		message_template_data = get_template_data(doc)
		if row.get('mobile_no'):
			send_whatsapp_message(doc.message_template, row.get('mobile_no'), message_template_data, doc.name,doc.doctype)

def send_message_group(doc):
	group_doc = frappe.get_doc("Wati Group",doc.group)
	message_template_data = get_template_data(doc)
	for row in group_doc.wati_group_details:
		if row.enable and row.get('mobile_no'):
			send_whatsapp_message(doc.message_template,row.get('mobile_no'), message_template_data, doc.name,doc.doctype)


def get_template_data(doc):
	data = []
	for field in doc.send_message_variables:
		data.append({
			'name': field.get('template_variable'),
			'value': field.get('value')
		})
	return json.dumps(data)