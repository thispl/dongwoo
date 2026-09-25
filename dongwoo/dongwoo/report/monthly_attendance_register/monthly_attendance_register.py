# Copyright (c) 2024, TEAMPRO and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from functools import total_ordering
from itertools import count
import frappe
from frappe import permissions
from frappe.utils import cstr, cint, getdate, get_last_day, get_first_day, add_days,date_diff
from math import floor
from frappe import msgprint, _
from calendar import month, monthrange
from datetime import date, timedelta, datetime,time

status_map = {
    "Present": "P",
    "On Leave": "On Leave",
    "Work From Home": "WFH",
    'Half Day': 'HD',
    "Absent": "A",
    "Holiday": "HH",
    "Weekly Off": "WW",
    "Leave Without Pay": "LOP",
    "Casual Leave (CL)": "CL",
    "Earned Leave (EL)": "EL",
    "Special Leave": "SPL",
    "Sick Leave (SL)": "SL",
    "Medical Leave": 'MDL',
    "Privilege Leave": "PVL",
    "Compensatory Off": "C-OFF",
}

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_columns(filters):
    columns = [
        _("Employee ID") + ":Data/:150",
        _("Employee Name") + ":Data/:200",
        _('Employee Category') + ':Data:100',
        _("Department") + ":Data/:150",
        _("DOJ") + ":Date/:100",
        _("Status") + ":Data/:150",
    ]
    
    dates = get_dates(filters.from_date, filters.to_date)
    for date in dates:
        date = datetime.strptime(date, '%Y-%m-%d')
        columns.append(_(datetime.date(date).strftime('%d/%b')) + ":Data/:100")
    
    columns.extend([
        _("Present") + ":Data/:100",
        _('Half Day') + ':Data/:100',
        _('On Duty') + ':Data/:100',
        _("Absent") + ":Data/:100",
        _('Weekoff') + ':Data/:100',
        _('Holiday') + ':Data/:100',
        _('Paid Leaves') + ':Data/:150',
        _('LOP') + ':Data/:100',
        _('COFF') + ':Data/:100',
        _('OT') + ':Data/:100'
    ])
    
    return columns


def get_employees(filters):
    conditions = ''
    left_employees = []
    if filters.employee:
        conditions += "and employee = '%s' " % (filters.employee)
    if filters.employee_type:
        conditions += "and employee_type = '%s' " % (filters.employee_type)
    if filters.department:
        conditions += "and department = '%s' " % (filters.department)
    if filters.employee_type=='Contract Employee':
        if filters.contractor:
            conditions += "and contractor = '%s' " % (filters.contractor)
    employees = frappe.db.sql("""select name,employee_name,employee_category,department,date_of_joining,status,relieving_date from `tabEmployee` where status = 'Active' %s """ % (conditions), as_dict=True)
    left_employees = frappe.db.sql("""select name,employee_name,employee_category,department,date_of_joining,status,relieving_date from `tabEmployee` where status = 'Left' and relieving_date >= '%s' %s """ %(filters.from_date,conditions),as_dict=True)
    employees.extend(left_employees)
    return employees


