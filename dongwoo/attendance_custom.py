import frappe
from frappe.utils import time_diff_in_hours 
from datetime import datetime , timedelta
from frappe import throw,_
from frappe.utils import cstr, add_days, date_diff, getdate, format_date
from dongwoo.mark_attendance import check_holiday
from datetime import datetime
from datetime import timedelta, time,date
from itertools import chain
from frappe.utils import time_diff_in_hours, formatdate, get_first_day,get_last_day, nowdate, now_datetime
from frappe.model.document import Document
from hrms.hr.utils import get_holiday_dates_for_employee
from hrms.hr.utils import get_holidays_for_employee
from frappe.utils import cstr, add_days, date_diff,format_datetime,ceil,flt
from dongwoo.mark_attendance import check_holiday
from frappe.utils.data import today, add_days, add_years
import csv
import io
from datetime import datetime, timedelta
import calendar
from frappe import _
from frappe.utils import getdate, get_site_path
from frappe.utils.file_manager import get_file

#use to create Employee Checkin from Unregistered Employeed Checkin
@frappe.whitelist()
def get_urc_to_ec(from_date):
    print("HI")
    urc = frappe.db.sql("""select biometric_pin,biometric_time,log_type,locationdevice_id,name from `tabUnregistered Employee Checkin` where date(biometric_time) = '%s' """%(from_date),as_dict=True)
    for uc in urc:
        pin = uc.biometric_pin
        time = uc.biometric_time
        dev = uc.locationdevice_id
        typ = uc.log_type
        nam = uc.name
        if time != "":
            if frappe.db.exists('Employee',{'name':pin}):
                if frappe.db.exists('Employee Checkin',{'biometric_pin':pin,"time":time}):
                    print("HI")
                else:
                    print("HII")
                    ec = frappe.new_doc('Employee Checkin')
                    ec.biometric_pin = pin
                    ec.employee = frappe.db.get_value('Employee',{'biometric_pin':pin},['employee_number'])
                    ec.time = time
                    ec.device_id = dev
                    ec.log_type = typ
                    ec.save(ignore_permissions=True)
                    frappe.db.commit()
                    print("Created")
                    attendance = frappe.db.sql(""" delete from `tabUnregistered Employee Checkin` where name = '%s' """%(nam))
                    print("Deleted")       
            else:
                print("hello")
    return "ok"



@frappe.whitelist()
def create_special_allow_emp(fdate, tdate,emp):
    special_all = 0
    attendance = frappe.get_all(
        "Attendance", {'employee_type': 'Staff','working_hours': ('>=', 20),'employee':emp, 'attendance_date': ('between', (fdate, tdate))},
        ['attendance_date', 'out_time', 'employee']
    )
    
    if attendance:  
        for att in attendance:
            emp_name = att.employee
            frappe.errprint(f"Processing employee: {emp_name} on {att.attendance_date}")
            start_date = fdate
            end_date = add_days(tdate, 1)
            holiday_dates = get_holiday_dates_for_employee(att.employee, fdate, end_date)
            if not holiday_dates:
                holiday_dates = []

            query = """SELECT cast(start_date as char) FROM `tabShift Assignment` WHERE employee='%s' AND shift_type = 'WW' AND reason = '' AND start_date BETWEEN '%s' AND '%s'"""  % (att.employee, start_date, end_date)
            ww = frappe.db.sql(query, as_list=True)
            ww_list = list(chain(*ww))
            holiday_dates.extend(ww_list)
            day_before_holidays = []
            for holiday in holiday_dates:
                day_before_holidays.append(add_days(holiday, -1)) 
             
            day_of_week = att.attendance_date.weekday()
            if cstr(att.attendance_date) in holiday_dates and cstr(att.attendance_date) not in day_before_holidays:
                special_all = 2500
            elif cstr(att.attendance_date) in day_before_holidays and cstr(att.attendance_date) not in holiday_dates:
                special_all = 3000
            elif cstr(att.attendance_date) in day_before_holidays and cstr(att.attendance_date) in holiday_dates:
                special_all = 3000
            else:
                frappe.errprint(att.employee)
                frappe.errprint(day_of_week)
                if day_of_week in [0, 1, 2, 3, 4]:
                    special_all = 1000
                elif day_of_week == 5:
                    special_all = 3000 
                elif day_of_week == 6:
                    special_all = 2500
            if special_all>0:
                if frappe.db.exists("Special Allowance", {'working_date': att.attendance_date, 'employee': att.employee, 'docstatus': ['!=', 2]}):
                    # count += 1
                    allow = frappe.get_doc("Special Allowance", {'working_date': att.attendance_date, 'employee': att.employee, 'docstatus': ['!=', 2]})
                    allow.employee = emp_name
                    allow.working_date = att.attendance_date
                    allow.amount = special_all
                    frappe.db.commit()
                    allow.save(ignore_permissions=True)
                else:
                    allow = frappe.new_doc('Special Allowance')
                    # frappe.errprint(f"Creating Special Allowance for {emp_name}")
                    allow.employee = emp_name
                    allow.working_date = att.attendance_date
                    allow.amount = special_all
                    allow.save(ignore_permissions=True)
                    frappe.db.commit()




