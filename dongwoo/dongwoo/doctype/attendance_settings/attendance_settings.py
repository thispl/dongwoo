# Copyright (c) 2023, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import time_diff_in_hours 
from datetime import datetime
from frappe.utils.data import today, add_days, add_years
from dateutil.relativedelta import relativedelta
from datetime import timedelta, time,date
from itertools import chain
from frappe.utils import time_diff_in_hours, formatdate, get_first_day,get_last_day, nowdate, now_datetime
from frappe.model.document import Document
from hrms.hr.utils import get_holiday_dates_for_employee
from hrms.hr.utils import get_holidays_for_employee
from frappe.utils import cstr, add_days, date_diff,format_datetime,ceil,flt
from dongwoo.mark_attendance import check_holiday
class AttendanceSettings(Document):
    pass
@frappe.whitelist()
def process_shift_allowance(from_date,to_date):
    frappe.msgprint("Shift allowance updating in background.Kindly check after few minutes.")
    frappe.enqueue(
        process_shift_allowance_method, 
        queue="default",
        timeout=36000,
        is_async=True, 
        now=False, 
        job_name='Shift Allowance',
        enqueue_after_commit=False,
        from_date=from_date,
        to_date=to_date
    )
@frappe.whitelist()
def process_shift_allowance_with_emp(from_date,to_date,emp):
    # process_shift_allowance_emp(from_date,to_date,emp)
    frappe.msgprint("Shift allowance updating in background.Kindly check after few minutes.")
    frappe.enqueue(
        process_shift_allowance_emp, 
        queue="default",
        timeout=36000,
        is_async=True, 
        now=False, 
        job_name='Shift Allowance',
        enqueue_after_commit=False,
        from_date=from_date,
        to_date=to_date,
		emp=emp
    )
@frappe.whitelist()
def process_shift_allowance_with_employee_type(from_date,to_date,employee_type):
    frappe.msgprint("Shift allowance updating in background.Kindly check after few minutes.")
    frappe.enqueue(
        process_shift_allowance_employee_type, 
        queue="default",
        timeout=36000,
        is_async=True, 
        now=False, 
        job_name='Shift Allowance',
        enqueue_after_commit=False,
        from_date=from_date,
        to_date=to_date,
		employee_type=employee_type
    )
