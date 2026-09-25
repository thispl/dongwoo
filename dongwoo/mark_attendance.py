import frappe
from frappe.utils import time_diff_in_hours 
from datetime import datetime
from frappe.utils.data import today, add_days, add_years
from dateutil.relativedelta import relativedelta
from datetime import timedelta, time,date
from frappe.utils import time_diff_in_hours, formatdate, get_first_day,get_last_day, nowdate, now_datetime
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,
    nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime)
from frappe.utils.data import ceil, get_time, get_year_start
import datetime as dt
from datetime import datetime, timedelta
from frappe.utils.background_jobs import enqueue

@frappe.whitelist()
def get_dates(from_date,to_date):
    no_of_days = date_diff(add_days(to_date, 1), from_date)
    dates = [add_days(from_date, i) for i in range(0, no_of_days)]
    return dates

@frappe.whitelist()
def mark_att_from_frontend():
    enqueue(mark_att_specific, queue='default', timeout=6000)


@frappe.whitelist()
def mark_att_specific():
    from_date = '2026-08-19'
    to_date =  '2026-08-20'
    checkins = frappe.db.sql("""select * from `tabEmployee Checkin` where date(time) between '%s' and '%s' order by time ASC """%(from_date,to_date),as_dict=1)
    for c in checkins:
        employee = frappe.db.exists('Employee',{'status':'Active','date_of_joining':['<=',from_date],'name':c.employee})
        if employee:  
            mark_attendance_from_checkin_test(c.employee,c.time,c.log_type)
    mark_absent(from_date,to_date)
    mark_wh_ot(from_date,to_date)
    update_regularize_ot(from_date,to_date)   
    get_assigned_shift(from_date, to_date)
    update_workspot(from_date,to_date)
    mark_att_present(from_date, to_date)
    mark_late_early(from_date,to_date)
    update_location(from_date, to_date)
    duplicate_attendance(from_date, to_date)
    return "ok"  
# @frappe.whitelist()
# def update_att_without_employee(fdate,tdate):  
# 	enqueue(mark_att_without_employee, queue='long', timeout=18000, fdate=fdate, tdate=tdate)	
@frappe.whitelist()
def update_att_without_employee(fdate,tdate):
    frappe.msgprint("Attendance updating in background.Kindly check after few minutes.")
    frappe.enqueue(
        mark_att_without_employee, 
        queue="default",
        timeout=36000,
        is_async=True, 
        now=False, 
        job_name='Att settings',
        enqueue_after_commit=False,
        fdate=fdate,
        tdate=tdate
    )
@frappe.whitelist()
def update_att_with_employee_type(fdate,tdate,employee_type):
    frappe.msgprint("Attendance updating in background.Kindly check after few minutes.")
    frappe.enqueue(
        mark_att_with_employee_type, 
        queue="default",
        timeout=36000,
        is_async=True, 
        now=False, 
        job_name='Att settings',
        enqueue_after_commit=False,
        fdate=fdate,
        tdate=tdate,
        employee_type =employee_type
    )

@frappe.whitelist()
def update_att_with_con_name(fdate,tdate,employee_type,con_name):
    frappe.msgprint("Attendance updating in background.Kindly check after few minutes.")
    frappe.enqueue(
        mark_att_with_con_name, 
        queue="default",
        timeout=36000,
        is_async=True, 
        now=False, 
        job_name='Att settings',
        enqueue_after_commit=False,
        fdate=fdate,
        tdate=tdate,
        employee_type =employee_type,
        con_name = con_name
    )

@frappe.whitelist()
def update_att_with_employee(fdate,tdate,employee):
    frappe.enqueue(
        mark_att_with_employee, 
        queue="default",
        timeout=36000,
        is_async=True, 
        now=False, 
        job_name='Att settings employee',
        enqueue_after_commit=False,
        fdate=fdate,
        tdate=tdate,
        employee=employee
    )
@frappe.whitelist()
def mark_att_without_employee(fdate,tdate):
    from_date = fdate
    to_date = tdate
    checkins = frappe.db.sql("""
    select * 
    from `tabEmployee Checkin` 
    where date(time) between '%s' and '%s' 	
    order by time ASC 
""" % (from_date, to_date), as_dict=1)
    for c in checkins:
        # fdate = frappe.utils.getdate(fdate)
        # tdate = frappe.utils.getdate(tdate)
        # doj=frappe.db.get_value("Employee",{'name':c.employee},['date_of_joining'])
        # date_of_joining = frappe.utils.getdate(doj)
        # if fdate <= date_of_joining <= tdate:
        #     from_date = date_of_joining
        employee = frappe.db.exists('Employee',{'status':'Active','date_of_joining':['<=',from_date],'name':c.employee})
        if employee:  
            mark_attendance_from_checkin_test(c.employee,c.time,c.log_type)
    mark_absent(from_date,to_date)
    mark_wh_ot(from_date,to_date)  
    update_regularize_ot(from_date,to_date)
    get_assigned_shift(from_date, to_date)
    update_workspot(from_date,to_date)
    mark_att_present(from_date, to_date)
    mark_late_early(from_date,to_date)
    create_ot_req(from_date,to_date)
    update_location(from_date, to_date)
    return "ok"     	        

@frappe.whitelist()
def mark_att_with_employee(fdate,tdate,employee):
    from_date = fdate
    to_date = tdate
    checkins = frappe.db.sql("""
    select * 
    from `tabEmployee Checkin` 
    where date(time) between '%s' and '%s' 
    and employee='%s'	
    order by time ASC 
""" % (from_date, to_date, employee), as_dict=1)
    for c in checkins:
        fdate = frappe.utils.getdate(fdate)
        tdate = frappe.utils.getdate(tdate)
        doj=frappe.db.get_value("Employee",{'name':c.employee},['date_of_joining'])
        date_of_joining = frappe.utils.getdate(doj)
        if fdate <= date_of_joining <= tdate:
            from_date = date_of_joining
        employee = frappe.db.exists('Employee',{'status':'Active','date_of_joining':['<=',from_date],'name':c.employee})
        if employee:  
            mark_attendance_from_checkin_test(c.employee,c.time,c.log_type)
    mark_absent_with_employee(from_date,to_date,employee)
    mark_wh_ot_with_employee(from_date,to_date,employee)   
    update_regularize_ot_with_employee(from_date,to_date,employee) 
    get_assigned_shift_with_employee(from_date, to_date, employee)
    update_workspot_with_employee(from_date,to_date,employee)
    mark_att_present_with_employee(from_date, to_date, employee)
    mark_late_early_with_employee(from_date,to_date,employee)
    create_ot_req_emp(from_date,to_date,employee)
    update_location_with_employee(from_date, to_date, employee)
    return "ok" 

@frappe.whitelist()
def mark_att_with_employee_type(fdate,tdate,employee_type):
    from_date = fdate
    to_date = tdate
    checkins = frappe.db.sql("""
        select * 
        from `tabEmployee Checkin` 
        where date(time) between '%s' and '%s' 
        and employee_type='%s'	
        order by time ASC 
    """ % (from_date, to_date, employee_type), as_dict=1)
    for c in checkins:
        fdate = frappe.utils.getdate(fdate)
        tdate = frappe.utils.getdate(tdate)
        doj=frappe.db.get_value("Employee",{'name':c.employee},['date_of_joining'])
        date_of_joining = frappe.utils.getdate(doj)
        if fdate <= date_of_joining <= tdate:
            from_date = date_of_joining
        employee = frappe.db.exists('Employee',{'status':'Active','date_of_joining':['<=',from_date],'name':c.employee})
        if employee:  
            mark_attendance_from_checkin_test(c.employee,c.time,c.log_type)
    mark_absent_with_employee_type(from_date,to_date,employee_type)
    mark_wh_ot_with_employee_type(from_date,to_date,employee_type)   
    update_regularize_ot_with_employee_type(from_date,to_date,employee_type)
    get_assigned_shift_with_employee_type(from_date, to_date, employee_type)
    update_workspot_with_employee_type(from_date,to_date,employee_type)
    mark_att_present_with_employee_type(from_date, to_date, employee_type)
    mark_late_early_with_employee_type(from_date,to_date,employee_type)
    create_ot_req_employee_type(from_date,to_date,employee_type)
    update_location_with_employee_type(from_date, to_date,employee_type)
    return "ok" 

@frappe.whitelist()
def mark_att_with_con_name(fdate,tdate,employee_type,con_name):
    from_date = fdate
    to_date = tdate
    checkins = frappe.db.sql("""
        select * 
        from `tabEmployee Checkin` 
        where date(time) between '%s' and '%s' 
        and employee_type='%s' 
        and contractor_name = '%s'
        order by time ASC 
    """ % (from_date, to_date, employee_type,con_name), as_dict=1)
    for c in checkins:
        fdate = frappe.utils.getdate(fdate)
        tdate = frappe.utils.getdate(tdate)
        doj=frappe.db.get_value("Employee",{'name':c.employee},['date_of_joining'])
        date_of_joining = frappe.utils.getdate(doj)
        if fdate <= date_of_joining <= tdate:
            from_date = date_of_joining
        employee = frappe.db.exists('Employee',{'status':'Active','date_of_joining':['<=',from_date],'name':c.employee})
        if employee:  
            mark_attendance_from_checkin_test(c.employee,c.time,c.log_type)
    mark_absent_with_con_name(from_date,to_date,employee_type,con_name)
    mark_wh_ot_with_con_name(from_date,to_date,employee_type,con_name)   
    update_regularize_ot_with_con_name(from_date,to_date,employee_type,con_name)
    get_assigned_shift_with_con_name(from_date, to_date, employee_type,con_name)
    update_workspot_with_con_name(from_date,to_date,employee_type,con_name)
    mark_att_present_with_con_name(from_date, to_date, employee_type,con_name)
    mark_late_early_with_con_name(from_date,to_date,employee_type,con_name)
    update_location_with_con_name(from_date, to_date,employee_type,con_name)
    return "ok" 



MARK_ATT_LOCK_KEY = "dongwoo:mark_att_running"
MARK_ATT_JOB_TIMEOUT = 7200


def mark_att_lock_key():
    return f"{frappe.conf.db_name}|{MARK_ATT_LOCK_KEY}"


def mark_att_is_running():
    return bool(frappe.cache().exists(mark_att_lock_key()))


@frappe.whitelist()
def mark_att():
    if mark_att_is_running():
        return
    frappe.enqueue(
        mark_att_enqueue, 
        queue="default",
        timeout=MARK_ATT_JOB_TIMEOUT,
        is_async=True, 
        now=False, 
        job_name='Mark Attendance',
        enqueue_after_commit=False,
        
    )
@frappe.whitelist()
def mark_att_enqueue():
    cache = frappe.cache()
    if not cache.set(mark_att_lock_key(), now_datetime().isoformat(), nx=True, ex=MARK_ATT_JOB_TIMEOUT + 300):
        return "skipped: another Mark Attendance job is running"
    try:
        return _mark_att_pipeline()
    finally:
        cache.delete(mark_att_lock_key())


def _mark_att_pipeline():
    from_date = add_days(today(),-1)
    to_date = today()
    # from_date = '2026-08-18'
    # to_date =  '2026-08-19'
    checkins = frappe.db.sql("""
    select name, employee, time, log_type
    from `tabEmployee Checkin`
    where time >= %s and time < %s

    order by time ASC
""", (f"{from_date} 00:00:00", f"{add_days(getdate(to_date), 1)} 00:00:00"), as_dict=1)
    active_employees = set(frappe.db.get_all('Employee', {'status': 'Active', 'date_of_joining': ['<=', to_date]}, pluck='name'))
    doj_cache = {}
    processed = 0
    for c in checkins:
        if c.employee not in active_employees:
            continue
        fdate = frappe.utils.getdate(from_date)
        tdate = frappe.utils.getdate(to_date)
        if c.employee not in doj_cache:
            doj_cache[c.employee] = frappe.db.get_value("Employee", {'name': c.employee}, 'date_of_joining')
        date_of_joining = frappe.utils.getdate(doj_cache[c.employee])
        if fdate <= date_of_joining <= tdate:
            from_date = date_of_joining
        if date_of_joining and date_of_joining <= fdate:
            # if c.attendance == "HR-ATT-2026-134503":
            #     continue

            mark_attendance_from_checkin_test(c.employee,c.time,c.log_type)
            processed += 1
            if processed % 25 == 0:
                frappe.db.commit()
    frappe.db.commit()
    mark_absent(from_date,to_date)
    frappe.db.commit()
    mark_wh_ot(from_date,to_date)  
    frappe.db.commit()
    update_regularize_ot(from_date,to_date) 
    frappe.db.commit()
    get_assigned_shift(from_date, to_date)
    frappe.db.commit()
    update_workspot(from_date,to_date)
    frappe.db.commit()
    mark_att_present(from_date, to_date)
    frappe.db.commit()
    mark_late_early(from_date,to_date)
    frappe.db.commit()
    create_ot_req(from_date,to_date)
    frappe.db.commit()
    update_location(from_date, to_date)
    frappe.db.commit()
    duplicate_attendance(from_date, to_date)
    frappe.db.commit()
    frappe.log_error(f"From: {from_date}, To: {to_date}", "DATE DEBUG")
    return "ok"    


def duplicate_attendance(from_date, to_date):

    attendance_list = frappe.get_all(
        "Attendance",
        filters={
            "attendance_date": ["between", [from_date, to_date]]
        },
        fields=["name", "employee", "attendance_date", "in_time", "out_time", "shift"]
    )

    from collections import defaultdict
    grouped = defaultdict(list)

    for att in attendance_list:
        key = (att.employee, att.attendance_date)
        grouped[key].append(att)

    for (employee, att_date), records in grouped.items():

        if len(records) <= 1:
            continue  

        valid_records = []
        invalid_records = []

        for r in records:
            if r.in_time or r.out_time or r.shift:
                valid_records.append(r)
            else:
                invalid_records.append(r)


        if valid_records:
            for r in invalid_records:
                frappe.log_error(f"Deleting invalid attendance: {r.name}", "Duplicate Cleanup")
                frappe.delete_doc("Attendance", r.name, force=1)

            if len(valid_records) > 1:
                for r in valid_records[1:]:
                    frappe.log_error(f"Deleting extra valid attendance: {r.name}", "Duplicate Cleanup")
                    frappe.delete_doc("Attendance", r.name, force=1)

        else:
            for r in records[1:]:
                frappe.log_error(f"Deleting duplicate invalid attendance: {r.name}", "Duplicate Cleanup")
                frappe.delete_doc("Attendance", r.name, force=1)