@frappe.whitelist()
def create_special_allow_employee_type(fdate, tdate,employee_type):
    special_all = 0
    attendance = frappe.get_all(
        "Attendance", {'employee_type': 'Staff','working_hours': ('>=', 20), 'attendance_date': ('between', (fdate, tdate))},
        ['attendance_date', 'out_time', 'employee']
    )
    
    if attendance:  
        for att in attendance:
            emp_name = att.employee
            frappe.errprint(f"Processing employee: {emp_name} on {att.attendance_date}")
            start_date = fdate
            end_date = add_days(tdate, 1)
            holiday_dates = get_holiday_dates_for_employee(att.employee, fdate, end_date)
            if not holiday_dates:
                holiday_dates = []

            query = """SELECT cast(start_date as char) FROM `tabShift Assignment` WHERE employee='%s' AND shift_type = 'WW' AND reason = '' AND start_date BETWEEN '%s' AND '%s'"""  % (att.employee, start_date, end_date)
            ww = frappe.db.sql(query, as_list=True)
            ww_list = list(chain(*ww))
            holiday_dates.extend(ww_list)
            day_before_holidays = []
            for holiday in holiday_dates:
                day_before_holidays.append(add_days(holiday, -1)) 
             
            day_of_week = att.attendance_date.weekday()
            if cstr(att.attendance_date) in holiday_dates and cstr(att.attendance_date) not in day_before_holidays:
                special_all = 2500
            elif cstr(att.attendance_date) in day_before_holidays and cstr(att.attendance_date) not in holiday_dates:
                special_all = 3000
            elif cstr(att.attendance_date) in day_before_holidays and cstr(att.attendance_date) in holiday_dates:
                special_all = 3000
            else:
                if day_of_week in [0, 1, 2, 3, 4]:
                    special_all = 1000
                elif day_of_week == 5:
                    special_all = 3000 
                elif day_of_week == 6:
                    special_all = 2500
            if special_all>0:
                if frappe.db.exists("Special Allowance", {'working_date': att.attendance_date, 'employee': att.employee, 'docstatus': ['!=', 2]}):
                    # count += 1
                    allow = frappe.get_doc("Special Allowance", {'working_date': att.attendance_date, 'employee': att.employee, 'docstatus': ['!=', 2]})
                    allow.employee = emp_name
                    allow.working_date = att.attendance_date
                    allow.amount = special_all
                    frappe.db.commit()
                    allow.save(ignore_permissions=True)
                else:
                    allow = frappe.new_doc('Special Allowance')
                    # frappe.errprint(f"Creating Special Allowance for {emp_name}")
                    allow.employee = emp_name
                    allow.working_date = att.attendance_date
                    allow.amount = special_all
                    allow.save(ignore_permissions=True)
                    frappe.db.commit()


@frappe.whitelist()
def create_special_allow(fdate, tdate):
    special_all = 0
    attendance = frappe.get_all(
        "Attendance", {'employee_type': 'Staff','working_hours': ('>=', 20), 'attendance_date': ('between', (fdate, tdate))},
        ['attendance_date', 'out_time', 'employee']
    )
    
    if attendance:  
        for att in attendance:
            emp_name = att.employee
            frappe.errprint(f"Processing employee: {emp_name} on {att.attendance_date}")
            start_date = fdate
            end_date = add_days(tdate, 1)
            holiday_dates = get_holiday_dates_for_employee(att.employee, fdate, end_date)
            if not holiday_dates:
                holiday_dates = []

            query = """SELECT cast(start_date as char) FROM `tabShift Assignment` WHERE employee='%s' AND shift_type = 'WW' AND reason = '' AND start_date BETWEEN '%s' AND '%s'"""  % (att.employee, start_date, end_date)
            ww = frappe.db.sql(query, as_list=True)
            ww_list = list(chain(*ww))
            holiday_dates.extend(ww_list)
            day_before_holidays = []
            for holiday in holiday_dates:
                day_before_holidays.append(add_days(holiday, -1)) 
             
            day_of_week = att.attendance_date.weekday()
            if cstr(att.attendance_date) in holiday_dates and cstr(att.attendance_date) not in day_before_holidays:
                special_all = 2500
            elif cstr(att.attendance_date) in day_before_holidays and cstr(att.attendance_date) not in holiday_dates:
                special_all = 3000
            elif cstr(att.attendance_date) in day_before_holidays and cstr(att.attendance_date) in holiday_dates:
                special_all = 3000
            else:
                frappe.errprint(att.employee)
                frappe.errprint(day_of_week)
                if day_of_week in [0, 1, 2, 3, 4]:
                    special_all = 1000
                elif day_of_week == 5:
                    special_all = 3000 
                elif day_of_week == 6:
                    special_all = 2500
            if special_all>0:
                if frappe.db.exists("Special Allowance", {'working_date': att.attendance_date, 'employee': att.employee, 'docstatus': ['!=', 2]}):
                    # count += 1
                    allow = frappe.get_doc("Special Allowance", {'working_date': att.attendance_date, 'employee': att.employee, 'docstatus': ['!=', 2]})
                    allow.employee = emp_name
                    allow.working_date = att.attendance_date
                    allow.amount = special_all
                    frappe.db.commit()
                    allow.save(ignore_permissions=True)
                else:
                    allow = frappe.new_doc('Special Allowance')
                    # frappe.errprint(f"Creating Special Allowance for {emp_name}")
                    allow.employee = emp_name
                    allow.working_date = att.attendance_date
                    allow.amount = special_all
                    allow.save(ignore_permissions=True)
                    frappe.db.commit()