@frappe.whitelist()
def process_shift_allowance_method(from_date,to_date):
    attendance = frappe.db.get_all('Attendance',{'attendance_date':('between',(from_date,to_date)),'docstatus':('!=','2')},['*'])  
    for att in attendance:
        att=frappe.get_doc("Attendance",att.name)
        if att.employee_type in ["Worker" ,"D . Trainee" ,"Contract Employee","GET"]:
            hh=check_holiday(att.attendance_date,att.employee)
            ot_wh=0
            tot_wh=0
            if att.shift:
                if ((not att.in_time or not att.out_time) or (not att.in_time and not att.out_time)) and att.attendance_upload:
                    if att.shift=='B':
                        frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                        frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                    elif att.shift=='C':
                        frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                        frappe.db.set_value("Attendance",att.name,'b_allowance',0)
                    else:
                        frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                        frappe.db.set_value("Attendance",att.name,'b_allowance',0)
                else:
                    if att.shift=='B':
                        act_time=frappe.db.get_value("Shift Type",{"name":att.shift},['_total_working_hours'])
                        act_hrs = 4.0
                        shift_st = frappe.get_value("Shift Type", {'name': att.shift}, ['start_time'])
                        shift_start_time = datetime.strptime(str(shift_st), '%H:%M:%S').time()
                        shift_endt = frappe.get_value("Shift Type", {'name': att.shift}, ['end_time'])
                        shift_end_time = datetime.strptime(str(shift_endt), '%H:%M:%S').time()
                        shift_date = add_days(att.attendance_date,+1) 	
                        shift_end_datetime = datetime.combine(shift_date, shift_end_time)
                        shift_start_datetime = datetime.combine(att.attendance_date, shift_start_time)
                        if att.in_time and att.out_time:
                            in_time = att.in_time
                            out_time = att.out_time
                            if isinstance(in_time, str):
                                in_time = datetime.strptime(in_time, '%Y-%m-%d %H:%M:%S')
                            if isinstance(out_time, str):
                                out_time = datetime.strptime(out_time, '%Y-%m-%d %H:%M:%S')
                            if in_time > shift_start_datetime:
                                if out_time > shift_end_datetime:
                                    tot_wh=time_diff_in_hours(shift_end_datetime, in_time)
                                else:
                                    tot_wh=time_diff_in_hours(out_time, in_time)
                            else:
                                if out_time > shift_end_datetime:
                                    tot_wh=time_diff_in_hours(shift_end_datetime, shift_start_datetime)
                                else:
                                    tot_wh=time_diff_in_hours(out_time, shift_start_datetime)
                        if tot_wh < act_hrs:
                            if att.att_permission:
                                perm=frappe.db.get_value("Permission",{'name':att.att_permission},['total_time'])
                                tot_wh=int(tot_wh)+int(perm)
                        if not hh:	
                            if att.attendance_upload:
                                if att.status=='Present' and att.overtime_hours==0:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                if att.overtime_hours>0:
                                    if att.overtime_hours>=7:
                                        if att.status=='Present':
                                            frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                        frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                    else:
                                        if att.status=='Present':
                                            frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                        frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                            else:
                                if tot_wh >= act_hrs and att.overtime_hours<7:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                elif tot_wh >= act_hrs and att.overtime_hours>=7:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                elif tot_wh < act_hrs and att.overtime_hours>=7:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',0)
                                else:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',0)
                        else:
                            if att.attendance_upload:
                                if att.status=='Present' and att.overtime_hours==0:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                if att.overtime_hours>0:
                                    if att.overtime_hours < 7:
                                        if att.status=='Present':
                                            frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                        frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                    elif att.overtime_hours >= 15:
                                        frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                        frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                    elif att.overtime_hours >= 7 and att.overtime_hours < 15:
                                        frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                        frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                            else:
                                if att.overtime_hours < 7:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',0)
                                elif att.overtime_hours >= 15:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                elif att.overtime_hours >= 7 and att.overtime_hours < 15:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                    if att.shift=='C':
                        act_time=frappe.db.get_value("Shift Type",{"name":att.shift},['_total_working_hours'])
                        # frappe.errprint(act_time)
                        act_hrs=4.0
                        shift_st = frappe.get_value("Shift Type", {'name': att.shift}, ['start_time'])
                        shift_start_time = datetime.strptime(str(shift_st), '%H:%M:%S').time()
                        shift_endt = frappe.get_value("Shift Type", {'name': att.shift}, ['end_time'])
                        shift_end_time = datetime.strptime(str(shift_endt), '%H:%M:%S').time()
                        shift_date = add_days(att.attendance_date,+1) 	
                        shift_end_datetime = datetime.combine(shift_date, shift_end_time)
                        shift_start_datetime = datetime.combine(shift_date, shift_start_time)
                        if att.in_time and att.out_time:
                            in_time = att.in_time
                            out_time = att.out_time
                            if isinstance(in_time, str):
                                in_time = datetime.strptime(in_time, '%Y-%m-%d %H:%M:%S')
                            if isinstance(out_time, str):
                                out_time = datetime.strptime(out_time, '%Y-%m-%d %H:%M:%S')
                            if in_time > shift_start_datetime:
                                if out_time > shift_end_datetime:
                                    tot_wh=time_diff_in_hours(shift_end_datetime, in_time)
                                else:
                                    tot_wh=time_diff_in_hours(out_time, in_time)
                            else:
                                if out_time > shift_end_datetime:
                                    tot_wh=time_diff_in_hours(shift_end_datetime, shift_start_datetime)
                                else:
                                    tot_wh=time_diff_in_hours(out_time, shift_start_datetime)
                        if tot_wh < act_hrs:
                            if att.att_permission:
                                perm=frappe.db.get_value("Permission",{'name':att.att_permission},['total_time'])
                                tot_wh=int(tot_wh)+int(perm)
                        if att.attendance_upload:
                            if att.status=='Present' and att.overtime_hours==0:
                                frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                frappe.db.set_value("Attendance",att.name,'b_allowance',0)
                            if att.overtime_hours>0:
                                if not hh:
                                    if att.overtime_hours >= 15:
                                        if att.status=='Present':
                                            frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                        frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                    else: 
                                        if att.status=='Present':
                                            frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                        frappe.db.set_value("Attendance",att.name,'b_allowance',0)
                                else:
                                    if att.overtime_hours >= 23:
                                        if att.status=='Present':
                                            frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                        frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                    else: 
                                        if att.status=='Present':
                                            frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                        frappe.db.set_value("Attendance",att.name,'b_allowance',0)
                        else:
                            if not hh:
                                if tot_wh >= act_hrs and att.overtime_hours >= 15:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',1)         
                                elif tot_wh >= act_hrs and att.overtime_hours < 15:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',0)             
                                elif tot_wh < act_hrs and att.overtime_hours >= 15:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                else: 
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',0)
                            else:
                                if tot_wh >= act_hrs and att.overtime_hours >= 23:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                elif tot_wh >= act_hrs and att.overtime_hours < 23:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',0)
                                elif tot_wh < act_hrs and att.overtime_hours >= 23:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                else: 
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',0)
                    
                    if att.shift=='A':
                        if not hh:	
                            if att.overtime_hours>=8 and att.overtime_hours<15:
                                frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                            elif att.overtime_hours>=15:
                                frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                            else:
                                frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                frappe.db.set_value("Attendance",att.name,'b_allowance',0)
                        else:
                            if att.overtime_hours >= 15 and att.overtime_hours < 23:
                                frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                            elif att.overtime_hours >= 23:
                                frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                            else:
                                frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                frappe.db.set_value("Attendance",att.name,'b_allowance',0)

        if att.employee_type == "NAPS":
            if att.shift and att.attendance_upload:
                if att.shift == "B":
                    frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                    frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                elif att.shift =="C":
                    frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                    frappe.db.set_value("Attendance",att.name,'b_allowance',0)  
                else:
                    frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                    frappe.db.set_value("Attendance",att.name,'b_allowance',0)
            else:
                frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                frappe.db.set_value("Attendance",att.name,'b_allowance',0)                     
                
