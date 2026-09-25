# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from functools import total_ordering
from itertools import count
import frappe
from frappe import permissions
from frappe.utils import cstr, cint, getdate, get_last_day, get_first_day, add_days
from frappe.utils import cstr, add_days, date_diff, getdate, format_date
from math import floor
from frappe import msgprint, _
from calendar import month, monthrange
from datetime import date, timedelta, datetime,time
import math
status_map = {
	'Permission Request' :'PR',
	'On Duty':'OD',
	'Half Day':'HD',
	"Absent": "A",
	"Half Day": "HD",
	"Holiday": "HH",
	"Weekly Off": "WW",
	"Present": "P",
	"None" : "-",
	"On Leave":"On Leave",
	"Work From Home": "WFH",
	"Leave Without Pay": "LOP",
	"Casual Leave": "CL",
	"Earned Leave": "EL",
	"Sick Leave": "SL",
	"Maternity Leave":'MTL',
	"Medical Leave": 'MDL',
	"Privilege Leave": "PVL",
	"Compensatory Off": "C-OFF",
}
def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	columns = []
	columns += [
		_("Employee") + ":Data/:150",
		_("Employee Name") + ":Data/:200",
		_("Department") + ":Data/:150",
		_("Designation") + ":Data/:150",
		_("DOJ") + ":Date/:100",
		_("Employee Type") + ":Data/:150",
		_("Details") + ":Data/:150",
	]
	dates = get_dates(filters.from_date,filters.to_date)
	for date in dates:
		date = datetime.strptime(date,'%Y-%m-%d')
		day = datetime.date(date).strftime('%d')
		month = datetime.date(date).strftime('%b')
		columns.append(_(day + '/' + month) + ":Data/:70")
	columns.append(_("SA - A") + ":Data/:100")
	columns.append(_("SA - B") +':Data/:100')
	columns.append(_("SA - C") + ":Data/:100")
	columns.append(_("SA - Wrk")+ ':Data/:100')
	columns.append(_("H") + ":Data/:100")
	columns.append(_("SA - Total") +':Data/:100')
	columns.append(_("Att. - A") + ":Data/:100")
	columns.append(_("Att. - B") +':Data/:100')
	columns.append(_("Att. - C") + ":Data/:100")
	columns.append(_("Att. - Wrk")+ ':Data/:100')
	columns.append(_("H") + ":Data/:100")
	columns.append(_("ATT. - Total") +':Data/:100')
	columns.append(_("Present") + ":Data/:100")
	columns.append(_('Half Day') +':Data/:100')
	columns.append(_("Absent") + ":Data/:100")
	columns.append(_("On Leave")+ ':Data/:100')

	return columns