def get_data(filters):
    data = []
    employees = get_employees(filters)
    dates = get_dates(filters.from_date, filters.to_date)
    attendance_data = frappe.get_all(
        "Attendance",{'attendance_date': ['in', dates], 'employee': ['in', [emp.name for emp in employees]]},["employee", "attendance_date", "status", "in_time", "out_time", "shift", "total_working_hours", 'session_from_time','session_to_time',
        "overtime_hours", "late_entry_time", "leave_type", "actual_shift","early_out_time","site", "late_entry", "early_exit",'from_time','to_time','on_duty_application']
    )
    # shift_data = frappe.get_all(
    #     "Shift Assignment",
    #     filters={'start_date': ['in', dates], 'employee': ['in', [emp.name for emp in employees]]},
    #     fields=["employee", "start_date", "shift_type"]
    # )

    for emp in employees:
        row1 = [emp.name, emp.employee_name, emp.employee_category, emp.department, emp.date_of_joining, "Status"]
        row2 = ["", "", "", "", "", "In Time"]
        row3 = ["", "", "", "", "", "Out Time"]
        row4 = ["", "", "", "", "", "Shift"]
        row5 = ["", "", "", "", "", "TWH"]
        row6 = ["", "", "", "", "", "OT"]
        row7 = ["", "", "", "", "", "Late Entry"]
        row8 = ["", "", "", "", "", "Early Out"]
        row9 = ["", "", "", "", "", "Site"]
        total_present = total_half_day = total_absent = total_holiday = total_weekoff = total_ot = total_od = total_lop = total_paid_leave = total_combo_off = 0
        emp_attendance = [att for att in attendance_data if att['employee'] == emp.name]
        for date in dates:
            att = None
            for attendance in emp_attendance:
                if isinstance(date, str):
                    date = datetime.strptime(date, '%Y-%m-%d').date()  # Convert string date to datetime.date if needed
                if isinstance(attendance['attendance_date'], str):
                    attendance['attendance_date'] = datetime.strptime(attendance['attendance_date'], '%Y-%m-%d').date()

                if attendance['attendance_date'] == date:
                    att = attendance
                    break
            
            if emp.status=='Active' or (emp.status=='Left' and emp.relieving_date >= getdate(date)):
                if att:
                    leave = status_map.get(att['leave_type'], '')
                    if att['overtime_hours'] and att['overtime_hours']>0:
                        total_ot+=att['overtime_hours']
                    if att['status'] == "Present":
                        hh = check_holiday(date, emp.name)
                        if hh == 'WW':
                            row1.append('WW/P')
                            total_present += 1
                        elif hh == 'HH':
                            row1.append('HH/P')
                            total_present += 1
                        elif att['actual_shift'] == 'WW':
                            row1.append('WW/P')
                            total_present += 1
                        else:
                            row1.append('P')
                            total_present += 1
                        
                    elif att['status'] == "Absent":
                        hh = check_holiday(date, emp.name)
                        if hh == 'WW':
                            row1.append('WW/A')
                            total_weekoff += 1
                        elif hh == 'HH':
                            row1.append('HH/A')
                            total_holiday += 1
                        elif att['actual_shift'] == 'WW':
                            row1.append('WW')
                            total_weekoff += 1
                        else:
                            row1.append("A")
                            total_absent += 1
                        
                    elif att['status'] == "Half Day":
                        hh = check_holiday(date, emp.name)
                        if hh == 'WW':
                            row1.append('WW/HD')
                            total_weekoff+= 0.5
                            total_half_day += 0.5
                        elif hh == 'HH':
                            row1.append('HH/HD')
                            total_holiday += 0.5
                            total_half_day += 0.5
                        elif att['actual_shift'] == 'WW':
                            row1.append('WW/HD')
                            total_weekoff+= 0.5
                            total_half_day += 0.5
                        else:
                            row1.append("HD")
                            total_half_day += 0.5
                            total_absent += 0.5
                        
                    elif att['status'] == "Work From Home":
                        row1.append("WFH")
                        total_present += 1
                    elif att['status'] == "On Leave":
                        row1.append(leave)
                        if leave == "LOP":
                            total_lop += 1
                        elif leave in ["CL", "SL", "SPL", "EL", "MDL", "C-OFF"]:
                            total_paid_leave += 1
                        if leave=='C-OFF':
                            total_combo_off+=1
                    intime=''
                    outtime=''
                    if att['on_duty_application']:
                        session = frappe.db.get_value("On Duty Application", {'name': att['on_duty_application']}, 'session')

                        if session != 'Flexible':
                            session_from_time = (datetime.min + att['session_from_time']).time() if isinstance(att['session_from_time'], timedelta) else att['session_from_time']
                            session_to_time = (datetime.min + att['session_to_time']).time() if isinstance(att['session_to_time'], timedelta) else att['session_to_time']
                            if att['in_time']:
                                if att['in_time'].time() < session_from_time:
                                    intime = att['in_time'].time() 
                                else:
                                    intime=session_from_time
                            else:
                                intime=''
                            if att['out_time']:
                                if att['out_time'] and att['out_time'].time() > session_to_time:
                                    outtime = att['out_time'].time()
                                else:
                                    outtime=session_to_time
                            else:
                                outtime=''

                        else:
                            if att['in_time'] is not None:
                                if att['from_time'] is not None:
                                    if att['in_time'].time() < att['from_time'].time():
                                        intime = att['in_time'].time() 
                                    else:
                                        intime=att['from_time'].time()
                                else:
                                    intime = att['in_time'].time() 
                            else:
                                intime=''
                            if att['out_time'] is not None:
                                if att['to_time'] is not None:
                                    if att['out_time'] and att['out_time'].time() > att['to_time'].time():
                                        outtime = att['out_time'].time()
                                    else:
                                        outtime=att['to_time'].time()
                                else:
                                    outtime = att['out_time'].time()
                            else:
                                outtime=''
                    else:
                        if att['in_time'] is not None:
                            intime = att['in_time'].time() 
                        else:
                            intime=''
                        if att['out_time'] is not None:
                            outtime = att['out_time'].time() 
                        else:
                            outtime=''
                        # intime = att['in_time'].time() if att['in_time'] else ''
                        # outtime = att['out_time'].time() if att['out_time'] else ''

                    row2.append(intime if intime else '-')
                    row3.append(outtime if outtime else '-')
                    if intime and outtime:
                        row4.append(att['shift'] if att['shift'] else "-")
                        row5.append(att['total_working_hours'] if att['total_working_hours'] else "-")
                        row6.append(att['overtime_hours'] if att['overtime_hours'] else "-")
                        row7.append(str(att['late_entry_time']) if att['late_entry'] else '-')
                        row8.append(str(att['early_out_time']) if att['early_exit'] else '-')
                        row9.append(att['site'] if att['site'] else '-')
                    else:
                        row4.append("-")
                        row5.append("-")
                        row6.append("-")
                        row7.append('-')
                        row8.append('-')
                        row9.append(att['site'] if att['site'] else '-')
                else:
                    hh = check_holiday(date, emp.name)
                    if hh:
                        if hh=='HH':
                            total_holiday += 1
                        else:
                            total_weekoff+= 1
                        row1.append(hh)
                        row2.append('-')
                        row3.append('-')
                        row4.append('-')
                        row5.append('-')
                        row6.append('-')
                        row7.append('-')
                        row8.append('-')
                        row9.append('-')
                    else:
                        row1.append("-")
                        row2.append('-')
                        row3.append('-')
                        row4.append('-')
                        row5.append('-')
                        row6.append('-')
                        row7.append('-')
                        row8.append('-')
                        row9.append('-')
            else:
                row1.append("-")
                row2.append('-')
                row3.append('-')
                row4.append('-')
                row5.append('-')
                row6.append('-')
                row7.append('-')
                row8.append('-')
                row9.append('-')
        row1.extend([total_present, total_half_day, total_od, total_absent, total_weekoff, total_holiday, total_paid_leave, total_lop, total_combo_off, total_ot])
        row2.extend(['-'] * 12)
        row3.extend(['-'] * 12)
        row4.extend(['-'] * 12)
        row5.extend(['-'] * 12)
        row6.extend(['-'] * 12)
        row7.extend(['-'] * 12)
        row8.extend(['-'] * 12)
        row9.extend(['-'] * 12)
        data.append(row1)
        data.append(row2)
        data.append(row3)
        data.append(row5)
        data.append(row4)
        data.append(row6)
        data.append(row7)
        data.append(row8)
        data.append(row9)

    return data

def get_dates(from_date, to_date):
    no_of_days = date_diff(add_days(to_date, 1), from_date)
    return [add_days(from_date, i) for i in range(0, no_of_days)]

def check_holiday(date, emp):
    holiday_list = frappe.db.get_value('Employee', {'name': emp}, 'holiday_list')
    holiday = frappe.db.sql("""
        SELECT `tabHoliday`.holiday_date, `tabHoliday`.weekly_off 
        FROM `tabHoliday List` 
        LEFT JOIN `tabHoliday` 
        ON `tabHoliday`.parent = `tabHoliday List`.name 
        WHERE `tabHoliday List`.name = %s AND holiday_date = %s
    """, (holiday_list, date), as_dict=True)
    
    doj = frappe.db.get_value("Employee", {'name': emp}, "date_of_joining")
    if frappe.db.exists('Shift Assignment', {'start_date': date, 'employee': emp, 'shift_type': 'WW', 'docstatus': 1}):
        return "WW"
    elif holiday:
        if doj <= holiday[0].holiday_date:
            return "WW" if holiday[0].weekly_off == 1 else "HH"
    return '-'

@frappe.whitelist()
def get_to_date(from_date):
    return get_last_day(from_date)