@frappe.whitelist()
def process_shift_allowance_emp(from_date,to_date,emp):
    attendance = frappe.db.get_all('Attendance',{'attendance_date':('between',(from_date,to_date)),'employee':emp,'docstatus':('!=','2')},['*'])  
    for att in attendance:
        att=frappe.get_doc("Attendance",att.name)
        if att.employee_type in ["Worker" ,"D . Trainee" ,"Contract Employee","GET"]:
            hh=check_holiday(att.attendance_date,att.employee)
            ot_wh=0
            tot_wh=0
            if att.shift:
                if ((not att.in_time or not att.out_time) or (not att.in_time and not att.out_time)) and att.attendance_upload:
                    if att.shift=='B':
                        # if att.overtime_hours >= "7.000":
                        #     frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                        #     frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                        # else:    
                        frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                        frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                    elif att.shift=='C':
                        frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                        frappe.db.set_value("Attendance",att.name,'b_allowance',0)
                    # elif att.shift =="A":
                    #     if att.overtime_hours >= "8.000":
                    #         frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                    #         frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                    #     else:    
                    #         frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                    #         frappe.db.set_value("Attendance",att.name,'b_allowance',0)
                    else:
                        frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                        frappe.db.set_value("Attendance",att.name,'b_allowance',0)
                else:
                    if att.shift=='B':
                        act_time=frappe.db.get_value("Shift Type",{"name":att.shift},['_total_working_hours'])
                        act_hrs = 4.0
                        shift_st = frappe.get_value("Shift Type", {'name': att.shift}, ['start_time'])
                        shift_start_time = datetime.strptime(str(shift_st), '%H:%M:%S').time()
                        shift_endt = frappe.get_value("Shift Type", {'name': att.shift}, ['end_time'])
                        shift_end_time = datetime.strptime(str(shift_endt), '%H:%M:%S').time()
                        shift_date = add_days(att.attendance_date,+1) 	
                        shift_end_datetime = datetime.combine(shift_date, shift_end_time)
                        shift_start_datetime = datetime.combine(att.attendance_date, shift_start_time)
                        if att.in_time and att.out_time:
                            in_time = att.in_time
                            out_time = att.out_time
                            if isinstance(in_time, str):
                                in_time = datetime.strptime(in_time, '%Y-%m-%d %H:%M:%S')
                            if isinstance(out_time, str):
                                out_time = datetime.strptime(out_time, '%Y-%m-%d %H:%M:%S')
                            if in_time > shift_start_datetime:
                                if out_time > shift_end_datetime:
                                    tot_wh=time_diff_in_hours(shift_end_datetime, in_time)
                                else:
                                    tot_wh=time_diff_in_hours(out_time, in_time)
                            else:
                                if out_time > shift_end_datetime:
                                    tot_wh=time_diff_in_hours(shift_end_datetime, shift_start_datetime)
                                else:
                                    tot_wh=time_diff_in_hours(out_time, shift_start_datetime)
                        if tot_wh < act_hrs:
                            if att.att_permission:
                                perm=frappe.db.get_value("Permission",{'name':att.att_permission},['total_time'])
                                tot_wh=int(tot_wh)+int(perm)
                        if not hh:	
                            if att.attendance_upload:
                                frappe.errprint('1')
                                if att.status=='Present' and att.overtime_hours==0:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                if att.overtime_hours>0:
                                    if att.overtime_hours>=7:
                                        frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                        if att.status=='Present':
                                            frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                        
                                    else:
                                        if att.status=='Present':
                                            frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                        frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                            else:
                                if tot_wh >= act_hrs and att.overtime_hours<7:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                elif tot_wh >= act_hrs and att.overtime_hours>=7:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                elif tot_wh < act_hrs and att.overtime_hours>=7:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',0)
                                else:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',0)
                        else:
                            if att.attendance_upload:
                                if att.status=='Present' and att.overtime_hours==0:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                if att.overtime_hours>0:
                                    if att.overtime_hours < 7:
                                        frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                        if att.status=='Present':
                                            frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                    elif att.overtime_hours >= 15:
                                        frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                        frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                    elif att.overtime_hours >= 7 and att.overtime_hours < 15:
                                        frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                        frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                            else:
                                if att.overtime_hours < 7:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',0)
                                elif att.overtime_hours >= 15:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                elif att.overtime_hours >= 7 and att.overtime_hours < 15:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                    if att.shift=='C':
                        act_time=frappe.db.get_value("Shift Type",{"name":att.shift},['_total_working_hours'])
                        # frappe.errprint(act_time)
                        act_hrs=4.0
                        shift_st = frappe.get_value("Shift Type", {'name': att.shift}, ['start_time'])
                        shift_start_time = datetime.strptime(str(shift_st), '%H:%M:%S').time()
                        shift_endt = frappe.get_value("Shift Type", {'name': att.shift}, ['end_time'])
                        shift_end_time = datetime.strptime(str(shift_endt), '%H:%M:%S').time()
                        shift_date = add_days(att.attendance_date,+1) 	
                        shift_end_datetime = datetime.combine(shift_date, shift_end_time)
                        shift_start_datetime = datetime.combine(shift_date, shift_start_time)
                        if att.in_time and att.out_time:
                            in_time = att.in_time
                            out_time = att.out_time
                            if isinstance(in_time, str):
                                in_time = datetime.strptime(in_time, '%Y-%m-%d %H:%M:%S')
                            if isinstance(out_time, str):
                                out_time = datetime.strptime(out_time, '%Y-%m-%d %H:%M:%S')
                            if in_time > shift_start_datetime:
                                if out_time > shift_end_datetime:
                                    tot_wh=time_diff_in_hours(shift_end_datetime, in_time)
                                else:
                                    tot_wh=time_diff_in_hours(out_time, in_time)
                            else:
                                if out_time > shift_end_datetime:
                                    tot_wh=time_diff_in_hours(shift_end_datetime, shift_start_datetime)
                                else:
                                    tot_wh=time_diff_in_hours(out_time, shift_start_datetime)
                        if tot_wh < act_hrs:
                            if att.att_permission:
                                perm=frappe.db.get_value("Permission",{'name':att.att_permission},['total_time'])
                                tot_wh=int(tot_wh)+int(perm)
                        if att.attendance_upload:
                            if att.status=='Present' and att.overtime_hours==0:
                                frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                frappe.db.set_value("Attendance",att.name,'b_allowance',0)
                            if att.overtime_hours>0:
                                if not hh:
                                    if att.overtime_hours >= 15:
                                        frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                        if att.status=='Present':
                                            frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                    else: 
                                        frappe.db.set_value("Attendance",att.name,'b_allowance',0)
                                        if att.status=='Present':
                                            frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                else:
                                    if att.overtime_hours >= 23:
                                        if att.status=='Present':
                                            frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                        frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                    else: 
                                        if att.status=='Present':
                                            frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                        frappe.db.set_value("Attendance",att.name,'b_allowance',0)
                        else:
                            if not hh:
                                if tot_wh >= act_hrs and att.overtime_hours >= 15:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',1)         
                                elif tot_wh >= act_hrs and att.overtime_hours < 15:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',0)             
                                elif tot_wh < act_hrs and att.overtime_hours >= 15:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                else: 
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',0)
                            else:
                                if tot_wh >= act_hrs and att.overtime_hours >= 23:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                elif tot_wh >= act_hrs and att.overtime_hours < 23:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',0)
                                elif tot_wh < act_hrs and att.overtime_hours >= 23:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                else: 
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',0)
                    
                    if att.shift=='A':
                        if not hh:	
                            if att.overtime_hours>=8 and att.overtime_hours<15:
                                frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                            elif att.overtime_hours>=15:
                                frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                            else:
                                frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                frappe.db.set_value("Attendance",att.name,'b_allowance',0)
                        else:
                            if att.overtime_hours >= 15 and att.overtime_hours < 23:
                                frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                            elif att.overtime_hours >= 23:
                                frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                            else:
                                frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                frappe.db.set_value("Attendance",att.name,'b_allowance',0)

        if att.employee_type == "NAPS":
            if att.shift and att.attendance_upload:
                if att.shift == "B":
                    frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                    frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                elif att.shift =="C":
                    frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                    frappe.db.set_value("Attendance",att.name,'b_allowance',0)  
                else:
                    frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                    frappe.db.set_value("Attendance",att.name,'b_allowance',0)
            else:
                frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                frappe.db.set_value("Attendance",att.name,'b_allowance',0)                         
            