# This method currently not used in attendance code 	        
@frappe.whitelist()
def mark_attendance_from_checkin(employee,time,log_type):
    if log_type == 'IN':
        att_time = time.time()
        # shift = ''
        att_date = time.date()
        max_in = datetime.strptime('05:30','%H:%M').time()
        before_in = frappe.db.sql("""select * from `tabEmployee Checkin` where employee = '%s' and log_type = 'IN' and date(time) = '%s' and TIME(time) < '%s' order by time ASC """%(employee,att_date,max_in),as_dict=True)
        after_in = frappe.db.sql("""select * from `tabEmployee Checkin` where employee = '%s' and log_type = 'IN' and date(time) = '%s' and TIME(time) > '%s' order by time ASC """%(employee,att_date,max_in),as_dict=True)
        if before_in and not after_in:
            att_date = add_days(att_date,-1)
            att = frappe.db.exists('Attendance',{"employee":employee,'attendance_date':att_date,'docstatus':['!=','2']})   
            if not att:
                att = frappe.new_doc("Attendance")
                att.employee = employee
                att.attendance_date = att_date
                if not att.shift:
                    att.shift = get_actual_shift_start(get_time(before_in[0].time))
                att.status = 'Absent'
                att.in_time = before_in[0].time
                att.total_working_hours = "00:00:00"
                att.working_hours = "0.0"
                att.extra_hours = "0.0"
                att.total_extra_hours = "00:00:00"
                att.total_overtime_hours = "00:00:00"
                att.overtime_hours = "0.0"
                att.late_entry_time = "00:00:00"
                att.early_out_time = "00:00:00"
                att.save(ignore_permissions=True)
                frappe.db.commit()
                for c in before_in:
                    frappe.db.set_value('Employee Checkin', c.name, 'skip_auto_attendance', 1)
                    frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                return att  
            else:
                att = frappe.get_doc("Attendance",att)
                if att.docstatus == 0 or att.docstatus == 1 and not att.in_time:
                    # print(att.name)
                    att.employee = employee
                    att.attendance_date = att_date
                    # att.shift = shift
                    # att.status = 'Absent'
                    att.in_time =before_in[0]['time']
                    att.shift = get_actual_shift_start(get_time(before_in[0]['time']))
                    # att.late_entry_time = "00:00:00"
                    # att.early_out_time = "00:00:00"
                    att.save(ignore_permissions=True)
                    frappe.db.commit()
                    for c in before_in:
                        frappe.db.set_value('Employee Checkin', c.name, 'skip_auto_attendance', 1)
                        frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                    return att 
        if after_in and not before_in:
            att = frappe.db.exists('Attendance',{"employee":employee,'attendance_date':att_date,'docstatus':['!=','2']})   
            if not att:
                att = frappe.new_doc("Attendance")
                att.employee = employee
                att.attendance_date = att_date
                att.shift = get_actual_shift_start(get_time(after_in[0].time))
                att.status = 'Absent'
                att.in_time = after_in[0].time
                att.total_working_hours = "00:00:00"
                att.working_hours = "0.0"
                att.extra_hours = "0.0"
                att.total_extra_hours = "00:00:00"
                att.total_overtime_hours = "00:00:00"
                att.overtime_hours = "0.0"
                att.late_entry_time = "00:00:00"
                att.early_out_time = "00:00:00"
                att.save(ignore_permissions=True)
                frappe.db.commit()
                for c in after_in:
                    frappe.db.set_value('Employee Checkin', c.name, 'skip_auto_attendance', 1)
                    frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                return att  
            else:
                att = frappe.get_doc("Attendance",att)
                if att.docstatus == 0 or att.docstatus == 1:
                    att.employee = employee
                    att.attendance_date = att_date
                    # att.shift = shift
                    # att.status = 'Absent'
                    att.in_time =after_in[0]['time']
                    att.shift = get_actual_shift_start(get_time(after_in[0]['time']))
                    # att.total_working_hours = "00:00:00"
                    # att.working_hours = "0.0"
                    # att.extra_hours = "0.0"
                    # att.total_extra_hours = "00:00:00"
                    # att.total_overtime_hours = "00:00:00"
                    # att.overtime_hours = "0.0"
                    # att.late_entry_time = "00:00:00"
                    # att.early_out_time = "00:00:00"
                    att.save(ignore_permissions=True)
                    frappe.db.commit()
                    for c in after_in:
                        frappe.db.set_value('Employee Checkin', c.name, 'skip_auto_attendance', 1)
                        frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                    return att
        if after_in and before_in:
            if before_in:
                prev_date = add_days(att_date,-1)
                prev_att = frappe.db.exists('Attendance',{"employee":employee,'attendance_date':prev_date,'docstatus':['!=','2']})   
                if not prev_att:
                    prev_att = frappe.new_doc("Attendance")
                    prev_att.employee = employee
                    prev_att.attendance_date = prev_date
                    if not prev_att.shift:
                        prev_att.shift = get_actual_shift_start(get_time(before_in[0].time))
                    prev_att.status = 'Absent'
                    prev_att.in_time = before_in[0].time
                    prev_att.total_working_hours = "00:00:00"
                    prev_att.working_hours = "0.0"
                    prev_att.extra_hours = "0.0"
                    prev_att.total_extra_hours = "00:00:00"
                    prev_att.total_overtime_hours = "00:00:00"
                    prev_att.overtime_hours = "0.0"
                    prev_att.late_entry_time = "00:00:00"
                    prev_att.early_out_time = "00:00:00"
                    prev_att.save(ignore_permissions=True)
                    frappe.db.commit()
                    for c in before_in:
                        frappe.db.set_value('Employee Checkin', c.name, 'skip_auto_attendance', 1)
                        frappe.db.set_value("Employee Checkin",c.name, "attendance", prev_att.name)
                    return prev_att  
                else:
                    prev_att = frappe.get_doc("Attendance",prev_att)
                    if (prev_att.docstatus == 0 or prev_att.docstatus == 1) and not prev_att.in_time:
                        prev_att.employee = employee
                        prev_att.attendance_date = prev_date
                        # prev_att.shift = shift
                        # prev_att.status = 'Absent'
                        prev_att.in_time =before_in[0]['time']
                        prev_att.shift = get_actual_shift_start(get_time(before_in[0]['time']))
                        # prev_att.total_working_hours = "00:00:00"
                        # prev_att.working_hours = "0.0"
                        # prev_att.extra_hours = "0.0"
                        # prev_att.total_extra_hours = "00:00:00"
                        # prev_att.total_overtime_hours = "00:00:00"
                        # prev_att.overtime_hours = "0.0"
                        # prev_att.late_entry_time = "00:00:00"
                        # prev_att.early_out_time = "00:00:00"
                        prev_att.save(ignore_permissions=True)
                        frappe.db.commit()
                        for c in before_in:
                            frappe.db.set_value('Employee Checkin', c.name, 'skip_auto_attendance', 1)
                            frappe.db.set_value("Employee Checkin",c.name, "attendance", prev_att.name)
                        # return prev_att
            
            att = frappe.db.exists('Attendance',{"employee":employee,'attendance_date':att_date,'docstatus':['!=','2']})   
            if not att:
                # print('attnot')
                att = frappe.new_doc("Attendance")
                att.employee = employee
                att.attendance_date = att_date
                att.shift = get_actual_shift_start(get_time(after_in[0].time))
                att.status = 'Absent'
                att.in_time = after_in[0].time
                att.total_working_hours = "00:00:00"
                att.working_hours = "0.0"
                att.extra_hours = "0.0"
                att.total_extra_hours = "00:00:00"
                att.total_overtime_hours = "00:00:00"
                att.overtime_hours = "0.0"
                att.late_entry_time = "00:00:00"
                att.early_out_time = "00:00:00"
                att.save(ignore_permissions=True)
                frappe.db.commit()
                for c in after_in:
                    frappe.db.set_value('Employee Checkin', c.name, 'skip_auto_attendance', 1)
                    frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                return att  
            else:
                # print('presentatt')
                att = frappe.get_doc("Attendance",att)
                if att.docstatus == 0 or att.docstatus == 1:
                    att.employee = employee
                    att.attendance_date = att_date
                    # att.shift = shift
                    # att.status = 'Absent'
                    att.in_time =after_in[0].time
                    # print(after_in[0].time)
                    # print(att.in_time)
                    att.shift = get_actual_shift_start(get_time(after_in[0].time))
                    # att.total_working_hours = "00:00:00"
                    # att.working_hours = "0.0"
                    # att.extra_hours = "0.0"
                    # att.total_extra_hours = "00:00:00"
                    # att.total_overtime_hours = "00:00:00"
                    # att.overtime_hours = "0.0"
                    # att.late_entry_time = "00:00:00"
                    # att.early_out_time = "00:00:00"
                    att.save(ignore_permissions=True)
                    frappe.db.commit()
                    for c in after_in:
                        frappe.db.set_value('Employee Checkin', c.name, 'skip_auto_attendance', 1)
                        frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                    return att
    if log_type == 'OUT':
        
        # shift = ''
        att_date = time.date()
        att_time = time.time()
        max_out = datetime.strptime('10:30','%H:%M').time()
        max_in = datetime.strptime('05:30','%H:%M').time()
        if att_time < max_out:
            same_day_out = frappe.db.sql("""SELECT * FROM `tabEmployee Checkin` WHERE employee = %s AND log_type = 'IN' AND DATE(time) = %s AND TIME(time) < %s AND device_id != 'Canteen' ORDER BY time ASC """, (employee, att_date, max_out), as_dict=True)
            yesterday = add_days(att_date,-1)
            checkins = frappe.db.sql("""select * from `tabEmployee Checkin` where employee = '%s' and log_type = 'OUT' and date(time) = '%s' and TIME(time) < '%s' order by time ASC """%(employee,att_date,max_out),as_dict=True)
            att = frappe.db.exists("Attendance",{'employee':employee,'attendance_date':yesterday})	
            
            if att:
                att = frappe.get_doc("Attendance",att)
                if att.docstatus != 2:
                        if att.out_time is None:
                            if not att.shift:
                                if len(checkins) > 0:
                                    att.shift = get_actual_shift(get_time(checkins[-1].time))
                                    att.out_time = checkins[-1].time
                                    for c in checkins:
                                        frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance',1)
                                        frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                                else:
                                    att.shift = get_actual_shift(get_time(checkins[0].time))
                                    att.out_time = checkins[0].time
                                    frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance',1)
                                    frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
                            else:
                                if len(checkins) > 0:
                                    att.out_time = checkins[-1].time
                                    for c in checkins:
                                        frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance',1)
                                        frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                                else:
                                    att.out_time = checkins[0].time
                                    frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance',1)
                                    frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
                            # att.status = 'Absent'    
                            att.save(ignore_permissions=True)
                            frappe.db.commit()
                            return att
                        else:
                            if not att.shift:
                                if len(checkins) > 0:
                                    att.shift = get_actual_shift(get_time(checkins[-1].time))
                                    att.out_time = checkins[-1].time
                                    for c in checkins:
                                        frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance',1)
                                        frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                                else:
                                    att.out_time = checkins[0].time
                                    att.shift = get_actual_shift(get_time(checkins[0].time))
                                    frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance',1)
                                    frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
                                
                            else:
                                if len(checkins) > 0:
                                    att.out_time = checkins[-1].time
                                    for c in checkins:
                                        frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance',1)
                                        frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                                else:
                                    att.out_time = checkins[0].time
                                    frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance',1)
                                    frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
                            att.save(ignore_permissions=True)
                            frappe.db.commit()
                            return att
            else:
                att = frappe.new_doc("Attendance")
                att.employee = employee
                att.attendance_date = yesterday
                att.status = 'Absent'
                if len(checkins) > 0:
                    att.out_time = checkins[-1].time
                    att.shift = get_actual_shift(get_time(checkins[-1].time))
                    for c in checkins:
                        frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance',1)
                        frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                else:
                    att.out_time = checkins[0].time
                    att.shift = get_actual_shift(get_time(checkins[0].time))
                    frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance',1)
                    frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
                att.total_working_hours = "00:00:00"
                att.working_hours = "0.0"
                att.extra_hours = "0.0"
                att.total_extra_hours = "00:00:00"
                att.total_overtime_hours = "00:00:00"
                att.overtime_hours = "0.0"
                att.late_entry_time = "00:00:00"
                att.early_out_time = "00:00:00"
                att.save(ignore_permissions=True)
                frappe.db.commit()
                for c in checkins:
                    frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance',1)
                    frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                return att	
        else:
            checkins = frappe.db.sql("""select * from `tabEmployee Checkin` where employee ='%s' and log_type = 'OUT' and date(time) = '%s' and TIME(time) > '%s' order by time ASC"""%(employee,att_date,max_out),as_dict=True)
            att = frappe.db.exists("Attendance",{'employee':employee,'attendance_date':att_date})
            if att:
                att = frappe.get_doc("Attendance",att)
                if att.docstatus != 2:
                    # if att.status != 'Present': 
                        if not att.out_time:
                            if not att.shift:
                                if len(checkins) > 0:
                                    att.shift = get_actual_shift(get_time(checkins[-1].time))
                                    att.out_time = checkins[-1].time
                                    for c in checkins:
                                        frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance',1)
                                        frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                                else:
                                    att.shift = get_actual_shift(get_time(checkins[0].time))
                                    att.out_time = checkins[0].time
                                    frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance',1)
                                    frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
                            else:
                                if len(checkins) > 0:
                                    att.out_time = checkins[-1].time
                                    for c in checkins:
                                        frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance',1)
                                        frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                                else:
                                    att.out_time = checkins[0].time
                                    frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance',1)
                                    frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
                            # att.status = 'Absent'    
                            att.save(ignore_permissions=True)
                            frappe.db.commit()
                            return att
                        else:
                            if len(checkins) > 0:
                                att.out_time = checkins[-1].time
                            else:
                                att.out_time = checkins[0].time
                            if not att.shift:
                                att.shift = get_actual_shift(get_time(checkins[-1].time))
                        att.save(ignore_permissions=True)
                        return att
            else:
                att = frappe.new_doc("Attendance")
                att.employee = employee
                att.attendance_date = att_date
                # att.shift = shift
                att.status = 'Absent'
                if len(checkins) > 0:
                    att.shift = get_actual_shift(get_time(checkins[-1].time))
                    att.out_time = checkins[-1].time
                else:
                    att.shift = get_actual_shift(get_time(checkins[0].time))
                    att.out_time = checkins[0].time
                att.total_working_hours = "00:00:00"
                att.working_hours = "0.0"
                att.extra_hours = "0.0"
                att.total_extra_hours = "00:00:00"
                att.total_overtime_hours = "00:00:00"
                att.overtime_hours = "0.0"
                att.late_entry_time = "00:00:00"
                att.early_out_time = "00:00:00"
                att.save(ignore_permissions=True)
                frappe.db.commit()
                for c in checkins:
                    frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance',1)
                    frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                return att 

@frappe.whitelist()
def is_between(time, time_range):
    if time_range[1] < time_range[0]:
        return time >= time_range[0] or time <= time_range[1]
    return time_range[0] <= time <= time_range[1]

@frappe.whitelist()
def get_actual_shift_start(get_shift_time):
    from datetime import datetime
    from datetime import date, timedelta,time
    shift1 = frappe.db.get_value('Shift Type',{'name':'A'},['checkin_start_time','checkin_end_time'])
    shift2 = frappe.db.get_value('Shift Type',{'name':'B'},['checkin_start_time','checkin_end_time'])
    shift3 = frappe.db.get_value('Shift Type',{'name':'C'},['checkin_start_time','checkin_end_time'])
    att_time_seconds = get_shift_time.hour * 3600 + get_shift_time.minute * 60 + get_shift_time.second
    shift = ''
    if shift1[0].total_seconds() < att_time_seconds < shift1[1].total_seconds():
        shift = 'A'
    if shift2[0].total_seconds() < att_time_seconds < shift2[1].total_seconds():
        shift = 'B'
    if shift3[0].total_seconds() < att_time_seconds < shift3[1].total_seconds():
        shift = 'C'
    return shift

@frappe.whitelist()
def get_actual_shift(get_shift_time):
    from datetime import datetime
    from datetime import date, timedelta,time
    shift1 = frappe.db.get_value('Shift Type',{'name':'A'},['checkout_start_time','checkout_end_time'])
    shift2 = frappe.db.get_value('Shift Type',{'name':'B'},['checkout_start_time','checkout_end_time'])
    shift3 = frappe.db.get_value('Shift Type',{'name':'C'},['checkout_start_time','checkout_end_time'])
    att_time_seconds = get_shift_time.hour * 3600 + get_shift_time.minute * 60 + get_shift_time.second
    shift = ''
    if shift1[0].total_seconds() < att_time_seconds < shift1[1].total_seconds():
        shift = 'A'
    if shift2[0].total_seconds() < att_time_seconds < shift2[1].total_seconds():
        shift = 'B'
    if shift3[0].total_seconds() < att_time_seconds < shift3[1].total_seconds():
        shift = 'C'
    return shift

@frappe.whitelist()
def mark_absent(from_date,to_date):
        dates = get_dates(from_date,to_date)
        for date in dates:
            employee = frappe.db.get_all('Employee',{'status':'Active','date_of_joining':['<=',from_date]})
            for emp in employee:
                hh = check_holiday(date,emp.name)
                if not hh:
                    if not frappe.db.exists('Attendance',{'attendance_date':date,'employee':emp.name,'docstatus':('!=','2')}):
                        att = frappe.new_doc("Attendance")
                        att.employee = emp.name
                        att.status = 'Absent'
                        att.attendance_date = date
                        att.total_working_hours = "00:00:00"
                        att.working_hours = "0.0"
                        att.extra_hours = "0.0"
                        att.total_extra_hours = "00:00:00"
                        att.total_overtime_hours = "00:00:00"
                        att.overtime_hours = "0.0"
                        att.late_entry_time = "00:00:00"
                        att.early_out_time = "00:00:00"
                        att.save(ignore_permissions=True)
                        frappe.db.commit()  

@frappe.whitelist()
def mark_absent_with_employee(from_date,to_date,employee):
        dates = get_dates(from_date,to_date)
        for date in dates:
            employees = frappe.db.get_all('Employee',{'status':'Active','name':employee,'date_of_joining':['<=',from_date]},['*'])
            for emp in employees:
                hh = check_holiday(date,emp.name)
                if not hh:
                    if not frappe.db.exists('Attendance',{'attendance_date':date,'employee':emp.name,'docstatus':('!=','2')}):
                        att = frappe.new_doc("Attendance")
                        att.employee = emp.name
                        att.status = 'Absent'
                        att.attendance_date = date
                        att.total_working_hours = "00:00:00"
                        att.working_hours = "0.0"
                        att.extra_hours = "0.0"
                        att.total_extra_hours = "00:00:00"
                        att.total_overtime_hours = "00:00:00"
                        att.overtime_hours = "0.0"
                        att.late_entry_time = "00:00:00"
                        att.early_out_time = "00:00:00"
                        att.save(ignore_permissions=True)
                        frappe.db.commit()  



@frappe.whitelist()
def mark_absent_with_employee_type(from_date,to_date,employee_type):
        dates = get_dates(from_date,to_date)
        for date in dates:
            employees = frappe.db.get_all('Employee',{'status':'Active','employee_type':employee_type,'date_of_joining':['<=',from_date]},['*'])
            for emp in employees:
                hh = check_holiday(date,emp.name)
                if not hh:
                    if not frappe.db.exists('Attendance',{'attendance_date':date,'employee':emp.name,'docstatus':('!=','2')}):
                        att = frappe.new_doc("Attendance")
                        att.employee = emp.name
                        att.status = 'Absent'
                        att.attendance_date = date
                        att.total_working_hours = "00:00:00"
                        att.working_hours = "0.0"
                        att.extra_hours = "0.0"
                        att.total_extra_hours = "00:00:00"
                        att.total_overtime_hours = "00:00:00"
                        att.overtime_hours = "0.0"
                        att.late_entry_time = "00:00:00"
                        att.early_out_time = "00:00:00"
                        att.save(ignore_permissions=True)
                        frappe.db.commit()  

@frappe.whitelist()
def mark_absent_with_con_name(from_date,to_date,employee_type,con_name):
        dates = get_dates(from_date,to_date)
        for date in dates:
            employees = frappe.db.get_all('Employee',{'status':'Active','employee_type':employee_type,"contractor":con_name,'date_of_joining':['<=',from_date]},['*'])
            for emp in employees:
                hh = check_holiday(date,emp.name)
                if not hh:
                    if not frappe.db.exists('Attendance',{'attendance_date':date,'employee':emp.name,'docstatus':('!=','2')}):
                        att = frappe.new_doc("Attendance")
                        att.employee = emp.name
                        att.status = 'Absent'
                        att.attendance_date = date
                        att.total_working_hours = "00:00:00"
                        att.working_hours = "0.0"
                        att.extra_hours = "0.0"
                        att.total_extra_hours = "00:00:00"
                        att.total_overtime_hours = "00:00:00"
                        att.overtime_hours = "0.0"
                        att.late_entry_time = "00:00:00"
                        att.early_out_time = "00:00:00"
                        att.save(ignore_permissions=True)
                        frappe.db.commit()  



