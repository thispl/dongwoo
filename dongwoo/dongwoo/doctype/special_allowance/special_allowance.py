# Copyright (c) 2024, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from dongwoo.mark_attendance import check_holiday
from frappe.utils import cstr, add_days, date_diff,format_datetime,ceil,flt

class SpecialAllowance(Document):
	def on_submit(self):
		shiftdate=add_days(self.working_date,1)
		hh=check_holiday(shiftdate,self.employee)
		if not hh:
			if not frappe.db.exists("Shift Assignment", {'employee': self.employee, 'start_date': shiftdate, 'end_date': shiftdate, 'docstatus': ['!=',2]}):
				sa = frappe.new_doc('Shift Assignment')
				sa.employee = self.employee
				sa.shift_type = "WW"
				sa.start_date = shiftdate
				sa.end_date = shiftdate
				sa.reason = 'Week Off automatically created for 24 hours working'
				sa.save(ignore_permissions=True)
				sa.submit()
				frappe.db.commit()
			else:
				if frappe.db.exists("Shift Assignment", {'employee': self.employee, 'start_date': shiftdate, 'end_date': shiftdate, 'docstatus': 1, 'shift_type':['!=','WW']}):
					sa_exist=frappe.get_doc("Shift Assignment", {'employee': self.employee, 'start_date': shiftdate, 'end_date': shiftdate, 'docstatus': 1})
					sa_exist.cancel() 
					frappe.db.commit()
					sa = frappe.new_doc('Shift Assignment')
					sa.employee = self.employee
					sa.shift_type = "WW"
					sa.start_date = shiftdate
					sa.end_date = shiftdate
					sa.reason = 'Week Off automatically created for 24 hours working'
					sa.save(ignore_permissions=True)
					sa.submit()
					frappe.db.commit()

	def on_cancel(self):
		shiftdate=add_days(self.working_date,1)
		if frappe.db.exists("Shift Assignment", {'employee': self.employee, 'start_date': shiftdate, 'end_date': shiftdate, 'docstatus': 1, 'shift_type':'WW','reason':['!=','']}):
			sa=frappe.get_doc("Shift Assignment", {'employee': self.employee, 'start_date': shiftdate, 'end_date': shiftdate, 'docstatus': 1, 'shift_type':'WW','reason':['!=','']})
			sa.cancel()
			frappe.db.commit()