@frappe.whitelist()
def process_shift_allowance_employee_type(from_date,to_date,employee_type):
    attendance = frappe.db.get_all('Attendance',{'attendance_date':('between',(from_date,to_date)),'employee_type':employee_type,'docstatus':('!=','2')},['*'])  
    for att in attendance:
        att=frappe.get_doc("Attendance",att.name)
        if att.employee_type in ["Worker" ,"D . Trainee" ,"Contract Employee","GET"]:
            hh=check_holiday(att.attendance_date,att.employee)
            ot_wh=0
            tot_wh=0
            
            if att.shift:
                if ((not att.in_time or not att.out_time) or (not att.in_time and not att.out_time)) and att.attendance_upload:
                    if att.shift=='B':
                        frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                        frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                    elif att.shift=='C':
                        frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                        frappe.db.set_value("Attendance",att.name,'b_allowance',0)
                    else:
                        frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                        frappe.db.set_value("Attendance",att.name,'b_allowance',0)
                else:
                    if att.shift=='B':
                        act_time=frappe.db.get_value("Shift Type",{"name":att.shift},['_total_working_hours'])
                        act_hrs = 4.0
                        shift_st = frappe.get_value("Shift Type", {'name': att.shift}, ['start_time'])
                        shift_start_time = datetime.strptime(str(shift_st), '%H:%M:%S').time()
                        shift_endt = frappe.get_value("Shift Type", {'name': att.shift}, ['end_time'])
                        shift_end_time = datetime.strptime(str(shift_endt), '%H:%M:%S').time()
                        shift_date = add_days(att.attendance_date,+1) 	
                        shift_end_datetime = datetime.combine(shift_date, shift_end_time)
                        shift_start_datetime = datetime.combine(att.attendance_date, shift_start_time)
                        if att.in_time and att.out_time:
                            in_time = att.in_time
                            out_time = att.out_time
                            if isinstance(in_time, str):
                                in_time = datetime.strptime(in_time, '%Y-%m-%d %H:%M:%S')
                            if isinstance(out_time, str):
                                out_time = datetime.strptime(out_time, '%Y-%m-%d %H:%M:%S')
                            if in_time > shift_start_datetime:
                                if out_time > shift_end_datetime:
                                    tot_wh=time_diff_in_hours(shift_end_datetime, in_time)
                                else:
                                    tot_wh=time_diff_in_hours(out_time, in_time)
                            else:
                                if out_time > shift_end_datetime:
                                    tot_wh=time_diff_in_hours(shift_end_datetime, shift_start_datetime)
                                else:
                                    tot_wh=time_diff_in_hours(out_time, shift_start_datetime)
                        if tot_wh < act_hrs:
                            if att.att_permission:
                                perm=frappe.db.get_value("Permission",{'name':att.att_permission},['total_time'])
                                tot_wh=int(tot_wh)+int(perm)
                        if not hh:	
                            if att.attendance_upload:
                                if att.status=='Present' and att.overtime_hours==0:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                if att.overtime_hours>0:
                                    if att.overtime_hours>=7:
                                        if att.status=='Present':
                                            frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                        frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                    else:
                                        if att.status=='Present':
                                            frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                        frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                            else:
                                if tot_wh >= act_hrs and att.overtime_hours<7:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                elif tot_wh >= act_hrs and att.overtime_hours>=7:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                elif tot_wh < act_hrs and att.overtime_hours>=7:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',0)
                                else:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',0)
                        else:
                            if att.attendance_upload:
                                
                                if att.status=='Present' and att.overtime_hours==0:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                if att.overtime_hours>0:
                                    if att.overtime_hours < 7:
                                        if att.status=='Present':
                                            frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                        frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                    elif att.overtime_hours >= 15:
                                        frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                        frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                    elif att.overtime_hours >= 7 and att.overtime_hours < 15:
                                        frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                        frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                            else:
                                if att.overtime_hours < 7:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',0)
                                elif att.overtime_hours >= 15:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                elif att.overtime_hours >= 7 and att.overtime_hours < 15:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                    if att.shift=='C':
                        act_time=frappe.db.get_value("Shift Type",{"name":att.shift},['_total_working_hours'])
                        # frappe.errprint(act_time)
                        act_hrs=4.0
                        shift_st = frappe.get_value("Shift Type", {'name': att.shift}, ['start_time'])
                        shift_start_time = datetime.strptime(str(shift_st), '%H:%M:%S').time()
                        shift_endt = frappe.get_value("Shift Type", {'name': att.shift}, ['end_time'])
                        shift_end_time = datetime.strptime(str(shift_endt), '%H:%M:%S').time()
                        shift_date = add_days(att.attendance_date,+1) 	
                        shift_end_datetime = datetime.combine(shift_date, shift_end_time)
                        shift_start_datetime = datetime.combine(shift_date, shift_start_time)
                        if att.in_time and att.out_time:
                            in_time = att.in_time
                            out_time = att.out_time
                            if isinstance(in_time, str):
                                in_time = datetime.strptime(in_time, '%Y-%m-%d %H:%M:%S')
                            if isinstance(out_time, str):
                                out_time = datetime.strptime(out_time, '%Y-%m-%d %H:%M:%S')
                            if in_time > shift_start_datetime:
                                if out_time > shift_end_datetime:
                                    tot_wh=time_diff_in_hours(shift_end_datetime, in_time)
                                else:
                                    tot_wh=time_diff_in_hours(out_time, in_time)
                            else:
                                if out_time > shift_end_datetime:
                                    tot_wh=time_diff_in_hours(shift_end_datetime, shift_start_datetime)
                                else:
                                    tot_wh=time_diff_in_hours(out_time, shift_start_datetime)
                        if tot_wh < act_hrs:
                            if att.att_permission:
                                perm=frappe.db.get_value("Permission",{'name':att.att_permission},['total_time'])
                                tot_wh=int(tot_wh)+int(perm)
                        if att.attendance_upload:
                            if att.status=='Present' and att.overtime_hours==0:
                                frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                frappe.db.set_value("Attendance",att.name,'b_allowance',0)
                            if att.overtime_hours>0:
                                if not hh:
                                    if att.overtime_hours >= 15:
                                        if att.status=='Present':
                                            frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                        frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                    else: 
                                        if att.status=='Present':
                                            frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                        frappe.db.set_value("Attendance",att.name,'b_allowance',0)
                                else:
                                    if att.overtime_hours >= 23:
                                        if att.status=='Present':
                                            frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                        frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                    else: 
                                        if att.status=='Present':
                                            frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                        frappe.db.set_value("Attendance",att.name,'b_allowance',0)
                        else:
                            if not hh:
                                if tot_wh >= act_hrs and att.overtime_hours >= 15:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',1)         
                                elif tot_wh >= act_hrs and att.overtime_hours < 15:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',0)             
                                elif tot_wh < act_hrs and att.overtime_hours >= 15:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                else: 
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',0)
                            else:
                                if tot_wh >= act_hrs and att.overtime_hours >= 23:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                elif tot_wh >= act_hrs and att.overtime_hours < 23:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',0)
                                elif tot_wh < act_hrs and att.overtime_hours >= 23:
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                                else: 
                                    frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                    frappe.db.set_value("Attendance",att.name,'b_allowance',0)
                    
                    if att.shift=='A':
                        if not hh:	
                            if att.overtime_hours>=8 and att.overtime_hours<15:
                                frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                            elif att.overtime_hours>=15:
                                frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                            else:
                                frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                frappe.db.set_value("Attendance",att.name,'b_allowance',0)
                        else:
                            if att.overtime_hours >= 15 and att.overtime_hours < 23:
                                frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                            elif att.overtime_hours >= 23:
                                frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                                frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                            else:
                                frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                                frappe.db.set_value("Attendance",att.name,'b_allowance',0)

        if att.employee_type == "NAPS":
            if att.shift and att.attendance_upload:
                if att.shift == "B":
                    frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                    frappe.db.set_value("Attendance",att.name,'b_allowance',1)
                elif att.shift =="C":
                    frappe.db.set_value("Attendance",att.name,'c_allowance',1)
                    frappe.db.set_value("Attendance",att.name,'b_allowance',0)  
                else:
                    frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                    frappe.db.set_value("Attendance",att.name,'b_allowance',0)
            else:
                frappe.db.set_value("Attendance",att.name,'c_allowance',0)
                frappe.db.set_value("Attendance",att.name,'b_allowance',0)                    