@frappe.whitelist()
def check_holiday(date,emp):
    holiday_list = frappe.db.get_value('Employee',{'name':emp},'holiday_list')
    holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List`
    left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(holiday_list,date),as_dict=True)
    doj= frappe.db.get_value("Employee",{'name':emp},"date_of_joining")
    status = ''
    if frappe.db.exists('Shift Assignment',{'start_date':date,'employee':emp,'shift_type':'WW','docstatus':1}):
        return "WW"
    elif holiday :
        if doj < holiday[0].holiday_date:
            if holiday[0].weekly_off == 1:
                return "WW"     
            else:
                return "HH"
@frappe.whitelist()
def mark_wh_ot(from_date, to_date):
    from_date=add_days(from_date,-1)
    attendance = frappe.db.get_all('Attendance', {'attendance_date': ('between', (from_date,to_date)),'docstatus': ('!=', '2')}, ['*'])
    # attendance = frappe.db.get_all('Attendance', {'attendance_date': ('between', (from_date,to_date)),'docstatus': ('!=', '2'),'regularize_marked': ('!=', 1)}, ['*'])
    for att in attendance:
        employee=att.employee
        if not att.attendance_upload:
            if att.shift and (att.in_time or ((att.session_from_time or (att.session and att.from_time)) and att.on_duty_application))and (att.out_time or ((att.session_to_time or (att.session and att.to_time)) and att.on_duty_application)):
                in_time = att.in_time
                out_time = att.out_time
                if att.shift == 'C':
                    shiftdate = add_days(att.attendance_date,+1) 	
                else:
                    shiftdate = att.attendance_date 
                if att.on_duty_application:
                    if att.session_from_time and att.session_to_time and not att.session:
                        if att.session_from_time:
                            ot_stime = datetime.strptime(str(att.session_from_time), '%H:%M:%S').time()
                            ot_start_datetime = datetime.combine(shiftdate, ot_stime)
                            if in_time:
                                if in_time<ot_start_datetime:
                                    in_time=in_time
                                else:
                                    in_time=ot_start_datetime
                                    
                            else:
                                in_time=ot_start_datetime
                        if att.session_to_time:
                            ot_etime = datetime.strptime(str(att.session_to_time), '%H:%M:%S').time()
                            ot_end_datetime = datetime.combine(shiftdate, ot_etime)
                            if att.shift=='B' and ot_end_datetime<in_time:
                                shift_end_date=add_days(shiftdate,1)
                                ot_end_datetime=datetime.combine(shift_end_date, ot_etime)
                            if out_time:
                                if out_time<ot_end_datetime:
                                    out_time=ot_end_datetime
                            else:
                                out_time=ot_end_datetime
                    elif att.session and att.from_time and att.to_time:
                        if att.from_time:
                            if in_time:
                                if in_time>att.from_time:
                                    in_time=att.from_time
                            else:
                                in_time=att.from_time
                        if att.to_time:
                            if out_time:
                                if out_time<att.to_time:
                                    out_time=att.to_time
                            else:
                                out_time=att.to_time

                if in_time:
                    shift_start = frappe.get_value("Shift Type", {'name': att.shift}, ['start_time'])
                    shift_stime = datetime.strptime(str(shift_start), '%H:%M:%S').time()
                    shift_start_datetime = datetime.combine(shiftdate, shift_stime)
                    if in_time < shift_start_datetime:
                        in_time = shift_start_datetime
                    else:
                        in_time=in_time
                att_wh = time_diff_in_hours(out_time, in_time)
                tot_wh=0
                p_wh=0
                od_wh=0
                perm_time=0
                if att.att_permission:
                    att_hours = frappe.get_value("Permission", {'name': att.att_permission}, ['total_time'])
                    if att_hours is not None:   
                        perm_time=int(float(att_hours))
                        if perm_time > 0:
                            p_wh = round(att_wh, 2) + perm_time
                            p_hrs=convert_hours_to_hms(p_wh)
                        else:
                            p_wh = round(att_wh, 2) + perm_time
                            p_hrs=convert_hours_to_hms(p_wh)
                else:
                    p_wh = round(att_wh, 2)
                    p_hrs=convert_hours_to_hms(p_wh)
                wh=round(att_wh, 2)
                time_in_standard_format = "{:02d}:{:02d}:{:02d}".format(int(wh), int((wh * 60) % 60), int((wh * 3600) % 60))
                if p_wh < 24.0:
                    twh = time_in_standard_format
                    # print(att.name)
                    # print(twh)
                    frappe.db.set_value('Attendance', att.name, 'total_working_hours', twh)
                    # print("HI")
                    frappe.db.set_value('Attendance', att.name, 'working_hours', p_wh)
                else:
                    twh = "23:59:59"
                    p_hrs='23:59:59'
                    frappe.db.set_value('Attendance', att.name, 'total_working_hours', p_hrs)
                    frappe.db.set_value('Attendance', att.name, 'working_hours', p_wh)
                if p_wh < 4:
                    if att.shift=='C' and p_wh>=3.5:
                        frappe.db.set_value("Attendance", att.name, "status", "Half Day")
                    else:
                        frappe.db.set_value("Attendance", att.name, "status", "Absent")
                elif 4 <= p_wh < 8:
                    if att.shift == "C" and 7 <= p_wh <= 8:
                        frappe.db.set_value("Attendance", att.name, "status", "Present")
                    else:
                        frappe.db.set_value("Attendance", att.name, "status", "Half Day")
                    day_of_week = att.attendance_date.strftime("%A")
                    if day_of_week == "Saturday" and att.employee_type == "Staff":
                        frappe.db.set_value("Attendance", att.name, "status", "Present")
                else:
                    frappe.db.set_value("Attendance", att.name, "status", "Present")
                hh = check_holiday(att.attendance_date,att.employee)
                break_times = [(time(20, 30), time(21, 0)),  (time(12, 30), time(13, 0))]
                if not hh:
                    if att.actual_shift is not None and att.actual_shift == 'WW':
                        shift_start = frappe.get_value("Shift Type", {'name': att.shift}, ['start_time'])
                        shift_stime = datetime.strptime(str(shift_start), '%H:%M:%S').time()
                        shift_start_datetime = datetime.combine(shiftdate, shift_stime)
                        if in_time < shift_start_datetime:
                            in_time = shift_start_datetime
                        else:
                            in_time=in_time
                        out_time = out_time

                        if out_time > in_time:
                            extra_hours=time_diff_in_hours(out_time,in_time)
                            total_extra_hours = out_time - in_time
                            ot_hours = None
                            time_diff = out_time - in_time

                            if time_diff.seconds >= 3600:
                                if time_diff.seconds % 3600 <= 1800:
                                    ot_hours = time(time_diff.seconds // 3600, 0, 0)
                                else:
                                    ot_hours = time(time_diff.seconds // 3600, 30, 0)

                            if ot_hours is not None:
                                ot_hr = round((ot_hours.hour + ot_hours.minute / 60), 1)
                            else:
                                ot_hr = 0
                            deducted_hours = 0
                            break_date = None
                            if att.shift=='C':
                                break_date = add_days(att.attendance_date,+1)	
                            else:
                                break_date = att.attendance_date
                            break_date_str = datetime.strptime(str(break_date), '%Y-%m-%d').date()
                            for break_start, break_end in break_times:
                                break_start_dt = datetime.combine(break_date_str, break_start)
                                break_end_dt = datetime.combine(break_date_str, break_end)
                                if break_start_dt > in_time and break_end_dt < out_time:
                                    deducted_hours += 0.5
                            if ot_hr > 0:
                                ot_hr = ot_hr-deducted_hours
                            total_seconds = int(ot_hr * 3600)  
                            hours, remainder = divmod(total_seconds, 3600)
                            minutes, seconds = divmod(remainder, 60)
                            ot_hours = f"{hours:02}:{minutes:02}:{seconds:02}"
                        if wh>24:
                            frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', '23:00:00')
                            frappe.db.set_value('Attendance', att.name, 'overtime_hours', '23')
                            frappe.db.set_value('Attendance', att.name, 'extra_hours', wh)
                            frappe.db.set_value('Attendance', att.name, 'total_extra_hours', twh)
                        else:
                            frappe.db.set_value('Attendance', att.name, 'extra_hours', wh)
                            frappe.db.set_value('Attendance', att.name, 'total_extra_hours', twh)
                            frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', ot_hours)
                            frappe.db.set_value('Attendance', att.name, 'overtime_hours', ot_hr)
                    else:
                        day_of_week = att.attendance_date.strftime("%A")
                        shift_time = time(0, 0, 0)
                        if day_of_week == "Saturday" and att.employee_type == "Staff":
                            shift_time = frappe.get_value("Shift Type", {'name': att.shift}, ["ot_time"])
                        else:
                            shift_time = frappe.get_value("Shift Type", {'name': att.shift}, ["end_time"])
                        shift_end_time = dt.datetime.strptime(str(shift_time), '%H:%M:%S').time()
                        shift_date = None
                        if att.shift in ["C","B"] :
                            shift_date = add_days(att.attendance_date,+1)	
                        else:
                            shift_date = att.attendance_date
                        ot_date_str = datetime.strptime(str(shift_date), '%Y-%m-%d').date()
                        end_time = datetime.combine(ot_date_str, shift_end_time)
                        end_time = frappe.utils.get_datetime(end_time)
                        out_time = frappe.utils.get_datetime(out_time)
                        if out_time > end_time:
                            extra_hours=time_diff_in_hours(out_time,end_time)
                            total_extra_hours = out_time - end_time
                            ot_hours = None
                            time_diff = out_time - end_time
                            if time_diff.seconds >= 3600:
                                if time_diff.seconds % 3600 <= 1800:
                                    ot_hours = time(time_diff.seconds // 3600, 0, 0)
                                else:
                                    ot_hours = time(time_diff.seconds // 3600, 30, 0)
                            if ot_hours is not None:
                                ot_hr = round((ot_hours.hour + ot_hours.minute / 60), 1)
                            else:
                                ot_hr = 0
                            deducted_hours = 0
                            break_date = None
                            if att.shift=='C':
                                break_date = add_days(att.attendance_date,+1)	
                            else:
                                break_date = att.attendance_date
                            break_date_str = datetime.strptime(str(break_date), '%Y-%m-%d').date()
                            for break_start, break_end in break_times:
                                break_start_dt = datetime.combine(break_date_str, break_start)
                                break_end_dt = datetime.combine(break_date_str, break_end)
                                if break_start_dt > end_time and break_end_dt < out_time:
                                    deducted_hours += 0.5
                            if ot_hr > 0:
                                ot_hr = ot_hr-deducted_hours
                            total_seconds = int(ot_hr * 3600)  
                            hours, remainder = divmod(total_seconds, 3600)
                            minutes, seconds = divmod(remainder, 60)
                            ot_hours = f"{hours:02}:{minutes:02}:{seconds:02}"
                        else:
                            extra_hours = 0.0
                            total_extra_hours = "00:00:00"
                            ot_hours = "00:00:00"
                            ot_hr = 0.0		
                        if wh>24:
                            if day_of_week == "Saturday" and att.employee_type == "Staff":
                                frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', '19:00:00')
                                frappe.db.set_value('Attendance', att.name, 'overtime_hours', '19')
                                frappe.db.set_value('Attendance', att.name, 'extra_hours', round(extra_hours, 2))
                                frappe.db.set_value('Attendance', att.name, 'total_extra_hours', total_extra_hours)
                            else:
                                frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', '15:00:00')
                                frappe.db.set_value('Attendance', att.name, 'overtime_hours', '15')
                                frappe.db.set_value('Attendance', att.name, 'extra_hours', round(extra_hours, 2))
                                frappe.db.set_value('Attendance', att.name, 'total_extra_hours', total_extra_hours)
                        else:	
                            frappe.db.set_value('Attendance', att.name, 'extra_hours', round(extra_hours, 2))
                            frappe.db.set_value('Attendance', att.name, 'total_extra_hours', total_extra_hours)
                            frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', ot_hours)
                            frappe.db.set_value('Attendance', att.name, 'overtime_hours', ot_hr)
                else:
                    if in_time and out_time:
                        shift_start = frappe.get_value("Shift Type", {'name': att.shift}, ['start_time'])
                        shift_stime = datetime.strptime(str(shift_start), '%H:%M:%S').time()
                        shift_start_datetime = datetime.combine(shiftdate, shift_stime)
                        if in_time < shift_start_datetime:
                            in_time = shift_start_datetime
                        else:
                            in_time=in_time
                        out_time = out_time

                        if out_time > in_time:
                            extra_hours=time_diff_in_hours(out_time,in_time)
                            total_extra_hours = out_time - in_time
                            ot_hours = None
                            time_diff = out_time - in_time

                            if time_diff.seconds >= 3600:
                                if time_diff.seconds % 3600 <= 1800:
                                    ot_hours = time(time_diff.seconds // 3600, 0, 0)
                                else:
                                    ot_hours = time(time_diff.seconds // 3600, 30, 0)

                            if ot_hours is not None:
                                ot_hr = round((ot_hours.hour + ot_hours.minute / 60), 1)
                            else:
                                ot_hr = 0
                            break_times = [
                            (time(20, 30), time(21, 0)),  
                            (time(12, 30), time(13, 0))  
                            ]
                            deducted_hours = 0
                            break_date = None
                            if att.shift=='C':
                                break_date = add_days(att.attendance_date,+1)	
                            else:
                                break_date = att.attendance_date
                            break_date_str = datetime.strptime(str(break_date), '%Y-%m-%d').date()
                            for break_start, break_end in break_times:
                                break_start_dt = datetime.combine(break_date_str, break_start)
                                break_end_dt = datetime.combine(break_date_str, break_end)
                                if break_start_dt > in_time and break_end_dt < out_time:
                                    deducted_hours += 0.5
                            if ot_hr > 0:
                                ot_hr = ot_hr-deducted_hours
                            total_seconds = int(ot_hr * 3600)  
                            hours, remainder = divmod(total_seconds, 3600)
                            minutes, seconds = divmod(remainder, 60)
                            ot_hours = f"{hours:02}:{minutes:02}:{seconds:02}"
                        else:
                            ot_hours = '00:00:00'
                            ot_hr=0
                        
                        fh_holiday=check_nhfh(att.attendance_date,att.employee)
                        if att.employee_type=='Contract Employee' and fh_holiday=='FH':
                            ot_hr=ot_hr*2
                            total_seconds = int(ot_hr * 3600)  
                            hours, remainder = divmod(total_seconds, 3600)
                            minutes, seconds = divmod(remainder, 60)
                            ot_hours = f"{hours:02}:{minutes:02}:{seconds:02}"
                            if ot_hr>=24:
                                ot_hr=23
                                ot_hours='23:00:00'
                        if wh>24:
                            frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', '23:00:00')
                            frappe.db.set_value('Attendance', att.name, 'overtime_hours', '23')
                            frappe.db.set_value('Attendance', att.name, 'extra_hours', wh)
                            frappe.db.set_value('Attendance', att.name, 'total_extra_hours', twh)
                        else:
                            frappe.db.set_value('Attendance', att.name, 'extra_hours', wh)
                            frappe.db.set_value('Attendance', att.name, 'total_extra_hours', twh)
                            frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', ot_hours)
                            frappe.db.set_value('Attendance', att.name, 'overtime_hours', ot_hr)
                    else:
                        frappe.db.set_value('Attendance', att.name, 'total_working_hours', "00:00:00")
                        frappe.db.set_value('Attendance', att.name, 'working_hours', "0.0")
                        frappe.db.set_value('Attendance', att.name, 'extra_hours', "0.0")
                        frappe.db.set_value('Attendance', att.name, 'total_extra_hours', "00:00:00")
                        frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', "00:00:00")
                        frappe.db.set_value('Attendance', att.name, 'overtime_hours', "0.0")
                        frappe.db.set_value('Attendance', att.name, 'late_entry_time', "00:00:00")
                        frappe.db.set_value('Attendance', att.name, 'early_out_time',"00:00:00")
                if in_time > out_time:
                    frappe.db.set_value('Attendance', att.name, 'total_working_hours', 0)
                    frappe.db.set_value('Attendance', att.name, 'working_hours', 0)
                    frappe.db.set_value('Attendance', att.name, 'status', 'Absent')
                    frappe.db.set_value('Attendance', att.name, 'extra_hours',0)
                    frappe.db.set_value('Attendance', att.name, 'total_extra_hours', 0)
                    frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', 0)
                    frappe.db.set_value('Attendance', att.name, 'overtime_hours', 0)
            else:
                frappe.db.set_value('Attendance', att.name, 'total_working_hours', "00:00:00")
                frappe.db.set_value('Attendance', att.name, 'working_hours', "0.0")
                frappe.db.set_value('Attendance', att.name, 'extra_hours', "0.0")
                frappe.db.set_value('Attendance', att.name, 'total_extra_hours', "00:00:00")
                frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', "00:00:00")
                frappe.db.set_value('Attendance', att.name, 'overtime_hours', "0.0")
                frappe.db.set_value('Attendance', att.name, 'late_entry_time', "00:00:00")
                frappe.db.set_value('Attendance', att.name, 'early_out_time',"00:00:00")
        
   
@frappe.whitelist()
def mark_wh_ot_with_employee(from_date, to_date, employee):
    from_date=add_days(from_date,-1)
    attendance = frappe.db.get_all('Attendance', {'attendance_date': ('between', (from_date,to_date)),'employee':employee,'docstatus': ('!=', '2')}, ['*'])
    for att in attendance:
        if not att.attendance_upload:
            if att.shift and (att.in_time or ((att.session_from_time or (att.session and att.from_time)) and att.on_duty_application))and (att.out_time or ((att.session_to_time or (att.session and att.to_time)) and att.on_duty_application)):
                # frappe.errprint("TEST")
                in_time = att.in_time
                out_time = att.out_time
                if att.shift == 'C':
                    shiftdate = add_days(att.attendance_date,+1) 	
                else:
                    shiftdate = att.attendance_date 
                if att.on_duty_application:
                    if att.session_from_time and att.session_to_time and not att.session:
                        if att.session_from_time:
                            ot_stime = datetime.strptime(str(att.session_from_time), '%H:%M:%S').time()
                            ot_start_datetime = datetime.combine(shiftdate, ot_stime)
                            if in_time:
                                if in_time<ot_start_datetime:
                                    in_time=in_time
                                else:
                                    in_time=ot_start_datetime
                                    
                            else:
                                in_time=ot_start_datetime
                        if att.session_to_time:
                            ot_etime = datetime.strptime(str(att.session_to_time), '%H:%M:%S').time()
                            ot_end_datetime = datetime.combine(shiftdate, ot_etime)
                            if att.shift=='B' and ot_end_datetime<in_time:
                                shift_end_date=add_days(shiftdate,1)
                                ot_end_datetime=datetime.combine(shift_end_date, ot_etime)
                            if out_time:
                                if out_time<ot_end_datetime:
                                    out_time=ot_end_datetime
                            else:
                                out_time=ot_end_datetime
                    elif att.session and att.from_time and att.to_time:
                        if att.from_time:
                            if in_time:
                                if in_time>att.from_time:
                                    in_time=att.from_time
                            else:
                                in_time=att.from_time
                        if att.to_time:
                            if out_time:
                                if out_time<att.to_time:
                                    out_time=att.to_time
                            else:
                                out_time=att.to_time
                # frappe.errprint(in_time)
                # frappe.errprint(out_time)
                if in_time:
                    shift_start = frappe.get_value("Shift Type", {'name': att.shift}, ['start_time'])
                    shift_stime = datetime.strptime(str(shift_start), '%H:%M:%S').time()
                    shift_start_datetime = datetime.combine(shiftdate, shift_stime)
                    if in_time < shift_start_datetime:
                        in_time = shift_start_datetime
                    else:
                        in_time=in_time
                att_wh = time_diff_in_hours(out_time, in_time)
                tot_wh=0
                p_wh=0
                od_wh=0
                perm_time=0
                if att.att_permission:
                    att_hours = frappe.get_value("Permission", {'name': att.att_permission}, ['total_time'])
                    if att_hours is not None:   
                        perm_time=int(float(att_hours))
                        if perm_time > 0:
                            p_wh = round(att_wh, 2) + perm_time
                            p_hrs=convert_hours_to_hms(p_wh)
                        else:
                            p_wh = round(att_wh, 2) + perm_time
                            p_hrs=convert_hours_to_hms(p_wh)
                else:
                    p_wh = round(att_wh, 2)
                    p_hrs=convert_hours_to_hms(p_wh)
                wh=round(att_wh, 2)
                time_in_standard_format = "{:02d}:{:02d}:{:02d}".format(int(wh), int((wh * 60) % 60), int((wh * 3600) % 60))
                if p_wh < 24.0:
                    twh = time_in_standard_format
                    frappe.db.set_value('Attendance', att.name, 'total_working_hours', twh)
                    frappe.db.set_value('Attendance', att.name, 'working_hours', p_wh)
                else:
                    twh = "23:59:59"
                    p_hrs='23:59:59'
                    frappe.db.set_value('Attendance', att.name, 'total_working_hours', p_hrs)
                    frappe.db.set_value('Attendance', att.name, 'working_hours', p_wh)
                if p_wh < 4:
                    if att.shift=='C' and p_wh>=3.5:
                        frappe.db.set_value("Attendance", att.name, "status", "Half Day")
                    else:
                        frappe.db.set_value("Attendance", att.name, "status", "Absent")
                elif 4 <= p_wh < 8:
                    if att.shift == "C" and 7 <= p_wh <= 8:
                        frappe.db.set_value("Attendance", att.name, "status", "Present")
                    else:
                        frappe.db.set_value("Attendance", att.name, "status", "Half Day")
                    day_of_week = att.attendance_date.strftime("%A")
                    if day_of_week == "Saturday" and att.employee_type == "Staff":
                        frappe.db.set_value("Attendance", att.name, "status", "Present")
                else:
                    frappe.db.set_value("Attendance", att.name, "status", "Present")
                hh = check_holiday(att.attendance_date,att.employee)
                break_times = [(time(20, 30), time(21, 0)),  (time(12, 30), time(13, 0))]
                if not hh:
                    if att.actual_shift is not None and att.actual_shift == 'WW':
                        shift_start = frappe.get_value("Shift Type", {'name': att.shift}, ['start_time'])
                        shift_stime = datetime.strptime(str(shift_start), '%H:%M:%S').time()
                        shift_start_datetime = datetime.combine(shiftdate, shift_stime)
                        if in_time < shift_start_datetime:
                            in_time = shift_start_datetime
                        else:
                            in_time=in_time
                        out_time = out_time

                        if out_time > in_time:
                            extra_hours=time_diff_in_hours(out_time,in_time)
                            total_extra_hours = out_time - in_time
                            ot_hours = None
                            time_diff = out_time - in_time

                            if time_diff.seconds >= 3600:
                                if time_diff.seconds % 3600 <= 1800:
                                    ot_hours = time(time_diff.seconds // 3600, 0, 0)
                                else:
                                    ot_hours = time(time_diff.seconds // 3600, 30, 0)

                            if ot_hours is not None:
                                ot_hr = round((ot_hours.hour + ot_hours.minute / 60), 1)
                            else:
                                ot_hr = 0
                            deducted_hours = 0
                            break_date = None
                            if att.shift=='C':
                                break_date = add_days(att.attendance_date,+1)	
                            else:
                                break_date = att.attendance_date
                            break_date_str = datetime.strptime(str(break_date), '%Y-%m-%d').date()
                            for break_start, break_end in break_times:
                                break_start_dt = datetime.combine(break_date_str, break_start)
                                break_end_dt = datetime.combine(break_date_str, break_end)
                                if break_start_dt > in_time and break_end_dt < out_time:
                                    deducted_hours += 0.5
                            if ot_hr > 0:
                                ot_hr = ot_hr-deducted_hours
                            total_seconds = int(ot_hr * 3600)  
                            hours, remainder = divmod(total_seconds, 3600)
                            minutes, seconds = divmod(remainder, 60)
                            ot_hours = f"{hours:02}:{minutes:02}:{seconds:02}"
                        if wh>24:
                            frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', '23:00:00')
                            frappe.db.set_value('Attendance', att.name, 'overtime_hours', '23')
                            frappe.db.set_value('Attendance', att.name, 'extra_hours', wh)
                            frappe.db.set_value('Attendance', att.name, 'total_extra_hours', twh)
                        else:
                            frappe.db.set_value('Attendance', att.name, 'extra_hours', wh)
                            frappe.db.set_value('Attendance', att.name, 'total_extra_hours', twh)
                            frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', ot_hours)
                            frappe.db.set_value('Attendance', att.name, 'overtime_hours', ot_hr)
                    else:
                        day_of_week = att.attendance_date.strftime("%A")
                        shift_time = time(0, 0, 0)
                        if day_of_week == "Saturday" and att.employee_type == "Staff":
                            shift_time = frappe.get_value("Shift Type", {'name': att.shift}, ["ot_time"])
                        else:
                            shift_time = frappe.get_value("Shift Type", {'name': att.shift}, ["end_time"])
                        shift_end_time = dt.datetime.strptime(str(shift_time), '%H:%M:%S').time()
                        shift_date = None
                        if att.shift in ["C","B"] :
                            shift_date = add_days(att.attendance_date,+1)	
                        else:
                            shift_date = att.attendance_date
                        ot_date_str = datetime.strptime(str(shift_date), '%Y-%m-%d').date()
                        end_time = datetime.combine(ot_date_str, shift_end_time)
                        end_time = frappe.utils.get_datetime(end_time)
                        out_time = frappe.utils.get_datetime(out_time)
                        if out_time > end_time:
                            extra_hours=time_diff_in_hours(out_time,end_time)
                            total_extra_hours = out_time - end_time
                            ot_hours = None
                            time_diff = out_time - end_time
                            if time_diff.seconds >= 3600:
                                if time_diff.seconds % 3600 <= 1800:
                                    ot_hours = time(time_diff.seconds // 3600, 0, 0)
                                else:
                                    ot_hours = time(time_diff.seconds // 3600, 30, 0)
                            if ot_hours is not None:
                                ot_hr = round((ot_hours.hour + ot_hours.minute / 60), 1)
                            else:
                                ot_hr = 0
                            deducted_hours = 0
                            break_date = None
                            if att.shift=='C':
                                break_date = add_days(att.attendance_date,+1)	
                            else:
                                break_date = att.attendance_date
                            break_date_str = datetime.strptime(str(break_date), '%Y-%m-%d').date()
                            for break_start, break_end in break_times:
                                break_start_dt = datetime.combine(break_date_str, break_start)
                                break_end_dt = datetime.combine(break_date_str, break_end)
                                if break_start_dt > end_time and break_end_dt < out_time:
                                    deducted_hours += 0.5
                            if ot_hr > 0:
                                ot_hr = ot_hr-deducted_hours
                            total_seconds = int(ot_hr * 3600)  
                            hours, remainder = divmod(total_seconds, 3600)
                            minutes, seconds = divmod(remainder, 60)
                            ot_hours = f"{hours:02}:{minutes:02}:{seconds:02}"
                        else:
                            extra_hours = 0.0
                            total_extra_hours = "00:00:00"
                            ot_hours = "00:00:00"
                            ot_hr = 0.0	
                        if wh>24:
                            if day_of_week == "Saturday" and att.employee_type == "Staff":
                                frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', '19:00:00')
                                frappe.db.set_value('Attendance', att.name, 'overtime_hours', '19')
                                frappe.db.set_value('Attendance', att.name, 'extra_hours', round(extra_hours, 2))
                                frappe.db.set_value('Attendance', att.name, 'total_extra_hours', total_extra_hours)
                            else:
                                frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', '15:00:00')
                                frappe.db.set_value('Attendance', att.name, 'overtime_hours', '15')
                                frappe.db.set_value('Attendance', att.name, 'extra_hours', round(extra_hours, 2))
                                frappe.db.set_value('Attendance', att.name, 'total_extra_hours', total_extra_hours)
                        else:	
                            frappe.db.set_value('Attendance', att.name, 'extra_hours', round(extra_hours, 2))
                            frappe.db.set_value('Attendance', att.name, 'total_extra_hours', total_extra_hours)
                            frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', ot_hours)
                            frappe.db.set_value('Attendance', att.name, 'overtime_hours', ot_hr)
                else:
                    frappe.errprint("Hello")
                    if in_time and out_time:
                        shift_start = frappe.get_value("Shift Type", {'name': att.shift}, ['start_time'])
                        shift_stime = datetime.strptime(str(shift_start), '%H:%M:%S').time()
                        shift_start_datetime = datetime.combine(shiftdate, shift_stime)
                        if in_time < shift_start_datetime:
                            in_time = shift_start_datetime
                        else:
                            in_time=in_time
                        out_time = out_time

                        if out_time > in_time:
                            frappe.errprint("Hello1")
                            extra_hours=time_diff_in_hours(out_time,in_time)
                            total_extra_hours = out_time - in_time
                            ot_hours = None
                            time_diff = out_time - in_time

                            if time_diff.seconds >= 3600:
                                if time_diff.seconds % 3600 <= 1800:
                                    ot_hours = time(time_diff.seconds // 3600, 0, 0)
                                else:
                                    ot_hours = time(time_diff.seconds // 3600, 30, 0)

                            if ot_hours is not None:
                                ot_hr = round((ot_hours.hour + ot_hours.minute / 60), 1)
                            else:
                                ot_hr = 0
                            break_times = [
                            (time(20, 30), time(21, 0)),  
                            (time(12, 30), time(13, 0))  
                            ]
                            deducted_hours = 0
                            break_date = None
                            if att.shift=='C':
                                break_date = add_days(att.attendance_date,+1)	
                            else:
                                break_date = att.attendance_date
                            break_date_str = datetime.strptime(str(break_date), '%Y-%m-%d').date()
                            for break_start, break_end in break_times:
                                break_start_dt = datetime.combine(break_date_str, break_start)
                                break_end_dt = datetime.combine(break_date_str, break_end)
                                if break_start_dt > in_time and break_end_dt < out_time:
                                    deducted_hours += 0.5
                            if ot_hr > 0:
                                ot_hr = ot_hr-deducted_hours
                            total_seconds = int(ot_hr * 3600)  
                            hours, remainder = divmod(total_seconds, 3600)
                            minutes, seconds = divmod(remainder, 60)
                            ot_hours = f"{hours:02}:{minutes:02}:{seconds:02}"
                        fh_holiday=check_nhfh(att.attendance_date,att.employee)
                        if att.employee_type=='Contract Employee' and fh_holiday=='FH':
                            ot_hr=ot_hr*2
                            total_seconds = int(ot_hr * 3600)  
                            hours, remainder = divmod(total_seconds, 3600)
                            minutes, seconds = divmod(remainder, 60)
                            ot_hours = f"{hours:02}:{minutes:02}:{seconds:02}"
                            if ot_hr>=24:
                                ot_hr=23
                                ot_hours='23:00:00'
                        if wh>24:
                            frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', '23:00:00')
                            frappe.db.set_value('Attendance', att.name, 'overtime_hours', '23')
                            frappe.db.set_value('Attendance', att.name, 'extra_hours', wh)
                            frappe.db.set_value('Attendance', att.name, 'total_extra_hours', twh)
                        else:
                            frappe.db.set_value('Attendance', att.name, 'extra_hours', wh)
                            frappe.db.set_value('Attendance', att.name, 'total_extra_hours', twh)
                            frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', ot_hours)
                            frappe.db.set_value('Attendance', att.name, 'overtime_hours', ot_hr)
                    else:
                        frappe.db.set_value('Attendance', att.name, 'total_working_hours', "00:00:00")
                        frappe.db.set_value('Attendance', att.name, 'working_hours', "0.0")
                        frappe.db.set_value('Attendance', att.name, 'extra_hours', "0.0")
                        frappe.db.set_value('Attendance', att.name, 'total_extra_hours', "00:00:00")
                        frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', "00:00:00")
                        frappe.db.set_value('Attendance', att.name, 'overtime_hours', "0.0")
                        frappe.db.set_value('Attendance', att.name, 'late_entry_time', "00:00:00")
                        frappe.db.set_value('Attendance', att.name, 'early_out_time',"00:00:00")
                if in_time > out_time:
                    frappe.db.set_value('Attendance', att.name, 'total_working_hours', 0)
                    frappe.db.set_value('Attendance', att.name, 'working_hours', 0)
                    frappe.db.set_value('Attendance', att.name, 'status', 'Absent')
                    frappe.db.set_value('Attendance', att.name, 'extra_hours',0)
                    frappe.db.set_value('Attendance', att.name, 'total_extra_hours', 0)
                    frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', 0)
                    frappe.db.set_value('Attendance', att.name, 'overtime_hours', 0)
            else:
                frappe.db.set_value('Attendance', att.name, 'total_working_hours', "00:00:00")
                frappe.db.set_value('Attendance', att.name, 'working_hours', "0.0")
                frappe.db.set_value('Attendance', att.name, 'extra_hours', "0.0")
                frappe.db.set_value('Attendance', att.name, 'total_extra_hours', "00:00:00")
                frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', "00:00:00")
                frappe.db.set_value('Attendance', att.name, 'overtime_hours', "0.0")
                frappe.db.set_value('Attendance', att.name, 'late_entry_time', "00:00:00")
                frappe.db.set_value('Attendance', att.name, 'early_out_time',"00:00:00")
        
       

@frappe.whitelist()
def mark_wh_ot_with_employee_type(from_date,to_date,employee_type):
    from_date=add_days(from_date,-1)
    attendance = frappe.db.get_all('Attendance', {'attendance_date': ('between', (from_date,to_date)),'employee_type':employee_type,'docstatus': ('!=', '2')}, ['*'])
    for att in attendance:
        if not att.attendance_upload:
            if att.shift and (att.in_time or ((att.session_from_time or (att.session and att.from_time)) and att.on_duty_application))and (att.out_time or ((att.session_to_time or (att.session and att.to_time)) and att.on_duty_application)):
                # frappe.errprint("TEST")
                in_time = att.in_time
                out_time = att.out_time
                if att.shift == 'C':
                    shiftdate = add_days(att.attendance_date,+1) 	
                else:
                    shiftdate = att.attendance_date 
                if att.on_duty_application:
                    if att.session_from_time and att.session_to_time and not att.session:
                        if att.session_from_time:
                            ot_stime = datetime.strptime(str(att.session_from_time), '%H:%M:%S').time()
                            ot_start_datetime = datetime.combine(shiftdate, ot_stime)
                            if in_time:
                                if in_time<ot_start_datetime:
                                    in_time=in_time
                                else:
                                    in_time=ot_start_datetime
                                    
                            else:
                                in_time=ot_start_datetime
                        if att.session_to_time:
                            ot_etime = datetime.strptime(str(att.session_to_time), '%H:%M:%S').time()
                            ot_end_datetime = datetime.combine(shiftdate, ot_etime)
                            if att.shift=='B' and ot_end_datetime<in_time:
                                shift_end_date=add_days(shiftdate,1)
                                ot_end_datetime=datetime.combine(shift_end_date, ot_etime)
                            if out_time:
                                if out_time<ot_end_datetime:
                                    out_time=ot_end_datetime
                            else:
                                out_time=ot_end_datetime
                    elif att.session and att.from_time and att.to_time:
                        if att.from_time:
                            if in_time:
                                if in_time>att.from_time:
                                    in_time=att.from_time
                            else:
                                in_time=att.from_time
                        if att.to_time:
                            if out_time:
                                if out_time<att.to_time:
                                    out_time=att.to_time
                            else:
                                out_time=att.to_time
                # frappe.errprint(in_time)
                # frappe.errprint(out_time)
                if in_time:
                    shift_start = frappe.get_value("Shift Type", {'name': att.shift}, ['start_time'])
                    shift_stime = datetime.strptime(str(shift_start), '%H:%M:%S').time()
                    shift_start_datetime = datetime.combine(shiftdate, shift_stime)
                    if in_time < shift_start_datetime:
                        in_time = shift_start_datetime
                    else:
                        in_time=in_time
                att_wh = time_diff_in_hours(out_time, in_time)
                tot_wh=0
                p_wh=0
                od_wh=0
                perm_time=0
                if att.att_permission is not None:
                    att_hours=shift_start = frappe.get_value("Permission", {'name': att.att_permission}, ['total_time'])
                    if att_hours is not None:   
                        perm_time=int(float(att_hours))
                        if perm_time > 0:
                            p_wh = round(att_wh, 2) + perm_time
                            p_hrs=convert_hours_to_hms(p_wh)
                        else:
                            p_wh = round(att_wh, 2) + perm_time
                            p_hrs=convert_hours_to_hms(p_wh)
                else:
                    p_wh = round(att_wh, 2)
                    p_hrs=convert_hours_to_hms(p_wh)
                wh=round(att_wh, 2)
                time_in_standard_format = "{:02d}:{:02d}:{:02d}".format(int(wh), int((wh * 60) % 60), int((wh * 3600) % 60))
                if p_wh < 24.0:
                    twh = time_in_standard_format
                    frappe.db.set_value('Attendance', att.name, 'total_working_hours', twh)
                    frappe.db.set_value('Attendance', att.name, 'working_hours', p_wh)
                else:
                    twh = "23:59:59"
                    p_hrs='23:59:59'
                    frappe.db.set_value('Attendance', att.name, 'total_working_hours', p_hrs)
                    frappe.db.set_value('Attendance', att.name, 'working_hours', p_wh)
                if p_wh < 4:
                    if att.shift=='C' and p_wh>=3.5:
                        frappe.db.set_value("Attendance", att.name, "status", "Half Day")
                    else:
                        frappe.db.set_value("Attendance", att.name, "status", "Absent")
                elif 4 <= p_wh < 8:
                    if att.shift == "C" and 7 <= p_wh <= 8:
                        frappe.db.set_value("Attendance", att.name, "status", "Present")
                    else:
                        frappe.db.set_value("Attendance", att.name, "status", "Half Day")
                    day_of_week = att.attendance_date.strftime("%A")
                    if day_of_week == "Saturday" and att.employee_type == "Staff":
                        frappe.db.set_value("Attendance", att.name, "status", "Present")
                else:
                    frappe.db.set_value("Attendance", att.name, "status", "Present")
                hh = check_holiday(att.attendance_date,att.employee)
                break_times = [(time(20, 30), time(21, 0)),  (time(12, 30), time(13, 0))]
                if not hh:
                    if att.actual_shift is not None and att.actual_shift == 'WW':
                        shift_start = frappe.get_value("Shift Type", {'name': att.shift}, ['start_time'])
                        shift_stime = datetime.strptime(str(shift_start), '%H:%M:%S').time()
                        shift_start_datetime = datetime.combine(shiftdate, shift_stime)
                        if in_time < shift_start_datetime:
                            in_time = shift_start_datetime
                        else:
                            in_time=in_time
                        out_time = out_time

                        if out_time > in_time:
                            extra_hours=time_diff_in_hours(out_time,in_time)
                            total_extra_hours = out_time - in_time
                            ot_hours = None
                            time_diff = out_time - in_time

                            if time_diff.seconds >= 3600:
                                if time_diff.seconds % 3600 <= 1800:
                                    ot_hours = time(time_diff.seconds // 3600, 0, 0)
                                else:
                                    ot_hours = time(time_diff.seconds // 3600, 30, 0)

                            if ot_hours is not None:
                                ot_hr = round((ot_hours.hour + ot_hours.minute / 60), 1)
                            else:
                                ot_hr = 0
                            deducted_hours = 0
                            break_date = None
                            if att.shift=='C':
                                break_date = add_days(att.attendance_date,+1)	
                            else:
                                break_date = att.attendance_date
                            break_date_str = datetime.strptime(str(break_date), '%Y-%m-%d').date()
                            for break_start, break_end in break_times:
                                break_start_dt = datetime.combine(break_date_str, break_start)
                                break_end_dt = datetime.combine(break_date_str, break_end)
                                if break_start_dt > in_time and break_end_dt < out_time:
                                    deducted_hours += 0.5
                            if ot_hr > 0:
                                ot_hr = ot_hr-deducted_hours
                            total_seconds = int(ot_hr * 3600)  
                            hours, remainder = divmod(total_seconds, 3600)
                            minutes, seconds = divmod(remainder, 60)
                            ot_hours = f"{hours:02}:{minutes:02}:{seconds:02}"
                        if wh>24:
                            frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', '23:00:00')
                            frappe.db.set_value('Attendance', att.name, 'overtime_hours', '23')
                            frappe.db.set_value('Attendance', att.name, 'extra_hours', wh)
                            frappe.db.set_value('Attendance', att.name, 'total_extra_hours', twh)
                        else:
                            frappe.db.set_value('Attendance', att.name, 'extra_hours', wh)
                            frappe.db.set_value('Attendance', att.name, 'total_extra_hours', twh)
                            frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', ot_hours)
                            frappe.db.set_value('Attendance', att.name, 'overtime_hours', ot_hr)
                    else:
                        day_of_week = att.attendance_date.strftime("%A")
                        shift_time = time(0, 0, 0)
                        if day_of_week == "Saturday" and att.employee_type == "Staff":
                            shift_time = frappe.get_value("Shift Type", {'name': att.shift}, ["ot_time"])
                        else:
                            shift_time = frappe.get_value("Shift Type", {'name': att.shift}, ["end_time"])
                        shift_end_time = dt.datetime.strptime(str(shift_time), '%H:%M:%S').time()
                        shift_date = None
                        if att.shift in ["C","B"] :
                            shift_date = add_days(att.attendance_date,+1)	
                        else:
                            shift_date = att.attendance_date
                        ot_date_str = datetime.strptime(str(shift_date), '%Y-%m-%d').date()
                        end_time = datetime.combine(ot_date_str, shift_end_time)
                        end_time = frappe.utils.get_datetime(end_time)
                        out_time = frappe.utils.get_datetime(out_time)
                        if out_time > end_time:
                            extra_hours=time_diff_in_hours(out_time,end_time)
                            total_extra_hours = out_time - end_time
                            ot_hours = None
                            time_diff = out_time - end_time
                            if time_diff.seconds >= 3600:
                                if time_diff.seconds % 3600 <= 1800:
                                    ot_hours = time(time_diff.seconds // 3600, 0, 0)
                                else:
                                    ot_hours = time(time_diff.seconds // 3600, 30, 0)
                            if ot_hours is not None:
                                ot_hr = round((ot_hours.hour + ot_hours.minute / 60), 1)
                            else:
                                ot_hr = 0
                            deducted_hours = 0
                            break_date = None
                            if att.shift=='C':
                                break_date = add_days(att.attendance_date,+1)	
                            else:
                                break_date = att.attendance_date
                            break_date_str = datetime.strptime(str(break_date), '%Y-%m-%d').date()
                            for break_start, break_end in break_times:
                                break_start_dt = datetime.combine(break_date_str, break_start)
                                break_end_dt = datetime.combine(break_date_str, break_end)
                                if break_start_dt > end_time and break_end_dt < out_time:
                                    deducted_hours += 0.5
                            if ot_hr > 0:
                                ot_hr = ot_hr-deducted_hours
                            total_seconds = int(ot_hr * 3600)  
                            hours, remainder = divmod(total_seconds, 3600)
                            minutes, seconds = divmod(remainder, 60)
                            ot_hours = f"{hours:02}:{minutes:02}:{seconds:02}"
                        else:
                            extra_hours = 0.0
                            total_extra_hours = "00:00:00"
                            ot_hours = "00:00:00"
                            ot_hr = 0.0		
                        if wh>24:
                            if day_of_week == "Saturday" and att.employee_type == "Staff":
                                frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', '19:00:00')
                                frappe.db.set_value('Attendance', att.name, 'overtime_hours', '19')
                                frappe.db.set_value('Attendance', att.name, 'extra_hours', round(extra_hours, 2))
                                frappe.db.set_value('Attendance', att.name, 'total_extra_hours', total_extra_hours)
                            else:
                                frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', '15:00:00')
                                frappe.db.set_value('Attendance', att.name, 'overtime_hours', '15')
                                frappe.db.set_value('Attendance', att.name, 'extra_hours', round(extra_hours, 2))
                                frappe.db.set_value('Attendance', att.name, 'total_extra_hours', total_extra_hours)
                        else:	
                            frappe.db.set_value('Attendance', att.name, 'extra_hours', round(extra_hours, 2))
                            frappe.db.set_value('Attendance', att.name, 'total_extra_hours', total_extra_hours)
                            frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', ot_hours)
                            frappe.db.set_value('Attendance', att.name, 'overtime_hours', ot_hr)
                else:
                    if in_time and out_time:
                        shift_start = frappe.get_value("Shift Type", {'name': att.shift}, ['start_time'])
                        shift_stime = datetime.strptime(str(shift_start), '%H:%M:%S').time()
                        shift_start_datetime = datetime.combine(shiftdate, shift_stime)
                        if in_time < shift_start_datetime:
                            in_time = shift_start_datetime
                        else:
                            in_time=in_time
                        out_time = out_time

                        if out_time > in_time:
                            extra_hours=time_diff_in_hours(out_time,in_time)
                            total_extra_hours = out_time - in_time
                            ot_hours = None
                            time_diff = out_time - in_time

                            if time_diff.seconds >= 3600:
                                if time_diff.seconds % 3600 <= 1800:
                                    ot_hours = time(time_diff.seconds // 3600, 0, 0)
                                else:
                                    ot_hours = time(time_diff.seconds // 3600, 30, 0)

                            if ot_hours is not None:
                                ot_hr = round((ot_hours.hour + ot_hours.minute / 60), 1)
                            else:
                                ot_hr = 0
                            break_times = [
                            (time(20, 30), time(21, 0)),  
                            (time(12, 30), time(13, 0))  
                            ]
                            deducted_hours = 0
                            break_date = None
                            if att.shift=='C':
                                break_date = add_days(att.attendance_date,+1)	
                            else:
                                break_date = att.attendance_date
                            break_date_str = datetime.strptime(str(break_date), '%Y-%m-%d').date()
                            for break_start, break_end in break_times:
                                break_start_dt = datetime.combine(break_date_str, break_start)
                                break_end_dt = datetime.combine(break_date_str, break_end)
                                if break_start_dt > in_time and break_end_dt < out_time:
                                    deducted_hours += 0.5
                            if ot_hr > 0:
                                ot_hr = ot_hr-deducted_hours
                            total_seconds = int(ot_hr * 3600)  
                            hours, remainder = divmod(total_seconds, 3600)
                            minutes, seconds = divmod(remainder, 60)
                            ot_hours = f"{hours:02}:{minutes:02}:{seconds:02}"
                        fh_holiday=check_nhfh(att.attendance_date,att.employee)
                        if att.employee_type=='Contract Employee' and fh_holiday=='FH':
                            ot_hr=ot_hr*2
                            total_seconds = int(ot_hr * 3600)  
                            hours, remainder = divmod(total_seconds, 3600)
                            minutes, seconds = divmod(remainder, 60)
                            ot_hours = f"{hours:02}:{minutes:02}:{seconds:02}"
                            if ot_hr>=24:
                                ot_hr=23
                                ot_hours='23:00:00'
                        if wh>24:
                            frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', '23:00:00')
                            frappe.db.set_value('Attendance', att.name, 'overtime_hours', '23')
                            frappe.db.set_value('Attendance', att.name, 'extra_hours', wh)
                            frappe.db.set_value('Attendance', att.name, 'total_extra_hours', twh)
                        else:
                            frappe.db.set_value('Attendance', att.name, 'extra_hours', wh)
                            frappe.db.set_value('Attendance', att.name, 'total_extra_hours', twh)
                            frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', ot_hours)
                            frappe.db.set_value('Attendance', att.name, 'overtime_hours', ot_hr)
                    else:
                        frappe.db.set_value('Attendance', att.name, 'total_working_hours', "00:00:00")
                        frappe.db.set_value('Attendance', att.name, 'working_hours', "0.0")
                        frappe.db.set_value('Attendance', att.name, 'extra_hours', "0.0")
                        frappe.db.set_value('Attendance', att.name, 'total_extra_hours', "00:00:00")
                        frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', "00:00:00")
                        frappe.db.set_value('Attendance', att.name, 'overtime_hours', "0.0")
                        frappe.db.set_value('Attendance', att.name, 'late_entry_time', "00:00:00")
                        frappe.db.set_value('Attendance', att.name, 'early_out_time',"00:00:00")
                if in_time > out_time:
                    frappe.db.set_value('Attendance', att.name, 'total_working_hours', 0)
                    frappe.db.set_value('Attendance', att.name, 'working_hours', 0)
                    frappe.db.set_value('Attendance', att.name, 'status', 'Absent')
                    frappe.db.set_value('Attendance', att.name, 'extra_hours',0)
                    frappe.db.set_value('Attendance', att.name, 'total_extra_hours', 0)
                    frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', 0)
                    frappe.db.set_value('Attendance', att.name, 'overtime_hours', 0)
            else:
                frappe.db.set_value('Attendance', att.name, 'total_working_hours', "00:00:00")
                frappe.db.set_value('Attendance', att.name, 'working_hours', "0.0")
                frappe.db.set_value('Attendance', att.name, 'extra_hours', "0.0")
                frappe.db.set_value('Attendance', att.name, 'total_extra_hours', "00:00:00")
                frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', "00:00:00")
                frappe.db.set_value('Attendance', att.name, 'overtime_hours', "0.0")
                frappe.db.set_value('Attendance', att.name, 'late_entry_time', "00:00:00")
                frappe.db.set_value('Attendance', att.name, 'early_out_time',"00:00:00")
        
@frappe.whitelist()
def mark_wh_ot_with_con_name(from_date,to_date,employee_type,con_name):
    from_date=add_days(from_date,-1)
    attendance = frappe.db.get_all('Attendance', {'attendance_date': ('between', (from_date,to_date)),'employee_type':employee_type,'contractor':con_name,'docstatus': ('!=', '2')}, ['*'])
    for att in attendance:
        if not att.attendance_upload:
            if att.shift and (att.in_time or ((att.session_from_time or (att.session and att.from_time)) and att.on_duty_application))and (att.out_time or ((att.session_to_time or (att.session and att.to_time)) and att.on_duty_application)):
                # frappe.errprint("TEST")
                in_time = att.in_time
                out_time = att.out_time
                if att.shift == 'C':
                    shiftdate = add_days(att.attendance_date,+1) 	
                else:
                    shiftdate = att.attendance_date 
                if att.on_duty_application:
                    if att.session_from_time and att.session_to_time and not att.session:
                        if att.session_from_time:
                            ot_stime = datetime.strptime(str(att.session_from_time), '%H:%M:%S').time()
                            ot_start_datetime = datetime.combine(shiftdate, ot_stime)
                            if in_time:
                                if in_time<ot_start_datetime:
                                    in_time=in_time
                                else:
                                    in_time=ot_start_datetime
                                    
                            else:
                                in_time=ot_start_datetime
                        if att.session_to_time:
                            ot_etime = datetime.strptime(str(att.session_to_time), '%H:%M:%S').time()
                            ot_end_datetime = datetime.combine(shiftdate, ot_etime)
                            if att.shift=='B' and ot_end_datetime<in_time:
                                shift_end_date=add_days(shiftdate,1)
                                ot_end_datetime=datetime.combine(shift_end_date, ot_etime)
                            if out_time:
                                if out_time<ot_end_datetime:
                                    out_time=ot_end_datetime
                            else:
                                out_time=ot_end_datetime
                    elif att.session and att.from_time and att.to_time:
                        if att.from_time:
                            if in_time:
                                if in_time>att.from_time:
                                    in_time=att.from_time
                            else:
                                in_time=att.from_time
                        if att.to_time:
                            if out_time:
                                if out_time<att.to_time:
                                    out_time=att.to_time
                            else:
                                out_time=att.to_time
                # frappe.errprint(in_time)
                # frappe.errprint(out_time)
                if in_time:
                    shift_start = frappe.get_value("Shift Type", {'name': att.shift}, ['start_time'])
                    shift_stime = datetime.strptime(str(shift_start), '%H:%M:%S').time()
                    shift_start_datetime = datetime.combine(shiftdate, shift_stime)
                    if in_time < shift_start_datetime:
                        in_time = shift_start_datetime
                    else:
                        in_time=in_time
                att_wh = time_diff_in_hours(out_time, in_time)
                tot_wh=0
                p_wh=0
                od_wh=0
                perm_time=0
                if att.att_permission is not None:
                    att_hours=shift_start = frappe.get_value("Permission", {'name': att.att_permission}, ['total_time'])
                    if att_hours is not None:   
                        perm_time=int(float(att_hours))
                        if perm_time > 0:
                            p_wh = round(att_wh, 2) + perm_time
                            p_hrs=convert_hours_to_hms(p_wh)
                        else:
                            p_wh = round(att_wh, 2) + perm_time
                            p_hrs=convert_hours_to_hms(p_wh)
                else:
                    p_wh = round(att_wh, 2)
                    p_hrs=convert_hours_to_hms(p_wh)
                wh=round(att_wh, 2)
                time_in_standard_format = "{:02d}:{:02d}:{:02d}".format(int(wh), int((wh * 60) % 60), int((wh * 3600) % 60))
                if p_wh < 24.0:
                    twh = time_in_standard_format
                    frappe.db.set_value('Attendance', att.name, 'total_working_hours', twh)
                    frappe.db.set_value('Attendance', att.name, 'working_hours', p_wh)
                else:
                    twh = "23:59:59"
                    p_hrs='23:59:59'
                    frappe.db.set_value('Attendance', att.name, 'total_working_hours', p_hrs)
                    frappe.db.set_value('Attendance', att.name, 'working_hours', p_wh)
                if p_wh < 4:
                    if att.shift=='C' and p_wh>=3.5:
                        frappe.db.set_value("Attendance", att.name, "status", "Half Day")
                    else:
                        frappe.db.set_value("Attendance", att.name, "status", "Absent")
                elif 4 <= p_wh < 8:
                    if att.shift == "C" and 7 <= p_wh <= 8:
                        frappe.db.set_value("Attendance", att.name, "status", "Present")
                    else:
                        frappe.db.set_value("Attendance", att.name, "status", "Half Day")
                    day_of_week = att.attendance_date.strftime("%A")
                    if day_of_week == "Saturday" and att.employee_type == "Staff":
                        frappe.db.set_value("Attendance", att.name, "status", "Present")
                else:
                    frappe.db.set_value("Attendance", att.name, "status", "Present")
                hh = check_holiday(att.attendance_date,att.employee)
                break_times = [(time(20, 30), time(21, 0)),  (time(12, 30), time(13, 0))]
                if not hh:
                    if att.actual_shift is not None and att.actual_shift == 'WW':
                        shift_start = frappe.get_value("Shift Type", {'name': att.shift}, ['start_time'])
                        shift_stime = datetime.strptime(str(shift_start), '%H:%M:%S').time()
                        shift_start_datetime = datetime.combine(shiftdate, shift_stime)
                        if in_time < shift_start_datetime:
                            in_time = shift_start_datetime
                        else:
                            in_time=in_time
                        out_time = out_time

                        if out_time > in_time:
                            extra_hours=time_diff_in_hours(out_time,in_time)
                            total_extra_hours = out_time - in_time
                            ot_hours = None
                            time_diff = out_time - in_time

                            if time_diff.seconds >= 3600:
                                if time_diff.seconds % 3600 <= 1800:
                                    ot_hours = time(time_diff.seconds // 3600, 0, 0)
                                else:
                                    ot_hours = time(time_diff.seconds // 3600, 30, 0)

                            if ot_hours is not None:
                                ot_hr = round((ot_hours.hour + ot_hours.minute / 60), 1)
                            else:
                                ot_hr = 0
                            deducted_hours = 0
                            break_date = None
                            if att.shift=='C':
                                break_date = add_days(att.attendance_date,+1)	
                            else:
                                break_date = att.attendance_date
                            break_date_str = datetime.strptime(str(break_date), '%Y-%m-%d').date()
                            for break_start, break_end in break_times:
                                break_start_dt = datetime.combine(break_date_str, break_start)
                                break_end_dt = datetime.combine(break_date_str, break_end)
                                if break_start_dt > in_time and break_end_dt < out_time:
                                    deducted_hours += 0.5
                            if ot_hr > 0:
                                ot_hr = ot_hr-deducted_hours
                            total_seconds = int(ot_hr * 3600)  
                            hours, remainder = divmod(total_seconds, 3600)
                            minutes, seconds = divmod(remainder, 60)
                            ot_hours = f"{hours:02}:{minutes:02}:{seconds:02}"
                        if wh>24:
                            frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', '23:00:00')
                            frappe.db.set_value('Attendance', att.name, 'overtime_hours', '23')
                            frappe.db.set_value('Attendance', att.name, 'extra_hours', wh)
                            frappe.db.set_value('Attendance', att.name, 'total_extra_hours', twh)
                        else:
                            frappe.db.set_value('Attendance', att.name, 'extra_hours', wh)
                            frappe.db.set_value('Attendance', att.name, 'total_extra_hours', twh)
                            frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', ot_hours)
                            frappe.db.set_value('Attendance', att.name, 'overtime_hours', ot_hr)
                    else:
                        day_of_week = att.attendance_date.strftime("%A")
                        shift_time = time(0, 0, 0)
                        if day_of_week == "Saturday" and att.employee_type == "Staff":
                            shift_time = frappe.get_value("Shift Type", {'name': att.shift}, ["ot_time"])
                        else:
                            shift_time = frappe.get_value("Shift Type", {'name': att.shift}, ["end_time"])
                        shift_end_time = dt.datetime.strptime(str(shift_time), '%H:%M:%S').time()
                        shift_date = None
                        if att.shift in ["C","B"] :
                            shift_date = add_days(att.attendance_date,+1)	
                        else:
                            shift_date = att.attendance_date
                        ot_date_str = datetime.strptime(str(shift_date), '%Y-%m-%d').date()
                        end_time = datetime.combine(ot_date_str, shift_end_time)
                        end_time = frappe.utils.get_datetime(end_time)
                        out_time = frappe.utils.get_datetime(out_time)
                        if out_time > end_time:
                            extra_hours=time_diff_in_hours(out_time,end_time)
                            total_extra_hours = out_time - end_time
                            ot_hours = None
                            time_diff = out_time - end_time
                            if time_diff.seconds >= 3600:
                                if time_diff.seconds % 3600 <= 1800:
                                    ot_hours = time(time_diff.seconds // 3600, 0, 0)
                                else:
                                    ot_hours = time(time_diff.seconds // 3600, 30, 0)
                            if ot_hours is not None:
                                ot_hr = round((ot_hours.hour + ot_hours.minute / 60), 1)
                            else:
                                ot_hr = 0
                            deducted_hours = 0
                            break_date = None
                            if att.shift=='C':
                                break_date = add_days(att.attendance_date,+1)	
                            else:
                                break_date = att.attendance_date
                            break_date_str = datetime.strptime(str(break_date), '%Y-%m-%d').date()
                            for break_start, break_end in break_times:
                                break_start_dt = datetime.combine(break_date_str, break_start)
                                break_end_dt = datetime.combine(break_date_str, break_end)
                                if break_start_dt > end_time and break_end_dt < out_time:
                                    deducted_hours += 0.5
                            if ot_hr > 0:
                                ot_hr = ot_hr-deducted_hours
                            total_seconds = int(ot_hr * 3600)  
                            hours, remainder = divmod(total_seconds, 3600)
                            minutes, seconds = divmod(remainder, 60)
                            ot_hours = f"{hours:02}:{minutes:02}:{seconds:02}"
                        else:
                            extra_hours = 0.0
                            total_extra_hours = "00:00:00"
                            ot_hours = "00:00:00"
                            ot_hr = 0.0		
                        if wh>24:
                            if day_of_week == "Saturday" and att.employee_type == "Staff":
                                frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', '19:00:00')
                                frappe.db.set_value('Attendance', att.name, 'overtime_hours', '19')
                                frappe.db.set_value('Attendance', att.name, 'extra_hours', round(extra_hours, 2))
                                frappe.db.set_value('Attendance', att.name, 'total_extra_hours', total_extra_hours)
                            else:
                                frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', '15:00:00')
                                frappe.db.set_value('Attendance', att.name, 'overtime_hours', '15')
                                frappe.db.set_value('Attendance', att.name, 'extra_hours', round(extra_hours, 2))
                                frappe.db.set_value('Attendance', att.name, 'total_extra_hours', total_extra_hours)
                        else:	
                            frappe.db.set_value('Attendance', att.name, 'extra_hours', round(extra_hours, 2))
                            frappe.db.set_value('Attendance', att.name, 'total_extra_hours', total_extra_hours)
                            frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', ot_hours)
                            frappe.db.set_value('Attendance', att.name, 'overtime_hours', ot_hr)
                else:
                    if in_time and out_time:
                        shift_start = frappe.get_value("Shift Type", {'name': att.shift}, ['start_time'])
                        shift_stime = datetime.strptime(str(shift_start), '%H:%M:%S').time()
                        shift_start_datetime = datetime.combine(shiftdate, shift_stime)
                        if in_time < shift_start_datetime:
                            in_time = shift_start_datetime
                        else:
                            in_time=in_time
                        out_time = out_time

                        if out_time > in_time:
                            extra_hours=time_diff_in_hours(out_time,in_time)
                            total_extra_hours = out_time - in_time
                            ot_hours = None
                            time_diff = out_time - in_time

                            if time_diff.seconds >= 3600:
                                if time_diff.seconds % 3600 <= 1800:
                                    ot_hours = time(time_diff.seconds // 3600, 0, 0)
                                else:
                                    ot_hours = time(time_diff.seconds // 3600, 30, 0)

                            if ot_hours is not None:
                                ot_hr = round((ot_hours.hour + ot_hours.minute / 60), 1)
                            else:
                                ot_hr = 0
                            break_times = [
                            (time(20, 30), time(21, 0)),  
                            (time(12, 30), time(13, 0))  
                            ]
                            deducted_hours = 0
                            break_date = None
                            if att.shift=='C':
                                break_date = add_days(att.attendance_date,+1)	
                            else:
                                break_date = att.attendance_date
                            break_date_str = datetime.strptime(str(break_date), '%Y-%m-%d').date()
                            for break_start, break_end in break_times:
                                break_start_dt = datetime.combine(break_date_str, break_start)
                                break_end_dt = datetime.combine(break_date_str, break_end)
                                if break_start_dt > in_time and break_end_dt < out_time:
                                    deducted_hours += 0.5
                            if ot_hr > 0:
                                ot_hr = ot_hr-deducted_hours
                            total_seconds = int(ot_hr * 3600)  
                            hours, remainder = divmod(total_seconds, 3600)
                            minutes, seconds = divmod(remainder, 60)
                            ot_hours = f"{hours:02}:{minutes:02}:{seconds:02}"
                        fh_holiday=check_nhfh(att.attendance_date,att.employee)
                        if att.employee_type=='Contract Employee' and fh_holiday=='FH':
                            ot_hr=ot_hr*2
                            total_seconds = int(ot_hr * 3600)  
                            hours, remainder = divmod(total_seconds, 3600)
                            minutes, seconds = divmod(remainder, 60)
                            ot_hours = f"{hours:02}:{minutes:02}:{seconds:02}"
                            if ot_hr>=24:
                                ot_hr=23
                                ot_hours='23:00:00'
                        if wh>24:
                            frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', '23:00:00')
                            frappe.db.set_value('Attendance', att.name, 'overtime_hours', '23')
                            frappe.db.set_value('Attendance', att.name, 'extra_hours', wh)
                            frappe.db.set_value('Attendance', att.name, 'total_extra_hours', twh)
                        else:
                            frappe.db.set_value('Attendance', att.name, 'extra_hours', wh)
                            frappe.db.set_value('Attendance', att.name, 'total_extra_hours', twh)
                            frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', ot_hours)
                            frappe.db.set_value('Attendance', att.name, 'overtime_hours', ot_hr)
                    else:
                        frappe.db.set_value('Attendance', att.name, 'total_working_hours', "00:00:00")
                        frappe.db.set_value('Attendance', att.name, 'working_hours', "0.0")
                        frappe.db.set_value('Attendance', att.name, 'extra_hours', "0.0")
                        frappe.db.set_value('Attendance', att.name, 'total_extra_hours', "00:00:00")
                        frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', "00:00:00")
                        frappe.db.set_value('Attendance', att.name, 'overtime_hours', "0.0")
                        frappe.db.set_value('Attendance', att.name, 'late_entry_time', "00:00:00")
                        frappe.db.set_value('Attendance', att.name, 'early_out_time',"00:00:00")
                if in_time > out_time:
                    frappe.db.set_value('Attendance', att.name, 'total_working_hours', 0)
                    frappe.db.set_value('Attendance', att.name, 'working_hours', 0)
                    frappe.db.set_value('Attendance', att.name, 'status', 'Absent')
                    frappe.db.set_value('Attendance', att.name, 'extra_hours',0)
                    frappe.db.set_value('Attendance', att.name, 'total_extra_hours', 0)
                    frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', 0)
                    frappe.db.set_value('Attendance', att.name, 'overtime_hours', 0)
            else:
                frappe.db.set_value('Attendance', att.name, 'total_working_hours', "00:00:00")
                frappe.db.set_value('Attendance', att.name, 'working_hours', "0.0")
                frappe.db.set_value('Attendance', att.name, 'extra_hours', "0.0")
                frappe.db.set_value('Attendance', att.name, 'total_extra_hours', "00:00:00")
                frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', "00:00:00")
                frappe.db.set_value('Attendance', att.name, 'overtime_hours', "0.0")
                frappe.db.set_value('Attendance', att.name, 'late_entry_time', "00:00:00")
                frappe.db.set_value('Attendance', att.name, 'early_out_time',"00:00:00")
        
 
 
@frappe.whitelist()
def submit_att(from_date,to_date,employee_type,department):
    if department == "All Departments":
        att = frappe.db.sql("""select * from tabAttendance where attendance_date between '%s' and '%s' and docstatus = 0 and employee_type = '%s' """%(from_date,to_date,employee_type),as_dict=True)
    elif department != "All Departments":
        att = frappe.db.sql("""select * from tabAttendance where attendance_date between '%s' and '%s' and docstatus = 0 and employee_type = '%s' and department = '%s' """%(from_date,to_date,employee_type,department),as_dict=True)
    for a in att:
        od = frappe.get_doc("Attendance",{'name':a.name})
        od.submit()
        frappe.db.commit()
    return "ok"

@frappe.whitelist()
def submit_att_with_employee(from_date,to_date,employee):
    att = frappe.db.sql("""select * from tabAttendance where attendance_date between '%s' and '%s' and docstatus = 0 and employee = '%s' """%(from_date,to_date,employee),as_dict=True)
    for a in att:
        od = frappe.get_doc("Attendance",{'name':a.name})
        od.save(ignore_permissions=True)
        od.submit()
        frappe.db.commit()
    return "ok"

@frappe.whitelist()
def update_workspot(from_date,to_date):
    attendance = frappe.db.sql("""select * from tabAttendance where attendance_date between '%s' and '%s' """%(from_date,to_date),as_dict=True)
    for att in attendance:
        if att.employee_type=="Worker" or att.employee_type=='Trainee':
            workspot=frappe.db.get_value("Employee",{"employee_number":att.employee},['workspot']) or ''
            if workspot:
                frappe.db.set_value("Attendance",att.name,'workspot',workspot)
        elif att=='Contract Employee':
            workspot=frappe.db.get_value("Workspot for CL",{"employee":att.employee,"date":att.attendance_date},['workspot']) or ''
            if workspot:
                frappe.db.set_value("Attendance",att.name,'workspot',workspot)

@frappe.whitelist()
def update_workspot_with_employee(from_date,to_date,employee):
    attendance = frappe.db.sql("""select * from tabAttendance where attendance_date between '%s' and '%s' and employee='%s' """%(from_date,to_date,employee),as_dict=True)
    for att in attendance:
        if att.employee_type=="Worker" or att.employee_type=='Trainee':
            workspot=frappe.db.get_value("Employee",{"employee_number":att.employee},['workspot']) or ''
            if workspot:
                frappe.db.set_value("Attendance",att.name,'workspot',workspot)
        elif att=='Contract Employee':
            workspot=frappe.db.get_value("Workspot for CL",{"employee":att.employee,"date":att.attendance_date},['workspot']) or ''
            if workspot:
                frappe.db.set_value("Attendance",att.name,'workspot',workspot)


@frappe.whitelist()
def update_workspot_with_employee_type(from_date,to_date,employee_type):
    attendance = frappe.db.sql("""select * from tabAttendance where attendance_date between '%s' and '%s' and employee_type='%s' """%(from_date,to_date,employee_type),as_dict=True)
    for att in attendance:
        if att.employee_type=="Worker" or att.employee_type=='Trainee':
            workspot=frappe.db.get_value("Employee",{"employee_number":att.employee},['workspot']) or ''
            if workspot:
                frappe.db.set_value("Attendance",att.name,'workspot',workspot)
        elif att=='Contract Employee':
            workspot=frappe.db.get_value("Workspot for CL",{"employee":att.employee,"date":att.attendance_date},['workspot']) or ''
            if workspot:
                frappe.db.set_value("Attendance",att.name,'workspot',workspot)

@frappe.whitelist()
def update_workspot_with_con_name(from_date,to_date,employee_type,con_name):
    attendance = frappe.db.sql("""select * from tabAttendance where attendance_date between '%s' and '%s' and employee_type='%s' and 'contractor' = '%s' """%(from_date,to_date,employee_type,con_name),as_dict=True)
    for att in attendance:
        if att.employee_type=="Worker" or att.employee_type=='Trainee':
            workspot=frappe.db.get_value("Employee",{"employee_number":att.employee},['workspot']) or ''
            if workspot:
                frappe.db.set_value("Attendance",att.name,'workspot',workspot)
        elif att=='Contract Employee':
            workspot=frappe.db.get_value("Workspot for CL",{"employee":att.employee,"date":att.attendance_date},['workspot']) or ''
            if workspot:
                frappe.db.set_value("Attendance",att.name,'workspot',workspot)


@frappe.whitelist()
def mark_att_present(from_date, to_date):
    attendance = frappe.db.get_all('Attendance', {'attendance_date': ('between', (from_date, to_date)),'docstatus': 0}, ['*'])
    for att in attendance:
        if att.status == 'Present':
            frappe.db.set_value('Attendance', att.name, 'docstatus', 1)

@frappe.whitelist()
def mark_att_present_with_employee(from_date, to_date, employee):
    attendance = frappe.db.get_all('Attendance', {'employee':employee,'attendance_date': ('between', (from_date, to_date)),'docstatus': 0}, ['*'])
    for att in attendance:
        if att.status == 'Present':
            frappe.db.set_value('Attendance', att.name, 'docstatus', 1)

@frappe.whitelist()
def mark_att_present_with_employee_type(from_date, to_date, employee_type):
    attendance = frappe.db.get_all('Attendance', {'employee_type':employee_type,'attendance_date': ('between', (from_date, to_date)),'docstatus': 0}, ['*'])
    for att in attendance:
        if att.status == 'Present':
            frappe.db.set_value('Attendance', att.name, 'docstatus', 1)
@frappe.whitelist()
def mark_att_present_with_con_name(from_date, to_date, employee_type,con_name):
    attendance = frappe.db.get_all('Attendance', {'employee_type':employee_type,'contractor':con_name,'attendance_date': ('between', (from_date, to_date)),'docstatus': 0}, ['*'])
    for att in attendance:
        if att.status == 'Present':
            frappe.db.set_value('Attendance', att.name, 'docstatus', 1)

@frappe.whitelist()
def mark_late_early(from_date, to_date):
    attendance = frappe.db.get_all('Attendance', {'attendance_date': ('between', (from_date, to_date))}, ['*'])
    for att in attendance:
        late_entry_value=0
        late_entry_diff=None
        if att.in_time:
            if att.shift in ['A','B']:
                # print("A,B")
                shift_time = frappe.get_value("Shift Type", {'name': att.shift}, ["start_time"])
                shift_start_time = datetime.strptime(str(shift_time), '%H:%M:%S').time()
                start_time = dt.datetime.combine(att.attendance_date,shift_start_time)
                
                if att.in_time > datetime.combine(att.attendance_date, shift_start_time):
                    late_entry_value=1
                    late_entry_diff= att.in_time -start_time
                else:
                    late_entry_value=0
                    late_entry_diff=None
            if att.shift in ['C']:
                # print("C")
                shift_time = frappe.get_value("Shift Type", {'name': att.shift}, ["start_time"])
                shift_start_time = datetime.strptime(str(shift_time), '%H:%M:%S').time()
                start_time = datetime.combine(add_days(att.attendance_date, 1), shift_start_time)
                if att.in_time > datetime.combine(add_days(att.attendance_date,1), shift_start_time):
                    late_entry_value=1
                    late_entry_diff= att.in_time - start_time
                else:
                    late_entry_value=0
                    late_entry_diff=None
            frappe.db.set_value('Attendance', att.name, 'late_entry', late_entry_value)
            frappe.db.set_value('Attendance', att.name, 'late_entry_time', late_entry_diff)
        if att.shift and att.out_time and att.in_time: 
            early_out_value=0
            early_out_diff=None
            if att.shift in ['A','B']:
                shift_time = frappe.get_value("Shift Type", {'name': att.shift}, ["end_time"])
                shift_end_time = datetime.strptime(str(shift_time), '%H:%M:%S').time()
                end_time = dt.datetime.combine(att.attendance_date,shift_end_time)
                if att.out_time < datetime.combine(att.attendance_date, shift_end_time) and att.out_time>att.in_time:
                    early_out_value=1
                    early_out_diff= end_time - att.out_time
                else:
                    early_out_value=0
                    early_out_diff=None
                
            if att.shift == "C":
                shift_time = frappe.get_value("Shift Type", {'name': att.shift}, ["end_time"])
                shift_end_time = datetime.strptime(str(shift_time), '%H:%M:%S').time()
                end_time = dt.datetime.combine(add_days(att.attendance_date,1),shift_end_time)
                if att.out_time < datetime.combine(add_days(att.attendance_date,1), shift_end_time) and att.out_time>att.in_time:
                    early_out_value=1
                    early_out_diff= end_time - att.out_time
                else:
                    early_out_value=0
                    early_out_diff= None
            frappe.db.set_value('Attendance', att.name, 'early_exit', early_out_value)
            # print(att.name)
            # print(early_out_diff)
            frappe.db.set_value('Attendance', att.name, 'early_out_time',early_out_diff)
            # print("HI")

@frappe.whitelist()
def mark_late_early_with_employee(from_date, to_date, employee):
    attendance = frappe.db.get_all('Attendance', {'employee':employee,'attendance_date': ('between', (from_date, to_date))}, ['*'])
    for att in attendance:
        late_entry_value=0
        late_entry_diff=None
        if att.in_time:
            if att.shift in ['A','B']:
                # print("A,B")
                shift_time = frappe.get_value("Shift Type", {'name': att.shift}, ["start_time"])
                shift_start_time = datetime.strptime(str(shift_time), '%H:%M:%S').time()
                start_time = dt.datetime.combine(att.attendance_date,shift_start_time)
                
                if att.in_time > datetime.combine(att.attendance_date, shift_start_time):
                    late_entry_value=1
                    late_entry_diff= att.in_time -start_time
                else:
                    late_entry_value=0
                    late_entry_diff=None
            if att.shift in ['C']:
                # print("C")
                shift_time = frappe.get_value("Shift Type", {'name': att.shift}, ["start_time"])
                shift_start_time = datetime.strptime(str(shift_time), '%H:%M:%S').time()
                start_time = datetime.combine(add_days(att.attendance_date, 1), shift_start_time)
                if att.in_time > datetime.combine(add_days(att.attendance_date,1), shift_start_time):
                    late_entry_value=1
                    late_entry_diff= att.in_time - start_time
                else:
                    late_entry_value=0
                    late_entry_diff=None
            frappe.db.set_value('Attendance', att.name, 'late_entry', late_entry_value)
            frappe.db.set_value('Attendance', att.name, 'late_entry_time', late_entry_diff)
        if att.shift and att.out_time and att.in_time: 
            early_out_value=0
            early_out_diff=None
            if att.shift in ['A','B']:
                shift_time = frappe.get_value("Shift Type", {'name': att.shift}, ["end_time"])
                shift_end_time = datetime.strptime(str(shift_time), '%H:%M:%S').time()
                end_time = dt.datetime.combine(att.attendance_date,shift_end_time)
                if att.out_time < datetime.combine(att.attendance_date, shift_end_time) and att.out_time>att.in_time:
                    early_out_value=1
                    early_out_diff= end_time - att.out_time
                else:
                    early_out_value=0
                    early_out_diff=None
                
            if att.shift == "C":
                shift_time = frappe.get_value("Shift Type", {'name': att.shift}, ["end_time"])
                shift_end_time = datetime.strptime(str(shift_time), '%H:%M:%S').time()
                end_time = dt.datetime.combine(add_days(att.attendance_date,1),shift_end_time)
                if att.out_time < datetime.combine(add_days(att.attendance_date,1), shift_end_time) and att.out_time>att.in_time:
                    early_out_value=1
                    early_out_diff= end_time - att.out_time
                else:
                    early_out_value=0
                    early_out_diff= None
            frappe.db.set_value('Attendance', att.name, 'early_exit', early_out_value)
            frappe.db.set_value('Attendance', att.name, 'early_out_time',early_out_diff)




@frappe.whitelist()
def mark_late_early_with_employee_type(from_date,to_date,employee_type):
    attendance = frappe.db.get_all('Attendance', {'employee_type':employee_type,'attendance_date': ('between', (from_date, to_date))}, ['*'])
    for att in attendance:
        late_entry_value=0
        late_entry_diff=None
        if att.in_time:
            if att.shift in ['A','B']:
                # print("A,B")
                shift_time = frappe.get_value("Shift Type", {'name': att.shift}, ["start_time"])
                shift_start_time = datetime.strptime(str(shift_time), '%H:%M:%S').time()
                start_time = dt.datetime.combine(att.attendance_date,shift_start_time)
                
                if att.in_time > datetime.combine(att.attendance_date, shift_start_time):
                    late_entry_value=1
                    late_entry_diff= att.in_time -start_time
                else:
                    late_entry_value=0
                    late_entry_diff=None
            if att.shift in ['C']:
                # print("C")
                shift_time = frappe.get_value("Shift Type", {'name': att.shift}, ["start_time"])
                shift_start_time = datetime.strptime(str(shift_time), '%H:%M:%S').time()
                start_time = datetime.combine(add_days(att.attendance_date, 1), shift_start_time)
                if att.in_time > datetime.combine(add_days(att.attendance_date,1), shift_start_time):
                    late_entry_value=1
                    late_entry_diff= att.in_time - start_time
                else:
                    late_entry_value=0
                    late_entry_diff=None
            frappe.db.set_value('Attendance', att.name, 'late_entry', late_entry_value)
            frappe.db.set_value('Attendance', att.name, 'late_entry_time', late_entry_diff)
        if att.shift and att.out_time: 
            early_out_value=0
            early_out_diff=None
            if att.shift in ['A','B']:
                shift_time = frappe.get_value("Shift Type", {'name': att.shift}, ["end_time"])
                shift_end_time = datetime.strptime(str(shift_time), '%H:%M:%S').time()
                end_time = dt.datetime.combine(att.attendance_date,shift_end_time)
                if att.out_time < datetime.combine(att.attendance_date, shift_end_time):
                    early_out_value=1
                    early_out_diff= end_time - att.out_time
                else:
                    early_out_value=0
                    early_out_diff=None
                
            if att.shift == "C":
                shift_time = frappe.get_value("Shift Type", {'name': att.shift}, ["end_time"])
                shift_end_time = datetime.strptime(str(shift_time), '%H:%M:%S').time()
                end_time = dt.datetime.combine(add_days(att.attendance_date,1),shift_end_time)
                if att.out_time < datetime.combine(add_days(att.attendance_date,1), shift_end_time):
                    early_out_value=1
                    early_out_diff= end_time - att.out_time
                else:
                    early_out_value=0
                    early_out_diff= None
            frappe.db.set_value('Attendance', att.name, 'early_exit', early_out_value)
            frappe.db.set_value('Attendance', att.name, 'early_out_time',early_out_diff)


@frappe.whitelist()
def mark_late_early_with_con_name(from_date,to_date,employee_type,con_name):
    attendance = frappe.db.get_all('Attendance', {'employee_type':employee_type,'contractor':con_name,'attendance_date': ('between', (from_date, to_date))}, ['*'])
    for att in attendance:
        late_entry_value=0
        late_entry_diff=None
        if att.in_time:
            if att.shift in ['A','B']:
                # print("A,B")
                shift_time = frappe.get_value("Shift Type", {'name': att.shift}, ["start_time"])
                shift_start_time = datetime.strptime(str(shift_time), '%H:%M:%S').time()
                start_time = dt.datetime.combine(att.attendance_date,shift_start_time)
                
                if att.in_time > datetime.combine(att.attendance_date, shift_start_time):
                    late_entry_value=1
                    late_entry_diff= att.in_time -start_time
                else:
                    late_entry_value=0
                    late_entry_diff=None
            if att.shift in ['C']:
                # print("C")
                shift_time = frappe.get_value("Shift Type", {'name': att.shift}, ["start_time"])
                shift_start_time = datetime.strptime(str(shift_time), '%H:%M:%S').time()
                start_time = datetime.combine(add_days(att.attendance_date, 1), shift_start_time)
                if att.in_time > datetime.combine(add_days(att.attendance_date,1), shift_start_time):
                    late_entry_value=1
                    late_entry_diff= att.in_time - start_time
                else:
                    late_entry_value=0
                    late_entry_diff=None
            frappe.db.set_value('Attendance', att.name, 'late_entry', late_entry_value)
            frappe.db.set_value('Attendance', att.name, 'late_entry_time', late_entry_diff)
        if att.shift and att.out_time: 
            early_out_value=0
            early_out_diff=None
            if att.shift in ['A','B']:
                shift_time = frappe.get_value("Shift Type", {'name': att.shift}, ["end_time"])
                shift_end_time = datetime.strptime(str(shift_time), '%H:%M:%S').time()
                end_time = dt.datetime.combine(att.attendance_date,shift_end_time)
                if att.out_time < datetime.combine(att.attendance_date, shift_end_time):
                    early_out_value=1
                    early_out_diff= end_time - att.out_time
                else:
                    early_out_value=0
                    early_out_diff=None
                
            if att.shift == "C":
                shift_time = frappe.get_value("Shift Type", {'name': att.shift}, ["end_time"])
                shift_end_time = datetime.strptime(str(shift_time), '%H:%M:%S').time()
                end_time = dt.datetime.combine(add_days(att.attendance_date,1),shift_end_time)
                if att.out_time < datetime.combine(add_days(att.attendance_date,1), shift_end_time):
                    early_out_value=1
                    early_out_diff= end_time - att.out_time
                else:
                    early_out_value=0
                    early_out_diff= None
            frappe.db.set_value('Attendance', att.name, 'early_exit', early_out_value)
            frappe.db.set_value('Attendance', att.name, 'early_out_time',early_out_diff)



@frappe.whitelist()
def get_assigned_shift(from_date, to_date):
    attendance = frappe.db.get_all('Attendance', {'attendance_date': ('between', (from_date, to_date)),'docstatus': ('!=',2)}, ['*'])
    for att in attendance:
        attendance_date=att.attendance_date
        att_employee=att.employee
        get_att = frappe.db.exists("Shift Assignment", {'employee': att_employee, 'start_date': attendance_date, 'end_date': attendance_date, 'docstatus': 1})
        if get_att:
            assign_name=frappe.db.get_value("Shift Assignment", {'employee': att_employee, 'start_date': attendance_date, 'end_date': attendance_date, 'docstatus': 1},['name'])
            sa = frappe.get_doc("Shift Assignment",assign_name)
            act_shift=sa.shift_type
            if act_shift:
                frappe.db.set_value("Attendance",att.name,'actual_shift',act_shift)
                if act_shift == "WW":
                    att_doc = frappe.get_doc("Attendance", att.name)
                    if att_doc.docstatus == 0:
                        if att_doc.status =="Absent":
                            att_doc.status = 'Present'
                            att_doc.save()
                        att_doc.submit()

@frappe.whitelist()
def get_assigned_shift_with_employee(from_date, to_date, employee):
    attendance = frappe.db.get_all('Attendance', {'employee':employee,'attendance_date': ('between', (from_date, to_date)),'docstatus': ('!=',2)}, ['*'])
    for att in attendance:
        attendance_date=att.attendance_date
        att_employee=att.employee
        get_att = frappe.db.exists("Shift Assignment", {'employee': att_employee, 'start_date': attendance_date, 'end_date': attendance_date, 'docstatus': 1})
        if get_att:
            assign_name=frappe.db.get_value("Shift Assignment", {'employee': att_employee, 'start_date': attendance_date, 'end_date': attendance_date, 'docstatus': 1},['name'])
            sa = frappe.get_doc("Shift Assignment",assign_name)
            act_shift=sa.shift_type
            if act_shift:
                frappe.db.set_value("Attendance",att.name,'actual_shift',act_shift)
                if act_shift == "WW":
                    att_doc = frappe.get_doc("Attendance", att.name)
                    if att_doc.status =="Absent":
                        att_doc.status = 'Present'
                        att_doc.save()
                    if att_doc.docstatus == 0:
                        
                        att_doc.submit()
                    





@frappe.whitelist()
def get_assigned_shift_with_employee_type(from_date, to_date, employee_type):
    attendance = frappe.db.get_all('Attendance', {'employee_type':employee_type,'attendance_date': ('between', (from_date, to_date)),'docstatus': ('!=',2)}, ['*'])
    for att in attendance:
        attendance_date=att.attendance_date
        att_employee=att.employee
        get_att = frappe.db.exists("Shift Assignment", {'employee': att_employee, 'start_date': attendance_date, 'end_date': attendance_date, 'docstatus': 1})
        if get_att:
            assign_name=frappe.db.get_value("Shift Assignment", {'employee': att_employee, 'start_date': attendance_date, 'end_date': attendance_date, 'docstatus': 1},['name'])
            sa = frappe.get_doc("Shift Assignment",assign_name)
            act_shift=sa.shift_type
            if act_shift:
                frappe.db.set_value("Attendance",att.name,'actual_shift',act_shift)
                if act_shift == "WW":
                    att_doc = frappe.get_doc("Attendance", att.name)
                    if att_doc.docstatus == 0:
                        if att_doc.status =="Absent":
                            att_doc.status = 'Present'
                            att_doc.save()
                        att_doc.submit()

@frappe.whitelist()
def get_assigned_shift_with_con_name(from_date, to_date, employee_type,con_name):
    attendance = frappe.db.get_all('Attendance', {'employee_type':employee_type,'contractor':con_name,'attendance_date': ('between', (from_date, to_date)),'docstatus': ('!=',2)}, ['*'])
    for att in attendance:
        attendance_date=att.attendance_date
        att_employee=att.employee
        get_att = frappe.db.exists("Shift Assignment", {'employee': att_employee, 'start_date': attendance_date, 'end_date': attendance_date, 'docstatus': 1})
        if get_att:
            assign_name=frappe.db.get_value("Shift Assignment", {'employee': att_employee, 'start_date': attendance_date, 'end_date': attendance_date, 'docstatus': 1},['name'])
            sa = frappe.get_doc("Shift Assignment",assign_name)
            act_shift=sa.shift_type
            if act_shift:
                frappe.db.set_value("Attendance",att.name,'actual_shift',act_shift)
                if act_shift == "WW":
                    att_doc = frappe.get_doc("Attendance", att.name)
                    if att_doc.docstatus == 0:
                        if att_doc.status =="Absent":
                            att_doc.status = 'Present'
                            att_doc.save()
                        att_doc.submit()



@frappe.whitelist()			
# convert the hours in integer format into time format		
def convert_hours_to_hms(hours):
    total_seconds = hours * 3600  
    hours = int(total_seconds // 3600) 
    total_seconds %= 3600  
    minutes = int(total_seconds // 60)  
    seconds = int(total_seconds % 60) 
    return f"{hours:02}:{minutes:02}:{seconds:02}"

@frappe.whitelist()
# method create OT request automatically when an employee worked on NH/FH
def create_ot_req(from_date,to_date):
    dates = get_dates(from_date,to_date)
    for date in dates:
        att=frappe.db.get_all("Attendance",{'attendance_date':date,'docstatus':1},['overtime_hours','name','in_time','out_time','shift','employee','total_working_hours'])
        if att:
            for a in att:
                hh=check_nhfh(date,a.employee)
                if hh and hh in ['NH','FH']:
                    if a.overtime_hours>0:
                        s_end=frappe.db.get_value("Shift Type",{'name':a.shift},['start_time'])
                        if not frappe.db.exists("Overtime Request",{'employee':a.employee,'ot_date':date,'docstatus':['!=',2]}):
                            ot=frappe.new_doc("Overtime Request")
                            ot.employee=a.employee
                            ot.shift=a.shift
                            ot.ot_reasons='Compensatory Off'
                            ot.ot_date=date
                            if a.in_time:
                                ot.from_time=a.in_time.time()
                            if a.out_time:
                                ot.to_time=a.out_time.time()
                            ot.total_hours=a.overtime_hours
                            ot.ot_reasons='Compensatory Off'
                            # frappe.errprint(a.total_working_hours)
                            ot.total_hour=a.total_working_hours
                            if a.overtime_hours>=8:
                                ot.is_considered_as='Overtime'
                            ot.insert()
                            ot.save(ignore_permissions=True)
                            frappe.db.commit()

@frappe.whitelist()
# method create OT request automatically when an employee worked on NH/FH
def create_ot_req_emp(from_date,to_date,employee):
    dates = get_dates(from_date,to_date)
    for date in dates:
        att=frappe.db.get_all("Attendance",{'attendance_date':date,'docstatus':1,'employee':employee},['overtime_hours','name','in_time','out_time','shift','employee','total_working_hours'])
        if att:
            for a in att:
                hh=check_nhfh(date,a.employee)
                if hh and hh in ['NH','FH']:
                    if a.overtime_hours>0:
                        s_end=frappe.db.get_value("Shift Type",{'name':a.shift},['start_time'])
                        if not frappe.db.exists("Overtime Request",{'employee':a.employee,'ot_date':date,'docstatus':['!=',2]}):
                            ot=frappe.new_doc("Overtime Request")
                            ot.employee=a.employee
                            ot.ot_date=date
                            # frappe.errprint(a.shift)
                            ot.shift=a.shift
                            ot.ot_reasons='Compensatory Off'
                            # frappe.errprint(ot.shift)
                            if a.in_time:
                                # frappe.errprint(a.in_time.time())
                                ot.from_time=a.in_time.time()
                            if a.out_time:
                                # frappe.errprint(a.out_time.time())
                                ot.to_time=a.out_time.time()
                            ot.total_hours=a.overtime_hours
                            # frappe.errprint(a.total_working_hours)
                            ot.total_hour=a.total_working_hours
                            if a.overtime_hours>=8:
                                ot.is_considered_as='Overtime'
                            ot.insert()
                            ot.save(ignore_permissions=True)
                            frappe.db.commit()
                            # frappe.db.set_value('Overtime Request',ot.name,'total_hour',a.total_working_hours)



@frappe.whitelist()
# method create OT request automatically when an employee worked on NH/FH
def create_ot_req_employee_type(from_date,to_date,employee_type):
    dates = get_dates(from_date,to_date)
    for date in dates:
        att=frappe.db.get_all("Attendance",{'attendance_date':date,'docstatus':1,'employee_type':employee_type},['overtime_hours','name','in_time','out_time','shift','employee','total_working_hours'])
        if att:
            for a in att:
                hh=check_nhfh(date,a.employee)
                if hh and hh in ['NH','FH']:
                    if a.overtime_hours>0:
                        s_end=frappe.db.get_value("Shift Type",{'name':a.shift},['start_time'])
                        if not frappe.db.exists("Overtime Request",{'employee':a.employee,'ot_date':date,'docstatus':['!=',2]}):
                            ot=frappe.new_doc("Overtime Request")
                            ot.employee=a.employee
                            ot.ot_date=date
                            ot.ot_reasons='Compensatory Off'
                            # frappe.errprint(a.shift)
                            ot.shift=a.shift
                            # frappe.errprint(ot.shift)
                            if a.in_time:
                                # frappe.errprint(a.in_time.time())
                                ot.from_time=a.in_time.time()
                            if a.out_time:
                                # frappe.errprint(a.out_time.time())
                                ot.to_time=a.out_time.time()
                            ot.total_hours=a.overtime_hours
                            # frappe.errprint(a.total_working_hours)
                            ot.total_hour=a.total_working_hours
                            if a.overtime_hours>=8:
                                ot.is_considered_as='Overtime'
                            ot.insert()
                            ot.save(ignore_permissions=True)
                            frappe.db.commit()
                            # frappe.db.set_value('Overtime Request',ot.name,'total_hour',a.total_working_hours)


@frappe.whitelist()
def check_nhfh(date,emp):
    holiday_list = frappe.db.get_value('Employee',{'name':emp},'holiday_list')
    holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off,`tabHoliday`.national_holiday,`tabHoliday`.festival_holiday from `tabHoliday List`
    left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(holiday_list,date),as_dict=True)
    doj= frappe.db.get_value("Employee",{'name':emp},"date_of_joining")
    status = ''
    if holiday :
        if doj < holiday[0].holiday_date:
            if holiday[0].national_holiday == 1:
                return "NH"     
            elif holiday[0].festival_holiday == 1:
                return "FH"   
            else:
                return ''

@frappe.whitelist()
def get_attendance_values(employee, ot_date):
    attendance_doc = frappe.get_all('Attendance', 
        filters={'employee': employee, 'attendance_date': ot_date},
        fields=['shift', 'out_time', 'total_working_hours', 'overtime_hours']
    )
        

    if attendance_doc:
        if attendance_doc and attendance_doc[0]['out_time']:
            out_time = attendance_doc[0]['out_time']
            
            if isinstance(out_time, str):
                out_time = datetime.strptime(out_time, '%Y-%m-%d %H:%M:%S') 
                
            out_time_str = out_time.strftime('%H:%M:%S')
            return {
                'shift': attendance_doc[0]['shift'],
                'out_time': out_time_str,
                'total_working_hours': attendance_doc[0]['total_working_hours'],
                'total_overtime_hours': attendance_doc[0]['overtime_hours']
            }

@frappe.whitelist()
def mark_attendance_from_checkin_test(employee,time,log_type):
    if log_type == 'IN':
        att_time = time.time()
        # shift = ''
        print(employee)
        att_date = time.date()
        max_in = datetime.strptime('05:30','%H:%M').time()
        before_in = frappe.db.sql("""select * from `tabEmployee Checkin` where employee = '%s' and log_type = 'IN' and date(time) = '%s' and TIME(time) < '%s' order by time ASC """%(employee,att_date,max_in),as_dict=True)
        after_in = frappe.db.sql("""select * from `tabEmployee Checkin` where employee = '%s' and log_type = 'IN' and date(time) = '%s' and TIME(time) > '%s' order by time ASC """%(employee,att_date,max_in),as_dict=True)
        if before_in and not after_in:
            att_date = add_days(att_date,-1)
            att = frappe.db.exists('Attendance',{"employee":employee,'attendance_date':att_date,'docstatus':['!=','2']})   
            if not att:
                att = frappe.new_doc("Attendance")
                att.employee = employee
                att.attendance_date = att_date
                if not att.shift:
                    att.shift = get_actual_shift_start(get_time(before_in[0].time))
                att.status = 'Absent'
                att.in_time = before_in[0].time
                att.total_working_hours = "00:00:00"
                att.working_hours = "0.0"
                att.extra_hours = "0.0"
                att.total_extra_hours = "00:00:00"
                att.total_overtime_hours = "00:00:00"
                att.overtime_hours = "0.0"
                att.late_entry_time = "00:00:00"
                att.early_out_time = "00:00:00"
                att.save(ignore_permissions=True)
                frappe.db.commit()
                for c in before_in:
                    frappe.db.set_value('Employee Checkin', c.name, 'skip_auto_attendance', 1)
                    frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                return att  
            else:
                att = frappe.get_doc("Attendance",att)
                if not att.attendance_upload:
                    if att.docstatus == 0 or att.docstatus == 1 and not att.in_time:
                        # print(att.name)
                        att.employee = employee
                        att.attendance_date = att_date
                        if att.attendance_regularize and att.attendance_regularize is not None:
                            if frappe.db.exists("Attendance Regularize",{'name':att.attendance_regularize,'in_time':1}):
                                reg_in=frappe.db.get_value("Attendance Regularize",{'name':att.attendance_regularize,'in_time':1},['corrected_in'])
                                att.in_time =reg_in
                            else:
                                att.in_time =before_in[0]['time']
                        else:
                            if att.out_time:
                                if att.out_time > before_in[0]['time']:
                                    att.in_time =before_in[0]['time']
                            else:
                                att.in_time =before_in[0]['time']
                        if att.attendance_regularize and att.attendance_regularize is not None:
                            if frappe.db.exists("Attendance Regularize",{'name':att.attendance_regularize,'shift':1}):
                                reg_in=frappe.db.get_value("Attendance Regularize",{'name':att.attendance_regularize,'shift':1},['corrected_shift'])
                                att.shift =reg_in
                            else:
                                att.shift = get_actual_shift_start(get_time(before_in[0]['time']))
                        else:
                            att.shift = get_actual_shift_start(get_time(before_in[0]['time']))
                        # att.late_entry_time = "00:00:00"
                        # att.early_out_time = "00:00:00"
                        att.save(ignore_permissions=True)
                        frappe.db.commit()
                        for c in before_in:
                            frappe.db.set_value('Employee Checkin', c.name, 'skip_auto_attendance', 1)
                            frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                        return att 
        if after_in and not before_in:
            att = frappe.db.exists('Attendance',{"employee":employee,'attendance_date':att_date,'docstatus':['!=','2']})   
            if not att:
                att = frappe.new_doc("Attendance")
                att.employee = employee
                att.attendance_date = att_date
                att.shift = get_actual_shift_start(get_time(after_in[0].time))
                att.status = 'Absent'
                att.in_time = after_in[0].time
                att.total_working_hours = "00:00:00"
                att.working_hours = "0.0"
                att.extra_hours = "0.0"
                att.total_extra_hours = "00:00:00"
                att.total_overtime_hours = "00:00:00"
                att.overtime_hours = "0.0"
                att.late_entry_time = "00:00:00"
                att.early_out_time = "00:00:00"
                att.save(ignore_permissions=True)
                frappe.db.commit()
                for c in after_in:
                    frappe.db.set_value('Employee Checkin', c.name, 'skip_auto_attendance', 1)
                    frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                return att  
            else:
                att = frappe.get_doc("Attendance",att)
                if not att.attendance_upload:
                    if att.docstatus == 0 or att.docstatus == 1:
                        att.employee = employee
                        att.attendance_date = att_date
                        # att.shift = shift
                        # att.status = 'Absent'
                        if att.attendance_regularize and att.attendance_regularize is not None:
                            if frappe.db.exists("Attendance Regularize",{'name':att.attendance_regularize,'in_time':1}):
                                reg_in=frappe.db.get_value("Attendance Regularize",{'name':att.attendance_regularize,'in_time':1},['corrected_in'])
                                att.in_time =reg_in
                            else:
                                att.in_time =after_in[0]['time']
                        else:
                            att.in_time =after_in[0]['time']
                        # att.in_time =after_in[0]['time']
                        if att.attendance_regularize and att.attendance_regularize is not None:
                            if frappe.db.exists("Attendance Regularize",{'name':att.attendance_regularize,'shift':1}):
                                reg_in=frappe.db.get_value("Attendance Regularize",{'name':att.attendance_regularize,'shift':1},['corrected_shift'])
                                att.shift =reg_in
                            else:
                                att.shift = get_actual_shift_start(get_time(after_in[0]['time']))
                        else:
                            att.shift = get_actual_shift_start(get_time(after_in[0]['time']))
                        # att.total_working_hours = "00:00:00"
                        # att.working_hours = "0.0"
                        # att.extra_hours = "0.0"
                        # att.total_extra_hours = "00:00:00"
                        # att.total_overtime_hours = "00:00:00"
                        # att.overtime_hours = "0.0"
                        # att.late_entry_time = "00:00:00"
                        # att.early_out_time = "00:00:00"
                        att.save(ignore_permissions=True)
                        frappe.db.commit()
                        for c in after_in:
                            frappe.db.set_value('Employee Checkin', c.name, 'skip_auto_attendance', 1)
                            frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                        return att
        if after_in and before_in:
            if before_in:
                prev_date = add_days(att_date,-1)
                prev_att = frappe.db.exists('Attendance',{"employee":employee,'attendance_date':prev_date,'docstatus':['!=','2']})   
                if not prev_att:
                    prev_att = frappe.new_doc("Attendance")
                    prev_att.employee = employee
                    prev_att.attendance_date = prev_date
                    if not prev_att.shift:
                        prev_att.shift = get_actual_shift_start(get_time(before_in[0].time))
                    prev_att.status = 'Absent'
                    prev_att.in_time = before_in[0].time
                    prev_att.total_working_hours = "00:00:00"
                    prev_att.working_hours = "0.0"
                    prev_att.extra_hours = "0.0"
                    prev_att.total_extra_hours = "00:00:00"
                    prev_att.total_overtime_hours = "00:00:00"
                    prev_att.overtime_hours = "0.0"
                    prev_att.late_entry_time = "00:00:00"
                    prev_att.early_out_time = "00:00:00"
                    prev_att.save(ignore_permissions=True)
                    frappe.db.commit()
                    for c in before_in:
                        frappe.db.set_value('Employee Checkin', c.name, 'skip_auto_attendance', 1)
                        frappe.db.set_value("Employee Checkin",c.name, "attendance", prev_att.name)
                    return prev_att  
                else:
                    prev_att = frappe.get_doc("Attendance",prev_att)
                    if not prev_att.attendance_upload:
                        if (prev_att.docstatus == 0 or prev_att.docstatus == 1) and not prev_att.in_time:
                            prev_att.employee = employee
                            prev_att.attendance_date = prev_date
                            # prev_att.shift = shift
                            # prev_att.status = 'Absent'
                            if prev_att.attendance_regularize and prev_att.attendance_regularize is not None:
                                if frappe.db.exists("Attendance Regularize",{'name':prev_att.attendance_regularize,'in_time':1}):
                                    reg_in=frappe.db.get_value("Attendance Regularize",{'name':prev_att.attendance_regularize,'in_time':1},['corrected_in'])
                                    prev_att.in_time =reg_in
                                else:
                                    prev_att.in_time =before_in[0]['time']
                            else:
                                prev_att.in_time =before_in[0]['time']
                            # prev_att.in_time =before_in[0]['time']
                            if prev_att.attendance_regularize and prev_att.attendance_regularize is not None:
                                if frappe.db.exists("Attendance Regularize",{'name':prev_att.attendance_regularize,'shift':1}):
                                    reg_in=frappe.db.get_value("Attendance Regularize",{'name':prev_att.attendance_regularize,'shift':1},['corrected_shift'])
                                    prev_att.shift =reg_in
                                else:
                                    prev_att.shift = get_actual_shift_start(get_time(before_in[0]['time']))
                            else:
                                prev_att.shift = get_actual_shift_start(get_time(before_in[0]['time']))
                            # prev_att.total_working_hours = "00:00:00"
                            # prev_att.working_hours = "0.0"
                            # prev_att.extra_hours = "0.0"
                            # prev_att.total_extra_hours = "00:00:00"
                            # prev_att.total_overtime_hours = "00:00:00"
                            # prev_att.overtime_hours = "0.0"
                            # prev_att.late_entry_time = "00:00:00"
                            # prev_att.early_out_time = "00:00:00"
                            prev_att.save(ignore_permissions=True)
                            frappe.db.commit()
                            for c in before_in:
                                frappe.db.set_value('Employee Checkin', c.name, 'skip_auto_attendance', 1)
                                frappe.db.set_value("Employee Checkin",c.name, "attendance", prev_att.name)
                            # return prev_att
            
            att = frappe.db.exists('Attendance',{"employee":employee,'attendance_date':att_date,'docstatus':['!=','2']})   
            if not att:
                # print('attnot')
                att = frappe.new_doc("Attendance")
                att.employee = employee
                att.attendance_date = att_date
                att.shift = get_actual_shift_start(get_time(after_in[0].time))
                att.status = 'Absent'
                att.in_time = after_in[0].time
                att.total_working_hours = "00:00:00"
                att.working_hours = "0.0"
                att.extra_hours = "0.0"
                att.total_extra_hours = "00:00:00"
                att.total_overtime_hours = "00:00:00"
                att.overtime_hours = "0.0"
                att.late_entry_time = "00:00:00"
                att.early_out_time = "00:00:00"
                att.save(ignore_permissions=True)
                frappe.db.commit()
                for c in after_in:
                    frappe.db.set_value('Employee Checkin', c.name, 'skip_auto_attendance', 1)
                    frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                return att  
            else:
                # print('presentatt')
                att = frappe.get_doc("Attendance",att)
                if not att.attendance_upload:
                    if att.docstatus == 0 or att.docstatus == 1:
                        att.employee = employee
                        att.attendance_date = att_date
                        # att.shift = shift
                        # att.status = 'Absent'
                        if att.attendance_regularize and att.attendance_regularize is not None:
                            if frappe.db.exists("Attendance Regularize",{'name':att.attendance_regularize,'in_time':1}):
                                reg_in=frappe.db.get_value("Attendance Regularize",{'name':att.attendance_regularize,'in_time':1},['corrected_in'])
                                att.in_time =reg_in
                            else:
                                att.in_time =after_in[0]['time']
                        else:
                            att.in_time =after_in[0]['time']
                        # att.in_time =after_in[0].time
                        # print(after_in[0].time)
                        # print(att.in_time)
                        if att.attendance_regularize and att.attendance_regularize is not None:
                            if frappe.db.exists("Attendance Regularize",{'name':att.attendance_regularize,'shift':1}):
                                reg_in=frappe.db.get_value("Attendance Regularize",{'name':att.attendance_regularize,'shift':1},['corrected_shift'])
                                att.shift =reg_in
                            else:
                                att.shift = get_actual_shift_start(get_time(after_in[0].time))
                        else:
                            att.shift = get_actual_shift_start(get_time(after_in[0].time))
                        # att.total_working_hours = "00:00:00"
                        # att.working_hours = "0.0"
                        # att.extra_hours = "0.0"
                        # att.total_extra_hours = "00:00:00"
                        # att.total_overtime_hours = "00:00:00"
                        # att.overtime_hours = "0.0"
                        # att.late_entry_time = "00:00:00"
                        # att.early_out_time = "00:00:00"
                        att.save(ignore_permissions=True)
                        frappe.db.commit()
                        for c in after_in:
                            frappe.db.set_value('Employee Checkin', c.name, 'skip_auto_attendance', 1)
                            frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                        return att
    if log_type == 'OUT':
        
        # shift = ''
        att_date = time.date()
        att_time = time.time()
        max_out = datetime.strptime('10:30','%H:%M').time()
        max_in = datetime.strptime('05:30','%H:%M').time()
        if att_time < max_out:
            # yesterday = add_days(att_date,-1)
            # checkins = frappe.db.sql("""select * from `tabEmployee Checkin` where employee = '%s' and log_type = 'OUT' and date(time) = '%s' and TIME(time) < '%s' order by time ASC """%(employee,att_date,max_out),as_dict=True)
            checkins=''
            yesterday=''
            today_att = frappe.db.exists("Attendance",{'employee':employee,'attendance_date':att_date})
            if today_att:
                attendance_doc = frappe.get_doc("Attendance",today_att)
                if not attendance_doc.attendance_upload:
                    if attendance_doc.in_time:
                        checkins = frappe.db.sql("""select * from `tabEmployee Checkin` where employee ='%s' and log_type = 'OUT' and date(time) = '%s' and TIME(time) < '%s' and time < '%s'order by time ASC"""%(employee,att_date,max_out,attendance_doc.in_time),as_dict=True)
                        if checkins:
                            yesterday = add_days(att_date,-1)
                        else:
                            yesterday=att_date
                    else:
                        checkins = frappe.db.sql("""select * from `tabEmployee Checkin` where employee ='%s' and log_type = 'OUT' and date(time) = '%s' and TIME(time) < '%s' order by time ASC"""%(employee,att_date,max_out),as_dict=True)
                        yesterday = add_days(att_date,-1)
            else:
                checkins = frappe.db.sql("""select * from `tabEmployee Checkin` where employee ='%s' and log_type = 'OUT' and date(time) = '%s' and TIME(time) < '%s' order by time ASC"""%(employee,att_date,max_out),as_dict=True)
                yesterday = add_days(att_date,-1)
            if not yesterday:
                yesterday = add_days(att_date,-1)
            att = frappe.db.exists("Attendance",{'employee':employee,'attendance_date':yesterday})	
            if att:
                att = frappe.get_doc("Attendance",att)
                if not att.attendance_upload:
                    if att.docstatus != 2:
                            if att.out_time is None:
                                if not att.shift:
                                    if att.attendance_regularize and att.attendance_regularize is not None:
                                        if frappe.db.exists("Attendance Regularize",{'name':att.attendance_regularize,'out_time':1}):
                                            reg_in=frappe.db.get_value("Attendance Regularize",{'name':att.attendance_regularize,'out_time':1},['corrected_out'])
                                            att.out_time =reg_in
                                        else:
                                            if len(checkins) > 0:
                                                att.shift = get_actual_shift(get_time(checkins[-1].time))
                                                att.out_time = checkins[-1].time
                                                for c in checkins:
                                                    frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance',1)
                                                    frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                                            else:
                                                if checkins:
                                                    att.shift = get_actual_shift(get_time(checkins[0].time))
                                                    att.out_time = checkins[0].time
                                                    frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance',1)
                                                    frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
                                    else:
                                        if len(checkins) > 0:
                                            att.shift = get_actual_shift(get_time(checkins[-1].time))
                                            att.out_time = checkins[-1].time
                                            for c in checkins:
                                                frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance',1)
                                                frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                                        else:
                                            if checkins:
                                                att.shift = get_actual_shift(get_time(checkins[0].time))
                                                att.out_time = checkins[0].time
                                                frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance',1)
                                                frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
                                else:
                                    if att.attendance_regularize and att.attendance_regularize is not None:
                                        if frappe.db.exists("Attendance Regularize",{'name':att.attendance_regularize,'out_time':1}):
                                            reg_in=frappe.db.get_value("Attendance Regularize",{'name':att.attendance_regularize,'out_time':1},['corrected_out'])
                                            att.out_time =reg_in
                                        else:
                                            if len(checkins) > 0:
                                                att.out_time = checkins[-1].time
                                                for c in checkins:
                                                    frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance',1)
                                                    frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                                            else:
                                                if checkins:
                                                    att.out_time = checkins[0].time
                                                    frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance',1)
                                                    frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
                                    else:
                                        if len(checkins) > 0:
                                            att.out_time = checkins[-1].time
                                            for c in checkins:
                                                frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance',1)
                                                frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                                        else:
                                            if checkins:
                                                att.out_time = checkins[0].time
                                                frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance',1)
                                                frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
                                # att.status = 'Absent'    
                                att.save(ignore_permissions=True)
                                frappe.db.commit()
                                return att
                            else:
                                if not att.shift:
                                    if att.attendance_regularize and att.attendance_regularize is not None:
                                        if frappe.db.exists("Attendance Regularize",{'name':att.attendance_regularize,'out_time':1}):
                                            reg_in=frappe.db.get_value("Attendance Regularize",{'name':att.attendance_regularize,'out_time':1},['corrected_out'])
                                            att.out_time =reg_in
                                        else:
                                            if len(checkins) > 0:
                                                att.shift = get_actual_shift(get_time(checkins[-1].time))
                                                att.out_time = checkins[-1].time
                                                for c in checkins:
                                                    frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance',1)
                                                    frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                                            else:
                                                if checkins:
                                                    att.out_time = checkins[0].time
                                                    att.shift = get_actual_shift(get_time(checkins[0].time))
                                                    frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance',1)
                                                    frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
                                    else:
                                        if len(checkins) > 0:
                                            att.shift = get_actual_shift(get_time(checkins[-1].time))
                                            att.out_time = checkins[-1].time
                                            for c in checkins:
                                                frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance',1)
                                                frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                                        else:
                                            if checkins:
                                                att.out_time = checkins[0].time
                                                att.shift = get_actual_shift(get_time(checkins[0].time))
                                                frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance',1)
                                                frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
                                    
                                else:
                                    if att.attendance_regularize and att.attendance_regularize is not None:
                                        if frappe.db.exists("Attendance Regularize",{'name':att.attendance_regularize,'out_time':1}):
                                            reg_in=frappe.db.get_value("Attendance Regularize",{'name':att.attendance_regularize,'out_time':1},['corrected_out'])
                                            att.out_time =reg_in
                                        else:
                                            if len(checkins) > 0:
                                                att.out_time = checkins[-1].time
                                                for c in checkins:
                                                    frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance',1)
                                                    frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                                            else:
                                                if checkins:
                                                    att.out_time = checkins[0].time
                                                    frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance',1)
                                                    frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
                                    else:
                                        # frappe.errprint("TEST PRINT OUT")
                                        if len(checkins) > 0:
                                            # frappe.errprint(att.name)
                                            # frappe.errprint(checkins[-1].time)
                                            att.out_time = checkins[-1].time
                                            for c in checkins:
                                                frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance',1)
                                                frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                                        else:
                                            if checkins:
                                                att.out_time = checkins[0].time
                                                frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance',1)
                                                frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
                                att.save(ignore_permissions=True)
                                frappe.db.commit()
                                return att
                
            else:
                att = frappe.new_doc("Attendance")
                att.employee = employee
                att.attendance_date = yesterday
                att.status = 'Absent'
                if len(checkins) > 0:
                    att.out_time = checkins[-1].time
                    att.shift = get_actual_shift(get_time(checkins[-1].time))
                    for c in checkins:
                        frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance',1)
                        frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                else:
                    att.out_time = checkins[0].time
                    att.shift = get_actual_shift(get_time(checkins[0].time))
                    frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance',1)
                    frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
                att.total_working_hours = "00:00:00"
                att.working_hours = "0.0"
                att.extra_hours = "0.0"
                att.total_extra_hours = "00:00:00"
                att.total_overtime_hours = "00:00:00"
                att.overtime_hours = "0.0"
                att.late_entry_time = "00:00:00"
                att.early_out_time = "00:00:00"
                att.save(ignore_permissions=True)
                frappe.db.commit()
                for c in checkins:
                    frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance',1)
                    frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                return att	
        else:
            checkins = frappe.db.sql("""select * from `tabEmployee Checkin` where employee ='%s' and log_type = 'OUT' and date(time) = '%s' and TIME(time) > '%s' order by time ASC"""%(employee,att_date,max_out),as_dict=True)
            att = frappe.db.exists("Attendance",{'employee':employee,'attendance_date':att_date})
            today_checkins=''
            today_att = frappe.db.exists("Attendance",{'employee':employee,'attendance_date':att_date})
            if today_att:
                attendance_doc = frappe.get_doc("Attendance",today_att)
                if not attendance_doc.attendance_upload:
                    if attendance_doc.in_time:
                        today_checkins = frappe.db.sql("""select * from `tabEmployee Checkin` where employee ='%s' and log_type = 'OUT' and date(time) = '%s' and TIME(time) > '%s' and time < '%s'order by time ASC"""%(employee,att_date,max_out,attendance_doc.in_time),as_dict=True)
                    else:
                        today_checkins = frappe.db.sql("""select * from `tabEmployee Checkin` where employee ='%s' and log_type = 'OUT' and date(time) = '%s' and TIME(time) > '%s' order by time ASC"""%(employee,att_date,max_out),as_dict=True)
            else:
                today_checkins = frappe.db.sql("""select * from `tabEmployee Checkin` where employee ='%s' and log_type = 'OUT' and date(time) = '%s' and TIME(time) > '%s' order by time ASC"""%(employee,att_date,max_out),as_dict=True)
            yesterday = add_days(att_date,-1)
            if frappe.db.exists("Attendance",{'employee':employee,'attendance_date':yesterday,'in_time':['!=',''],'shift':'C','docstatus':['!=',2]}) and today_checkins:
                prev_att = frappe.get_doc("Attendance",{'employee':employee,'attendance_date':yesterday,'in_time':['!=',''],'shift':'C','docstatus':['!=',2]})
                if prev_att.attendance_regularize and prev_att.attendance_regularize is not None:
                    if frappe.db.exists("Attendance Regularize",{'name':prev_att.attendance_regularize,'out_time':1}):
                        reg_in=frappe.db.get_value("Attendance Regularize",{'name':prev_att.attendance_regularize,'out_time':1},['corrected_out'])
                        prev_att.out_time =reg_in
                    else:
                        prev_att.out_time =today_checkins[0]['time']
                else:
                    if not prev_att.attendance_upload:
                        prev_att.out_time =today_checkins[0]['time']
                prev_att.save(ignore_permissions=True)
                frappe.db.commit()
                if prev_att.attendance_regularize and prev_att.attendance_regularize is not None:
                    if frappe.db.exists("Attendance Regularize",{'name':prev_att.attendance_regularize,'out_time':1}):
                        reg_in=frappe.db.get_value("Attendance Regularize",{'name':prev_att.attendance_regularize,'out_time':1},['corrected_out'])
                        prev_att.out_time =reg_in
                    else:
                        if len(today_checkins) > 0:
                            prev_att.out_time = today_checkins[-1].time  
                        else:
                            prev_att.out_time = today_checkins[0].time
                else:
                    if not prev_att.attendance_upload:
                        if len(today_checkins) > 0:
                            prev_att.out_time = today_checkins[-1].time  
                        else:
                            prev_att.out_time = today_checkins[0].time
                for c in today_checkins:
                    frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance',1)
                    frappe.db.set_value("Employee Checkin",c.name, "attendance", prev_att.name)
            else:
                if att:
                    att = frappe.get_doc("Attendance",att)
                    if not att.attendance_upload:
                        if att.docstatus != 2:
                            # if att.status != 'Present': 
                                if not att.out_time:
                                    if not att.shift:
                                        if att.attendance_regularize and att.attendance_regularize is not None:
                                            if frappe.db.exists("Attendance Regularize",{'name':att.attendance_regularize,'out_time':1}):
                                                reg_in=frappe.db.get_value("Attendance Regularize",{'name':att.attendance_regularize,'out_time':1},['corrected_out'])
                                                att.out_time =reg_in
                                            else:
                                                if len(checkins) > 0:
                                                    att.shift = get_actual_shift(get_time(checkins[-1].time))
                                                    att.out_time = checkins[-1].time
                                                    for c in checkins:
                                                        frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance',1)
                                                        frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                                                else:
                                                    att.shift = get_actual_shift(get_time(checkins[0].time))
                                                    att.out_time = checkins[0].time
                                                    frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance',1)
                                                    frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
                                        else:
                                            if att.attendance_regularize and att.attendance_regularize is not None:
                                                if frappe.db.exists("Attendance Regularize",{'name':att.attendance_regularize,'out_time':1}):
                                                    reg_in=frappe.db.get_value("Attendance Regularize",{'name':att.attendance_regularize,'out_time':1},['corrected_out'])
                                                    att.out_time =reg_in
                                                else:
                                                    if len(checkins) > 0:
                                                        att.shift = get_actual_shift(get_time(checkins[-1].time))
                                                        att.out_time = checkins[-1].time
                                                        for c in checkins:
                                                            frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance',1)
                                                            frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                                                    else:
                                                        if checkins:
                                                            att.shift = get_actual_shift(get_time(checkins[0].time))
                                                            att.out_time = checkins[0].time
                                                            frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance',1)
                                                            frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
                                            else:
                                                if len(checkins) > 0:
                                                    att.shift = get_actual_shift(get_time(checkins[-1].time))
                                                    att.out_time = checkins[-1].time
                                                    for c in checkins:
                                                        frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance',1)
                                                        frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                                                else:
                                                    if checkins:
                                                        att.shift = get_actual_shift(get_time(checkins[0].time))
                                                        att.out_time = checkins[0].time
                                                        frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance',1)
                                                        frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
                                    else:
                                        if att.attendance_regularize and att.attendance_regularize is not None:
                                            if frappe.db.exists("Attendance Regularize",{'name':att.attendance_regularize,'out_time':1}):
                                                reg_in=frappe.db.get_value("Attendance Regularize",{'name':att.attendance_regularize,'out_time':1},['corrected_out'])
                                                att.out_time =reg_in
                                            else:
                                                if len(checkins) > 0:
                                                    att.out_time = checkins[-1].time
                                                    for c in checkins:
                                                        frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance',1)
                                                        frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                                                else:
                                                    if checkins:
                                                        att.out_time = checkins[0].time
                                                        frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance',1)
                                                        frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
                                        else:
                                            if len(checkins) > 0:
                                                att.out_time = checkins[-1].time
                                                for c in checkins:
                                                    frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance',1)
                                                    frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                                            else:
                                                if checkins:
                                                    att.out_time = checkins[0].time
                                                    frappe.db.set_value('Employee Checkin',checkins[0].name,'skip_auto_attendance',1)
                                                    frappe.db.set_value("Employee Checkin",checkins[0].name, "attendance", att.name)
                                    # att.status = 'Absent'    
                                    att.save(ignore_permissions=True)
                                    frappe.db.commit()
                                    return att
                                else:
                                    if att.attendance_regularize and att.attendance_regularize is not None:
                                        if frappe.db.exists("Attendance Regularize",{'name':att.attendance_regularize,'out_time':1}):
                                            reg_in=frappe.db.get_value("Attendance Regularize",{'name':att.attendance_regularize,'out_time':1},['corrected_out'])
                                            att.out_time =reg_in
                                        else:
                                            if len(checkins) > 0:
                                                att.out_time = checkins[-1].time
                                            else:
                                                if checkins:
                                                    att.out_time = checkins[0].time
                                    else:
                                        if len(checkins) > 0:
                                            att.out_time = checkins[-1].time
                                        else:
                                            if checkins:
                                                att.out_time = checkins[0].time
                                    if not att.shift:
                                        if  checkins:
                                            att.shift = get_actual_shift(get_time(checkins[-1].time))
                                att.save(ignore_permissions=True)
                                return att
                    
                else:
                    att = frappe.new_doc("Attendance")
                    att.employee = employee
                    att.attendance_date = att_date
                    # att.shift = shift
                    att.status = 'Absent'
                    if len(checkins) > 0:
                        att.shift = get_actual_shift(get_time(checkins[-1].time))
                        att.out_time = checkins[-1].time
                    else:
                        att.shift = get_actual_shift(get_time(checkins[0].time))
                        att.out_time = checkins[0].time
                    att.total_working_hours = "00:00:00"
                    att.working_hours = "0.0"
                    att.extra_hours = "0.0"
                    att.total_extra_hours = "00:00:00"
                    att.total_overtime_hours = "00:00:00"
                    att.overtime_hours = "0.0"
                    att.late_entry_time = "00:00:00"
                    att.early_out_time = "00:00:00"
                    att.save(ignore_permissions=True)
                    frappe.db.commit()
                    for c in checkins:
                        frappe.db.set_value('Employee Checkin',c.name,'skip_auto_attendance',1)
                        frappe.db.set_value("Employee Checkin",c.name, "attendance", att.name)
                    return att 

@frappe.whitelist()
def update_regularize_ot_with_employee(from_date,to_date,employee):
    attendance = frappe.db.get_all('Attendance', {'attendance_date': ('between', (from_date,to_date)),'docstatus': ('!=', '2'),'employee':employee,'attendance_regularize':('!=','')}, ['*'])
    for att in attendance:
        if frappe.db.exists("Attendance Regularize", {'name': att.attendance_regularize, 'docstatus': 1, 'ot_hours': 1}):
            ot = frappe.db.get_value("Attendance Regularize", {'name': att.attendance_regularize}, 'corrected_ot')
            if ot is None:
                continue  
            doc = frappe.get_doc("Attendance", att.name)
            doc.overtime_hours = ot
            try:
                ot_float = float(ot)
                if ot_float >= 24:
                    doc.total_overtime_hours = "23:59:59"
                else:
                    td = timedelta(hours=ot_float)
                    total_seconds = int(td.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    seconds = total_seconds % 60
                    doc.total_overtime_hours = f"{hours:02}:{minutes:02}:{seconds:02}"
            except ValueError:
                frappe.throw(f"Invalid overtime value: {ot}")

            doc.save(ignore_permissions=True)

@frappe.whitelist()
def update_regularize_ot(from_date,to_date):
    attendance = frappe.db.get_all('Attendance', {'attendance_date': ('between', (from_date,to_date)),'docstatus': ('!=', '2'),'attendance_regularize':('!=','')}, ['*'])
    for att in attendance:
        if frappe.db.exists("Attendance Regularize", {'name': att.attendance_regularize, 'docstatus': 1, 'ot_hours': 1}):
            ot = frappe.db.get_value("Attendance Regularize", {'name': att.attendance_regularize}, 'corrected_ot')
            if ot is None:
                continue  
            doc = frappe.get_doc("Attendance", att.name)
            doc.overtime_hours = ot
            try:
                ot_float = float(ot)
                if ot_float >= 24:
                    doc.total_overtime_hours = "23:59:59"
                else:
                    td = timedelta(hours=ot_float)
                    total_seconds = int(td.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    seconds = total_seconds % 60
                    doc.total_overtime_hours = f"{hours:02}:{minutes:02}:{seconds:02}"
            except ValueError:
                frappe.throw(f"Invalid overtime value: {ot}")

            doc.save(ignore_permissions=True)

@frappe.whitelist()
def update_regularize_ot_with_employee_type(from_date,to_date,employee_type):
    attendance = frappe.db.get_all('Attendance', {'attendance_date': ('between', (from_date,to_date)),'docstatus': ('!=', '2'),'employee_type':employee_type,'attendance_regularize':('!=','')}, ['*'])
    for att in attendance:
        if frappe.db.exists("Attendance Regularize", {'name': att.attendance_regularize, 'docstatus': 1, 'ot_hours': 1}):
            ot = frappe.db.get_value("Attendance Regularize", {'name': att.attendance_regularize}, 'corrected_ot')
            if ot is None:
                continue  
            doc = frappe.get_doc("Attendance", att.name)
            doc.overtime_hours = ot
            try:
                ot_float = float(ot)
                if ot_float >= 24:
                    doc.total_overtime_hours = "23:59:59"
                else:
                    td = timedelta(hours=ot_float)
                    total_seconds = int(td.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    seconds = total_seconds % 60
                    doc.total_overtime_hours = f"{hours:02}:{minutes:02}:{seconds:02}"
            except ValueError:
                frappe.throw(f"Invalid overtime value: {ot}")

            doc.save(ignore_permissions=True)

@frappe.whitelist()
def update_regularize_ot_with_con_name(from_date,to_date,employee_type,con_name):
    attendance = frappe.db.get_all('Attendance', {'attendance_date': ('between', (from_date,to_date)),'docstatus': ('!=', '2'),'employee_type':employee_type,'contractor':con_name,'attendance_regularize':('!=','')}, ['*'])
    for att in attendance:
        if frappe.db.exists("Attendance Regularize", {'name': att.attendance_regularize, 'docstatus': 1, 'ot_hours': 1}):
            ot = frappe.db.get_value("Attendance Regularize", {'name': att.attendance_regularize}, 'corrected_ot')
            if ot is None:
                continue  
            doc = frappe.get_doc("Attendance", att.name)
            doc.overtime_hours = ot
            try:
                ot_float = float(ot)
                if ot_float >= 24:
                    doc.total_overtime_hours = "23:59:59"
                else:
                    td = timedelta(hours=ot_float)
                    total_seconds = int(td.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    seconds = total_seconds % 60
                    doc.total_overtime_hours = f"{hours:02}:{minutes:02}:{seconds:02}"
            except ValueError:
                frappe.throw(f"Invalid overtime value: {ot}")

            doc.save(ignore_permissions=True)


@frappe.whitelist()
def update_location_with_employee(from_date, to_date, employee):
    attendance = frappe.db.get_all('Attendance', {'employee':employee,'attendance_date': ('between', (from_date, to_date)),'docstatus': ['!=',2]}, ['name'])
    for att in attendance:
        if frappe.db.exists("Employee Checkin",{"remarks": "Automatically created via mark attendance document",'attendance':att.name}):
           frappe.db.set_value("Attendance",att.name, "site", "NO")
        else:
            frappe.db.set_value("Attendance", att.name, "site", "YES")	  

@frappe.whitelist()
def update_location(from_date, to_date):
    attendance = frappe.db.get_all('Attendance', {'attendance_date': ('between', (from_date, to_date)),'docstatus': ['!=',2]}, ['name'])
    for att in attendance:
        if frappe.db.exists("Employee Checkin",{"remarks": "Automatically created via mark attendance document",'attendance':att.name}):
           frappe.db.set_value("Attendance",att.name, "site", "NO")
        else:
            frappe.db.set_value("Attendance", att.name, "site", "YES")  

@frappe.whitelist()
def update_location_with_employee_type(from_date, to_date,employee_type):
    attendance = frappe.db.get_all('Attendance', {'employee_type':employee_type,'attendance_date': ('between', (from_date, to_date)),'docstatus': ['!=',2]}, ['name'])
    for att in attendance:
        if frappe.db.exists("Employee Checkin",{"remarks": "Automatically created via mark attendance document",'attendance':att.name}):
           frappe.db.set_value("Attendance",att.name, "site", "NO")
        else:
            frappe.db.set_value("Attendance", att.name, "site", "YES")           
        
    
@frappe.whitelist()
def update_location_with_con_name(from_date, to_date,employee_type,con_name):
    attendance = frappe.db.get_all('Attendance', {'employee_type':employee_type,'contractor':con_name,'attendance_date': ('between', (from_date, to_date)),'docstatus': ['!=',2]}, ['name'])
    for att in attendance:
        if frappe.db.exists("Employee Checkin",{"remarks": "Automatically created via mark attendance document",'attendance':att.name}):
           frappe.db.set_value("Attendance",att.name, "site", "NO")
        else:
            frappe.db.set_value("Attendance", att.name, "site", "YES")
