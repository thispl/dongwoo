# Copyright (c) 2023, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime
from frappe import _, msgprint
from urllib.request import ftpwrapper
from frappe.model.document import Document
from frappe.utils import get_first_day, get_last_day, format_datetime,get_url_to_form,today

class Permission(Document):
	@frappe.whitelist()
	def hour_res(self):
		data = []
		total = 0
		month_start = get_first_day(today())
		month_end = get_last_day(today())
		permission = frappe.db.get_all('Permission',{'employee':self.employee,"permission_date": ('between',(month_start,month_end)),'docstatus':['!=',2]},['*'])    
		for per in permission:
			total_per_time = frappe.db.get_value('Permission',{'name':per.name},['total_time'])
			data.append(total_per_time)
		total = sum(map(int, [i for i in data if i.isdigit()]))
		total_hours = total + float(self.total_time)
		frappe.errprint(total_hours)
		# if total_hours > int(4):
		# 	self.total_time=0
		# 	frappe.throw(_("Only 4 Hours permissions are allowed for a month"))

	def validate(self):
		if self.total_time:
			if float(self.total_time)<=0:
				frappe.throw("Total Permission time should be greater than 0")
		data = []
		total = 0
		month_start = get_first_day(today())
		month_end = get_last_day(today())
		permission = frappe.db.get_all('Permission',{'employee':self.employee,"name":['!=',self.name],"permission_date": ('between',(month_start,month_end)),'docstatus':['!=',2]},['*'])    
		for per in permission:
			total_per_time = frappe.db.get_value('Permission',{'name':per.name},['total_time'])
			total+=float(total_per_time)
		
		total_hours = total + float(self.total_time)
		frappe.errprint(total_hours)
		if total_hours > int(4):
			# self.total_time=0
			frappe.throw(_("Only 4 Hours permissions are allowed for a month"))
		count=frappe.db.count('Permission',{'employee':self.employee,"name":['!=',self.name],"permission_date": ('between',(month_start,month_end)),'docstatus':['!=',2],'name':['!=',self.name]})
		count+=1
		if count > 2:
			frappe.throw(_("Only 2 permission documents are allowed for a month"))
	# # Saturday Restriction Code
	@frappe.whitelist()
	def sat_res(self):
		dates = frappe.db.get_value('permission',{'employee':self.employee,},['permission_date'])
		day = self.permission_date
		date_obj = datetime.strptime(day, '%Y-%m-%d')
		if date_obj.weekday() == 5:
			frappe.throw(_("Permission not allowed in Saturday"))
@frappe.whitelist()
def att_permission_update(doc,method):
	frappe.errprint("Present")
	if frappe.db.exists("Attendance",{'attendance_date':doc.permission_date,'employee':doc.employee,'docstatus':['!=',2]}):
		frappe.errprint("if")
		att=frappe.db.get_value("Attendance",{'attendance_date':doc.permission_date,'employee':doc.employee,'docstatus':['!=',2]},['name'])
		frappe.errprint(att)
		att_perm=frappe.get_doc("Attendance",att)
		att_perm.att_permission = doc.name
		tot=float(doc.total_time)
		if att_perm.working_hours > 0:
			twh=att_perm.working_hours+float(tot)
			if att_perm.shift:
				if att_perm.shift=='C':
					if twh>=3 and twh<7:
						att_perm.status='Half Day'
					elif twh >= 7:
						att_perm.status='Present'
				else:
					if twh>=4 and twh<8:
						att_perm.status='Half Day'
					elif twh >= 8:
						att_perm.status='Present'
		else:
			frappe.errprint('if')
			if doc.total_time=='4':
				frappe.errprint('else')
				att_perm.status='Half Day'
		att_perm.save(ignore_permissions=True)
		frappe.db.commit()
		if att_perm.status=='Present' and att_perm.docstatus==0:
			frappe.db.set_value("Attendance",att_perm.name,'docstatus',1)
@frappe.whitelist()
def att_permission_cancel(doc,method):
	if frappe.db.exists("Attendance",{'att_permission':doc.name,'docstatus':['!=',2]}):
		att=frappe.db.get_value("Attendance",{'att_permission':doc.name,'docstatus':['!=',2]},['name'])
		att_perm=frappe.get_doc("Attendance",att)
		att_perm.att_permission = ''
		att_perm.save(ignore_permissions=True)
		frappe.db.commit()