@frappe.whitelist()
def create_special_allow(fdate,tdate):
    special_all=0
    attendance=frappe.get_all("Attendance",{'employee_type':'Staff','working_hours':('>=',20),'attendance_date':('between',(fdate,tdate))},['attendance_date','out_time'])
    if attendance:  
        for att in attendance:
            # frappe.errprint(att.employee)
            shift_et = frappe.db.get_value("Shift Type", {'name': 'C'}, ['end_time'])
            if isinstance(shift_et, str):
                shift_et = time.fromisoformat(shift_et)
            start_date=fdate
            end_date=add_days(tdate , 1)
            holiday_dates = get_holiday_dates_for_employee(att.employee, fdate, end_date)
            if not holiday_dates:
                holiday_dates = []
            query = """SELECT cast(start_date as char) FROM `tabShift Assignment` WHERE employee='%s' AND shift_type = 'WW' AND reason = '' AND start_date BETWEEN '%s' AND '%s'"""  % (att.employee, start_date, end_date)
            # frappe.errprint(query)
            ww = frappe.db.sql(query,as_list=True)
            ww_list = list(chain(*ww))
            holiday_dates.extend(ww_list)
            day_before_holidays = []
            for holiday in holiday_dates:
                day_before_holidays.append(add_days(holiday, -1)) 
                out_time = att.out_time.time()
                out_time_timedelta = timedelta(hours=out_time.hour, minutes=out_time.minute, seconds=out_time.second)
                if out_time_timedelta >= shift_et:
                    day_of_week = att.attendance_date.weekday()
                    if cstr(att.attendance_date) in holiday_dates and cstr(att.attendance_date) not in day_before_holidays:
                        special_all=2500
                    elif cstr(att.attendance_date) in day_before_holidays and cstr(att.attendance_date) not in holiday_dates:
                        special_all=3000
                    elif cstr(att.attendance_date) in day_before_holidays and cstr(att.attendance_date) in holiday_dates:
                        special_all=3000
                    else:
                        if day_of_week in [0,1,2,3,4]:
                            special_all=1000
                        elif day_of_week ==5:
                            special_all=3000 
                        elif day_of_week ==6:
                            special_all=2500
            if special_all>0:
                if frappe.db.exists("Special Allowance",{'working_date':att.attendance_date,'employee':att.employee,'docstatus':['!=',2]}):
                    allow=frappe.get_doc("Special Allowance",{'working_date':att.attendance_date,'employee':att.employee,'docstatus':['!=',2]})
                    allow.employee=att.employee
                    allow.working_date=att.attendance_date
                    allow.amount=special_all
                    allow.save(ignore_permissions=True)
                else:
                    allow=frappe.new_doc('Special Allowance')
                    # frappe.errprint(att.employee)
                    allow.employee=att.employee
                    allow.working_date=att.attendance_date
                    allow.amount=special_all
                    allow.insert()
                    allow.save(ignore_permissions=True)

