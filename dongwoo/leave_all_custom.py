
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



#returns the total allocated leave of an employee from the start date and for the leave type to display it in Print Format
@frappe.whitelist()
def get_total_leaves_allocated(start_date, employee, leave_type):
    year = getdate(start_date).year    
    total_leaves = frappe.db.sql("""
        SELECT SUM(total_leaves_allocated) AS total_allocated
        FROM `tabLeave Allocation`
        WHERE docstatus = 1 
        AND employee = %s 
        AND leave_type = %s
        AND YEAR(from_date) = %s 
        AND YEAR(to_date) = %s
    """, (employee, leave_type, year, year), as_dict=True)    
    return total_leaves[0].get('total_allocated', 0) if total_leaves else 0


import frappe
from frappe import db
#returns the total approved leaves of an employee from the start date and for the leave type to display it in Print Format
@frappe.whitelist()
def get_approved_leave_days(start_date, employee, leave_type):
    start_date_obj = frappe.utils.getdate(start_date)
    start_month = start_date_obj.month
    start_year = start_date_obj.year
    leave_days = db.sql("""
        SELECT SUM(total_leave_days) 
        FROM `tabLeave Application` 
        WHERE docstatus = 1 
        AND workflow_state = 'Approved' 
        AND employee = %s 
        AND leave_type = %s
        AND MONTH(from_date) = %s 
        AND YEAR(from_date) = %s 
        AND MONTH(to_date) = %s 
        AND YEAR(to_date) = %s
    """, (employee, leave_type, start_month, start_year, start_month, start_year), as_dict=True)

    return leave_days[0].get('SUM(total_leave_days)') or 0


@frappe.whitelist()
def get_balance_leaves(start_date, employee, leave_type):
    balance=0
    opening=get_total_leaves_allocated(start_date, employee, leave_type)
    availed=get_approved_leave_days(start_date, employee, leave_type)
    balance=opening-availed
    if balance<0:
        balance=0
    return balance






#returns the holiday count of that period for the employee 
@frappe.whitelist()
def count_holidays(employee,start_date,end_date):
    # Fetch the holiday list from the employee document
    # employee='20080113'
    # start_date='2024-10-01'
    # end_date='2024-10-30'
    employee_doc = frappe.get_doc("Employee", employee)
    holiday_list = employee_doc.holiday_list

    start_date = getdate(start_date)
    end_date = getdate(end_date)

    holidays = frappe.get_all('Holiday',
        filters={
            'parent': holiday_list,
            'holiday_date': ['between', (start_date, end_date)],
            'weekly_off': 0  
        },
        fields=['holiday_date']
    )

    return len(holidays)



@frappe.whitelist()
def cl_monthly_leave_allocations1():
    print("Hi")
    today = date.today()

    # if today.day != 1:
    #     return

    first_day = today.replace(day=1)
    last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1])
    print(first_day)
    print(last_day)

    # employees = [{
    #     "name": "4231001",
    #     "employee_name": "DURAI P"
    # }]
    employees = frappe.db.sql("""
        SELECT name, employee_name, date_of_joining, employee_type
        FROM `tabEmployee`
        WHERE status = 'Active'
        AND employee_type IN ('NAPS', 'GET', 'D . Trainee')
    """, as_dict=True)

    for employee in employees:
      
        exists = frappe.db.exists("Leave Allocation", {
            "employee": employee["name"],
            "leave_type": "Casual Leave (CL)",
            "from_date": first_day,
            "to_date": last_day,
            "docstatus":["!=",2]
        })
        if not exists:
            la = frappe.new_doc("Leave Allocation")
            la.employee = employee["name"]
            la.leave_type = "Casual Leave (CL)"
            la.new_leaves_allocated = 1
            la.from_date = first_day
            la.to_date = last_day
            # la.save(ignore_permissions=True)
            # la.submit()
            

@frappe.whitelist()
def create_cl_leave():
    job = frappe.db.exists('Scheduled Job Type', 'cl_monthly_leave_allocations1')
    if not job:
        att = frappe.new_doc("Scheduled Job Type")
        att.update({
            "method": 'dongwoo.leave_all_custom.cl_monthly_leave_allocations1',
            "frequency": 'Monthly',
            "cron_format": "0 0 1 * *"
        })
        att.save(ignore_permissions=True)