def get_data(filters):
	data = []
	emp_status_map = []
	employees = get_employees(filters)
	for emp in employees:
		dates = get_dates(filters.from_date,filters.to_date)
		row1 = [emp.name,emp.employee_name,emp.department  or '',emp.designation or '',emp.date_of_joining  or '',emp.employee_type or '',"Scheduled"]
		row2 = ["","","","","","","Actual"]
		row3 = ["","","","","","","Continue"]
		
		total_present = 0
		total_half_day = 0
		total_absent = 0
		total_onleave = 0
		total_weekoff = 0
		total_holiday = 0
		shift = 0
		shift1 = 0
		shift2 = 0
		shift3 = 0
		ashift1 = 0
		ashift2 = 0
		ashift3 = 0
		for date in dates:
			if frappe.db.exists("Shift Assignment",{'start_date':date,'employee':emp.name,'docstatus':('!=',2)}):
				sa = frappe.db.get_value("Shift Assignment",{'start_date':date,'employee':emp.name,'docstatus':('!=',2)},['shift_type'])
				row1.append(sa[0])
				shift += 1
				if sa[0] == "":
					shift1 += 1
				if sa[0] == "":
					shift2 += 1
				if sa[0] == "":
					shift3 += 1
			else:
				hh = check_holiday(date,emp.name)
				if hh:
					if hh == 'WW':
						row1.append("H")
					elif hh == 'HH':
						row1.append("H")
					else:
						row1.append("-")
				else:
					row1.append("-")
			if frappe.db.exists("Attendance",{'attendance_date':date,'employee':emp.name,'docstatus':('!=',2)}):
				att = frappe.db.get_value("Attendance",{'attendance_date':date,'employee':emp.name,'docstatus':('!=',2)},['status','shift','leave_type','employee_type','name','on_duty_application','working_hours'])
				status = status_map.get(att[0], "")
				leave = status_map.get(att[2], "")
				if status == 'P':
					hh = check_holiday(date,emp.name)
					if hh :
						if hh == 'WW':
							total_present = total_present + 1
						else:
							total_present = total_present + 1
					else:
						total_present = total_present + 1
					if att[1]:
						row2.append(att[1])
					else:
						if att[4]:
							row2.append("OD")
						else:
							row2.append("-")
				elif status == 'A':
					hh = check_holiday(date,emp.name)
					if hh:
						if hh == 'WW':
							total_absent = total_absent + 1
						else:
							total_absent = total_absent + 1
					else:
						total_absent = total_absent + 1
					if att[1]:
						row2.append(att[1])
					else:
						row2.append("-")	
				elif status == 'WFH':
					hh = check_holiday(date,emp.name)
					if hh:
						if hh == 'WW':
							total_present = total_present + 1
						else:
							total_present = total_present + 1
					else:
						total_present = total_present + 1
					row2.append("WFH")
				elif status == 'HD':
					hh = check_holiday(date,emp.name)
					if hh:
						if hh == 'WW':
							total_half_day += 1
						else:
							total_half_day += 1
						if att[1]:
							row2.append(att[1])
						else:
							row2.append(att[1])
					else:
						if leave:
							total_half_day += 1
							total_onleave += 0.5
						else:
							total_half_day += 1
						
						if att[1] and leave:
							row2.append(att[1] + leave)
						else:
							row2.append(att[1] + "/LOP")
				elif status == 'On Leave':
					if leave:
						total_onleave += 1
						row2.append(leave)
					else:
						total_onleave += 1
						row2.append("LOP")
				if att[5] is not None and att[5] > 16.0:
					row3.append(round(att[5],2))
				else:
					row3.append("-")
				if att[1]:
					if att[1] == "A":
						ashift1 += 1
					if att[1] == "B":
						ashift2 += 1
					if att[1] == "C":
						ashift3 += 1
			else:
				hh = check_holiday(date,emp.name)
				if hh :
					if hh == 'WW':
						total_weekoff += 1
						row2.append("H")
					elif hh == 'HH':
						total_holiday += 1
						row2.append("H")
					else:
						hh = '-'
						row2.append('-')
				else:
					row2.append('-')
				row3.append("-")
		row1.extend([shift1,shift2,shift3,(shift1+shift2+shift3),(total_weekoff + total_holiday),(shift1+shift2+shift3+total_weekoff + total_holiday),ashift1,ashift2,ashift3,(ashift1+ashift2+ashift3),(total_weekoff + total_holiday),(ashift1+ashift2+ashift3+total_weekoff + total_holiday),total_present,total_half_day,total_absent,total_onleave])
		row2.extend(['','','','','','','','','','','','','','','',''])
		row3.extend(['','','','','','','','','','','','','','','',''])
		data.append(row1)
		data.append(row2)
		data.append(row3)

	return data

def get_dates(from_date,to_date):
	no_of_days = date_diff(add_days(to_date, 1), from_date)
	dates = [add_days(from_date, i) for i in range(0, no_of_days)]
	return dates

def get_employees(filters):
	conditions = ''
	left_employees = []
	if filters.employee:
		conditions += "and e.employee = '%s' " % (filters.employee)
	if filters.designation:
		conditions += "and e.designation = '%s' " % (filters.designation)
	if filters.department:
		conditions+="and e.department = '%s' "%(filters.department)
	if filters.employee_type:
		conditions+="and employee_type = '%s' "%(filters.employee_type)
	employees = frappe.db.sql("""select e.* from `tabEmployee` e inner join `tabDepartment` d on e.department = d.name inner join `tabDesignation` de on de.name = e.designation where e.status = 'Active' and d.name != 'All Departments' %s order by d.order_value, de.order, e.date_of_joining""" % (conditions), as_dict=True)
	left_employees = frappe.db.sql("""select e.* from `tabEmployee` e inner join `tabDepartment` d on e.department = d.name inner join `tabDesignation` de on de.name = e.employee where e.status = 'Left' and e.relieving_date >= '%s' and d.name != 'All Departments' %s order by d.order_value, de.order, e.date_of_joining""" %(filters.from_date,conditions),as_dict=True)
	employees.extend(left_employees)
	return employees

def check_holiday(date,emp):
	holiday_list = frappe.db.get_value('Employee',{'name':emp},'holiday_list')
	holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List`
	left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(holiday_list,date),as_dict=True)
	doj= frappe.db.get_value("Employee",{'name':emp},"date_of_joining")
	status = ''
	if holiday :
		if doj < holiday[0].holiday_date:
			if holiday[0].weekly_off == 1:
				status = "WW"
			else:
				status = "HH"
		else:
			status = 'Not Joined'
	return status