# @frappe.whitelist()
# def get_urc_to_ec(from_date):
#     print("HI")
#     urc = frappe.db.sql("""select biometric_pin,biometric_time,log_type,locationdevice_id,name from `tabUnregistered Employee Checkin` where date(biometric_time) = '%s' """%(from_date),as_dict=True)
#     for uc in urc:
#         pin = uc.biometric_pin
#         time = uc.biometric_time
#         dev = uc.locationdevice_id
#         typ = uc.log_type
#         nam = uc.name
#         if time != "":
#             if frappe.db.exists('Employee',{'name':pin}):
#                 if frappe.db.exists('Employee Checkin',{'biometric_pin':pin,"time":time}):
#                     print("HI")
#                 else:
#                     print("HII")
#                     ec = frappe.new_doc('Employee Checkin')
#                     ec.biometric_pin = pin
#                     ec.employee = frappe.db.get_value('Employee',{'name':pin},['employee_number'])
#                     ec.time = time
#                     ec.device_id = dev
#                     ec.log_type = typ
#                     ec.save(ignore_permissions=True)
#                     frappe.db.commit()
#                     print("Created")
#                     attendance = frappe.db.sql(""" delete from `tabUnregistered Employee Checkin` where name = '%s' """%(nam))
#                     print("Deleted")       
#             else:
#                 print("hello")
#     return "ok"


