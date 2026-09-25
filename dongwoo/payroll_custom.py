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

# Late In and Early Out Penalty creation
@frappe.whitelist()
def attendance_calc(from_date,to_date):
    
    late_count=0
    late_count1=0
    ad=''
    
    employees = frappe.get_all("Employee", {"status": "Active"}, ["*"])
    
    for emp in employees:
        shifts = frappe.get_all('Shift Type', ['*'])
        
        for shift in shifts:
            late_count = frappe.db.sql("""
                SELECT COUNT(name) AS count
                FROM `tabAttendance`
                WHERE
                    employee = %s AND shift = %s
                    AND time(in_time) > %s
                    AND attendance_date BETWEEN %s AND %s
            """, (emp.name, shift.name, shift.start_time, from_date, to_date), as_dict=True)[0].count or 0

            print(f"Employee: {emp.name}, Shift: {shift.name}, shift:{shift.start_time} Late Count: {late_count}")

            late_count1 = frappe.db.sql("""
                SELECT COUNT(name) AS count
                FROM `tabAttendance`
                WHERE
                    employee = %s AND shift = %s
                    AND time(out_time) < %s
                    AND attendance_date BETWEEN %s AND %s
            """, (emp.name, shift.name, shift.start_time, from_date, to_date), as_dict=True)[0].count or 0

            print(f"Employee: {emp.name}, Shift: {shift.name}, shift:{shift.start_time} Late Count: {late_count}")
            if late_count > 0 or late_count1 > 0:
                print('hiii')

                if not frappe.db.exists("Late In and Early Out Penalty", {"employee": emp.name,"from_date":from_date,"to_date":to_date}):
                    ad = frappe.new_doc('Late In And Early Out Penalty')
                    ad.employee = emp.name
                    frappe.errprint(ad.employee)
                    ad.employee_name=emp.first_name
                    ad.designation=emp.designation
                    ad.from_date=from_date
                    ad.to_date=to_date
                    ad.total_no_of_late_in=late_count
                    ad.total_no_of_early_out=late_count1
                    total=late_count+late_count1
                    ad.total_no_of_late_deductions_day=total
                    if total > 0:
                        late=total/2
                        ad.late_penalty_day=late
                    leave=frappe.get_all('Leave Allocation',{'employee_name':emp.first_name},['*'])
                    for j in leave:
                        if j.leave_type not in ["Compensatory Off",'Sick Leave']:
                            ad.append(
                                "leave_deduction",
                                {
                                    "leave_type": j.leave_type,
                                    "leave_balance": j.new_leaves_allocated,
            },
        )

                    
                    frappe.db.commit()
                    ad.save(ignore_permissions=True)
                    frappe.errprint("Late Penalty Created via Additional Salary")
                else:
                    ad = frappe.get_doc('Late In And Early Out Penalty',{"employee": emp.name,"from_date":from_date,"to_date":to_date})
                    ad.employee = emp.name
                    ad.employee_name=emp.first_name
                    ad.designation=emp.designation
                    ad.from_date=from_date
                    ad.to_date=to_date
                    ad.total_no_of_late_in=late_count+ad.total_no_of_late_in
                    ad.total_no_of_early_out=late_count1+ad.total_no_of_early_out
                    total=late_count+late_count1
                    ad.total_no_of_late_deductions_day=total+ad.total_no_of_late_deductions_day
                    if total > 0:
                        late=total/2
                        ad.late_penalty_day=late+ad.late_penalty_day
                    frappe.db.commit()
                    ad.save(ignore_permissions=True)
                    frappe.errprint("Late Penalty Created via Additional Salary")
                # return 'ok'

