# Copyright (c) 2025, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime

class MarkAttendance(Document):
	def validate(self):
		if frappe.db.exists("Mark Attendance",{'name':['!=',self.name],'employee':self.employee,'date':self.date}):
			frappe.throw("Already another document found for this date.")

@frappe.whitelist()		
def create_in_checkins(date,employee,in_time,name):
	current_date = datetime.now().date()
	if not frappe.db.exists("Mark Attendance",{'name':['!=',name],'employee':employee,'date':date}):
		if in_time:
			if not frappe.db.exists("Employee Checkin",{'employee':employee,'log_type':'IN','remarks':['!=',''], 'creation': ['between', (current_date, f"{current_date} 23:59:59")]}):
				ec=frappe.new_doc("Employee Checkin")
				ec.employee=employee
				ec.log_type='IN'
				ec.remarks='Automatically created via mark attendance document'
				ec.time=in_time
				ec.insert(ignore_permissions=True)
				frappe.db.commit
		return "ok"

@frappe.whitelist()		
def create_out_checkins(date,employee,out_time,name):
	current_date = datetime.now().date()
	if not frappe.db.exists("Mark Attendance",{'name':['!=',name],'employee':employee,'date':date}):
		if out_time:
			if not frappe.db.exists("Employee Checkin",{'employee':employee,'log_type':'OUT','remarks':['!=',''], 'creation': ['between', (current_date, f"{current_date} 23:59:59")]}):
				ec=frappe.new_doc("Employee Checkin")
				ec.employee=employee
				ec.log_type='OUT'
				ec.remarks='Automatically created via mark attendance document'
				ec.time=out_time
				ec.insert(ignore_permissions=True)
				frappe.db.commit
	return "ok"