# @frappe.whitelist()
# def get_urc_to_ec(from_date, to_date, employee):

    # pin = frappe.db.get_value(
    #     'Employee',
    #     {'name': employee},
    #     'attendance_device_id'
    # )

    # urc = frappe.db.sql("""
    #     SELECT *
    #     FROM `tabUnregistered Employee Checkin`
    #     WHERE DATE(biometric_time) BETWEEN %s AND %s
    #     AND biometric_pin = %s
    # """, (from_date, to_date, pin), as_dict=True)

    # for uc in urc:

    #     pin = uc.biometric_pin
    #     time = uc.biometric_time
    #     dev = uc.location_device_id
    #     typ = uc.log_type
    #     nam = uc.name

    #     if not time:
    #         continue

    #     # Get employee from biometric PIN
    #     emp = frappe.db.get_value(
    #         'Employee',
    #         {'attendance_device_id': pin},
    #         'name'
    #     )

    #     if not emp:
    #         continue

    #     # Check duplicate Employee Checkin
    #     duplicate = frappe.db.exists(
    #         'Employee Checkin',
    #         {
    #             'employee': emp,
    #             'time': time
    #         }
    #     )

    #     if duplicate:
    #         # Duplicate timestamp - skip this checkin
    #         continue

    #     # Create Employee Checkin
    #     ec = frappe.new_doc('Employee Checkin')
    #     ec.biometric_pin = pin
    #     ec.employee = emp
    #     ec.time = time
    #     ec.device_id = dev
    #     ec.log_type = typ

    #     ec.save(ignore_permissions=True)

    #     # Delete successfully processed unregistered checkin
    #     frappe.db.delete(
    #         'Unregistered Employee Checkin',
    #         nam
    #     )

    #     frappe.db.commit()

    # return "ok"


