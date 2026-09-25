# Copyright (c) 2023, TEAMPRO and contributors
# For license information, please see license.txt

# import frappe
from __future__ import unicode_literals
from csv import writer
from inspect import getfile
from unicodedata import name
import frappe
from frappe.utils import cstr, add_days, date_diff, getdate
from frappe import _
from frappe.utils.csvutils import UnicodeWriter, read_csv_content
from frappe.utils.file_manager import get_file, upload
from frappe.model.document import Document
from datetime import datetime,timedelta,date,time
from frappe.utils import cint,today,flt,date_diff,add_days,add_months,date_diff,getdate,formatdate,cint,cstr
# from numpy import unicode_
from frappe.utils.background_jobs import enqueue
from frappe.model.document import Document

class ShiftSchedule(Document):
	def on_submit(self): 
		if self.attach:
			args = {'attach':self.attach,'fdate':self.from_date,'tdate':self.to_date,'name':self.name}
			frappe.msgprint("Shift Assignment are creating in background.Kindly check after few minutes.")
			enqueue(create_shift_assignment, queue='default', timeout=6000, event='create_shift_assignment',args=args)
		else:
			frappe.throw("Kindly attach the file to submit the schedule")
	def on_cancel(self):
		if self.attach:
			args = {'attach':self.attach,'fdate':self.from_date,'tdate':self.to_date,'name':self.name}
			enqueue(cancel_shift_assignment, queue='default', timeout=6000, event='cancel_shift_assignment',args=args)
			# self.cancel_shift_assignment()

	def get_dates(self,from_date,to_date):
		no_of_days = date_diff(add_days(to_date, 1), from_date)
		dates = [add_days(from_date, i) for i in range(0, no_of_days)]
		return dates

	@frappe.whitelist()
	def validate(self):

		shift_assignment = frappe.db.sql("""select name from `tabShift Assignment` where department = '%s' and start_date between '%s' and '%s' """ % (self.department, self.from_date, self.to_date), as_dict=True)
		if shift_assignment:
				self.upload = ''
				return 'Shift Schedule already submitted for the selected date'
		if self.attach:
			check_shift_assignment(self.attach, self.from_date, self.to_date)



@frappe.whitelist()	
def get_dates(from_date,to_date):
		no_of_days = date_diff(add_days(to_date, 1), from_date)
		dates = [add_days(from_date, i) for i in range(0, no_of_days)]
		return dates

@frappe.whitelist()
def get_template():
	args = frappe.local.form_dict
	if getdate(args.from_date) > getdate(args.to_date):
		frappe.throw(_("To Date should be greater than From Date"))
	w = UnicodeWriter()
	w = add_header(w, args)
	w = add_data(w, args)
	frappe.response['result'] = cstr(w.getvalue())
	frappe.response['type'] = 'csv'
	frappe.response['doctype'] = "Shift Assignment"

def add_header(w, args):
	base_header = ['Employee ID', 'Employee Name', 'Department','Category']
	date_header = get_dates(args['from_date'], args['to_date'])
	complete_header = base_header + date_header
	w.writerow(complete_header)
	print("Header written:", complete_header)  
	return w  

def add_data(w, args):
	data = get_data(args)
	writedata(w, data)
	return w  

@frappe.whitelist()
def get_data(args):
	department=frappe.db.get_value('Shift Schedule',{"name":args.name},['department'])
	# department = args.department
	if args.department == 'All Departments' and args.employee_type:
		employees = frappe.db.get_all('Employee', {'status': 'Active', 'employee_type': args.employee_type}, ['*'])
	elif args.department and args.employee_type:
		employees = frappe.db.get_all('Employee', {'status': 'Active', 'department': department,'employee_type':args.employee_type}, ['*'])
	elif args.department and args.department !='All Departments':
		employees = frappe.db.get_all('Employee', {'status': 'Active', 'department': department}, ['*'])
	elif args.employee_type:
		employees = frappe.db.get_all('Employee', {'status': 'Active', 'employee_type': args.employee_type}, ['*'])
	elif args.department == 'All Departments':
		employees = frappe.db.get_all('Employee', {'status': 'Active'}, ['*'])
		
	data = []
	for emp in employees:
		row = [
			emp.name, emp.first_name, emp.department,emp.employee_type
		]
		data.append(row)
	return data

@frappe.whitelist()
def writedata(w, data):
	for row in data:
		w.writerow(row)

class UnicodeWriter:
	def __init__(self):
		import csv
		from io import StringIO
		self.stream = StringIO()
		self.writer = csv.writer(self.stream)
	def writerow(self, row):
		self.writer.writerow(row)
	def getvalue(self):
		return self.stream.getvalue()

@frappe.whitelist()
def check_shift_assignment(file, from_date, to_date):
    filepath = get_file(file)
    pps = read_csv_content(filepath[1])
    dates = get_dates(from_date, to_date)

    for pp in pps[1:]:
        ppcount = 4
        while ppcount < len(pp):
            shift = pp[ppcount]
            # if not frappe.db.exists("Shift Type", {'name': shift}):
            #     error_message = "Shift type <strong>" + str(shift) + "</strong> not found. Check the schedule again."
            #     frappe.msgprint(error_message)
            #     frappe.throw(error_message)
            ppcount += 1
		

@frappe.whitelist()
def create_shift_assignment(args):
		filepath = get_file(args['attach'])
		pps = read_csv_content(filepath[1])
		dates = get_dates(args['fdate'],args['tdate'])
		for pp in pps[1:]:
			ppcount = 4
			for date in dates:
				if ppcount < len(pp): 
					shift = pp[ppcount]
					if shift=='H':
						shift='WW'
					else:
						shift = pp[ppcount]
					ppcount += 1  
					if shift:
						if not frappe.db.exists("Shift Assignment", {'employee': pp[0], 'start_date': date, 'end_date': date, 'docstatus': ['in', [0, 1]]}):
							doc = frappe.new_doc('Shift Assignment')
							doc.employee = pp[0]
							# doc.employee_name = pp[1]
							doc.shift_type = shift
							doc.department = pp[2]
							doc.schedule=args['name']
							doc.start_date = date
							doc.end_date = date
							doc.save(ignore_permissions=True)
							doc.submit()
							frappe.db.commit()
@frappe.whitelist()
def cancel_shift_assignment(args):
		filepath = get_file(args['attach'])
		pps = read_csv_content(filepath[1])
		dates = get_dates(args['fdate'],args['tdate'])
		
		for pp in pps[1:]:
			ppcount = 3  
			for date in dates:
				if ppcount < len(pp): 
					shift = pp[ppcount]
					ppcount += 1
					if shift:
						if frappe.db.exists("Shift Assignment", {'employee': pp[0], 'start_date': date, 'end_date': date, 'docstatus': ['in', [0, 1]]}):
							doc = frappe.get_doc('Shift Assignment', {'employee': pp[0], 'start_date': date, 'end_date': date, 'docstatus': ['in', [0, 1]]})
							doc.cancel()
							frappe.db.commit()