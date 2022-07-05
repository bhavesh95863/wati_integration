# Copyright (c) 2022, Bhavesh Maheshwari and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import re
from frappe.model.document import Document
from frappe import _

class MessageTemplate(Document):
	def validate(self):
		try:
			template_message = self.template_message.format()
		except Exception as e:
			frappe.throw(_("Invalid Message Format"))
		res = re.findall(r'\{.*?\}', template_message)
		# self.template_variable = []
		self.template_variables = ""
		for variable in res:
			if not self.template_variables == "":
				self.template_variables += ","
			variable = variable.replace('{','')
			variable = variable.replace('}','')
			self.template_variables += f"{variable}"
		self.template_variables = self.template_variables