@frappe.whitelist()
def get_urc_to_ec(from_date, to_date, employee=None, employee_type=None):
    employee_filters = {
        "status": "Active",
        "attendance_device_id": ["is", "set"]
    }

    # If Employee is selected
    if employee:
        employee_filters["name"] = employee

    # If Employee Type is selected
    if employee_type:
        employee_filters["employee_type"] = employee_type

    employees = frappe.get_all(
        "Employee",
        filters=employee_filters,
        fields=["name", "attendance_device_id"]
    )

    if not employees:
        return "No matching employees found."

    employee_map = {}

    for emp in employees:
        if emp.attendance_device_id:
            employee_map[str(emp.attendance_device_id)] = emp.name

    if not employee_map:
        return "No Attendance Device ID found for the selected employee(s)."

    urc_filters = {
        "biometric_time": ["between", [
            from_date + " 00:00:00",
            to_date + " 23:59:59"
        ]],
        "biometric_pin": ["in", list(employee_map.keys())]
    }

    urc = frappe.get_all(
        "Unregistered Employee Checkin",
        filters=urc_filters,
        fields=[
            "name",
            "biometric_pin",
            "biometric_time",
            "locationdevice_id",
            "log_type"
        ],
        order_by="biometric_time asc"
    )

    created = 0
    skipped = 0

    for uc in urc:

        pin = str(uc.biometric_pin)
        time = uc.biometric_time
        employee_name = employee_map.get(pin)

        if not time:
            continue

        if not employee_name:
            continue

        duplicate = frappe.db.exists(
            "Employee Checkin",
            {
                "employee": employee_name,
                "time": time
            }
        )

        if duplicate:

            frappe.db.delete(
                "Unregistered Employee Checkin",
                uc.name
            )

            skipped += 1

            continue

        ec = frappe.new_doc("Employee Checkin")

        ec.employee = employee_name
        ec.biometric_pin = pin
        ec.time = time
        ec.device_id = uc.locationdevice_id
        ec.log_type = uc.log_type

        ec.insert(ignore_permissions=True)

        frappe.db.delete(
            "Unregistered Employee Checkin",
            uc.name
        )

        created += 1

    frappe.db.commit()


    return {
        "status": "ok",
        "created": created,
        "skipped": skipped,
        "message": (
            f"Checkins created successfully. "
            f"Created: {created}, "
            f"Skipped duplicates: {skipped}"
        )
    }