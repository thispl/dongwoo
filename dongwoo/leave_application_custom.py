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




@frappe.whitelist()
def get_reasons(leave_type):
    doc = frappe.get_doc("Leave Type", leave_type)
    reasons = [reason.pre_defined_reason for reason in doc.pre_defined_reason_table]
    return reasons

@frappe.whitelist(allow_guest=True)
def get_leave_data(from_date, to_date, employee, year): 
    from_date_ = datetime.strptime(from_date, "%Y-%m-%d").strftime('%d-%m-%Y')
    to_date_ = datetime.strptime(to_date, "%Y-%m-%d").strftime('%d-%m-%Y')
    emp_data_list = frappe.db.get_all('Employee',{'name':employee},['first_name','date_of_joining','department','designation','employee_type'])
    emp_data = emp_data_list[0] 
    allocated_leave_list = frappe.db.sql("""
        select total_leaves_allocated,leave_type
        from `tabLeave Allocation`
        where docstatus != 2 and employee = %(employee)s
            and (from_date between %(from_date)s and %(to_date)s
                or to_date between %(from_date)s and %(to_date)s
                or (from_date < %(from_date)s and to_date > %(to_date)s))
        """, {
            "from_date": from_date,
            "to_date": to_date,
            "employee":employee,
        },
    as_dict = True)
    allocated_cl, allocated_sl, allocated_el =0,0,0
    for allocated_leave in allocated_leave_list:
        if allocated_leave['leave_type'] == 'Casual Leave (CL)':
            allocated_cl = allocated_leave['total_leaves_allocated']
        # else:
        #     allocated_cl =0
        if allocated_leave['leave_type'] == 'Sick Leave (SL)':
            allocated_sl = allocated_leave['total_leaves_allocated']
        # else:
        #     allocated_sl =0
        if allocated_leave['leave_type'] == 'Earned Leave (EL)':
            allocated_el = allocated_leave['total_leaves_allocated']
        # else:
        #     allocated_el =0
    leave_data = frappe.db.sql("""
                select leave_balance,from_date,to_date,total_leave_days,pre_defined_reason,leave_type,creation,modified
                from `tabLeave Application`
                where docstatus = 1 and workflow_state != 'Rejected' and employee = %(employee)s
                    and (from_date between %(from_date)s and %(to_date)s
                        or to_date between %(from_date)s and %(to_date)s
                        or (from_date < %(from_date)s and to_date > %(to_date)s))
                    order by creation 
                """, {
                    "from_date": from_date,
                    "to_date": to_date,
                    "employee":employee
                },
            as_dict = True)
    rows = ""
    index =0
    cl_leave_balance = float(allocated_cl) if allocated_cl else 0.0
    sl_leave_balance = float(allocated_sl) if allocated_sl else 0.0
    el_leave_balance = float(allocated_el) if allocated_el else 0.0
    cl_leave_type = ''
    sl_leave_type =''
    el_leave_type =''
    for leave in leave_data:
        index +=1
        if leave['leave_type'] in ['Casual Leave (CL)','Sick Leave (SL)','Earned Leave (EL)']:
            if leave['leave_type'] == 'Casual Leave (CL)':
                cl_leave_balance -= float(leave['total_leave_days'])
                cl_leave_type = '<span style="color: black; font-weight: bold;">✔</span>'
                sl_leave_type =''
                el_leave_type =''
            elif leave['leave_type'] == 'Sick Leave (SL)':
                sl_leave_type = '<span style="color: black; font-weight: bold;">✔</span>'
                cl_leave_type = ''
                el_leave_type =''
                sl_leave_balance -= float(leave['total_leave_days'])
            elif leave['leave_type'] == 'Earned Leave (EL)':
                el_leave_type = '<span style="color: black; font-weight: bold;">✔</span>'
                cl_leave_type = ''
                sl_leave_type =''
                el_leave_balance -= float(leave['total_leave_days'])
            creation_date = leave['creation'].strftime('%d-%m-%Y')
            modified_date = leave['modified'].strftime('%d-%m-%Y')
            leave_start_date = leave['from_date'].strftime('%d-%m-%Y')
            leave_end_date = leave['to_date'].strftime('%d-%m-%Y')
            rows += f"""
            <tr>
                <td style="border: 1px solid black;text-align: center;">{index}</td>
                <td style="border: 1px solid black;text-align: center;">{creation_date}</td>
                <td style="border: 1px solid black;text-align: center;">{modified_date}</td>
                <td style="border: 1px solid black;text-align: center;">{leave_start_date}</td>
                <td style="border: 1px solid black;text-align: center;">{leave_end_date}</td>
                <td style="border: 1px solid black;text-align: right;">{leave['total_leave_days']}</td>
                <td style="border: 1px solid black;text-align: center;">{cl_leave_type}</td>
                <td style="border: 1px solid black;text-align: center;">{sl_leave_type}</td>
                <td style="border: 1px solid black;text-align: center;">{el_leave_type}</td>
                <td style="border: 1px solid black;text-align: center;">{leave['pre_defined_reason']}</td>
                <td style="border: 1px solid black;text-align: right;">{cl_leave_balance}</td>
                <td style="border: 1px solid black;text-align: right;">{sl_leave_balance}</td>
                <td style="border: 1px solid black;text-align: right;">{el_leave_balance}</td>
            </tr>
            """
        
        
    doj = emp_data['date_of_joining'].strftime('%d-%m-%Y')
    data = f"""
    
    <div style="overflow-x: auto; color: black;">
            <table border="1" style="width: 100%; border-collapse: collapse; text-align: left;border: none;">
               
                
            <tr>
              <td rowspan="2" style="border: 1px solid black;text-align: center;"><strong>S.No.</strong></th>
              <td rowspan ="2" style="border: 1px solid black;text-align: center;"><strong>APPLTN. DATE</strong></td>
              <td rowspan="2" style="border: 1px solid black;text-align: center;"><strong>APPRVL DATE</strong></td>
              <td colspan="2" style="border: 1px solid black;text-align: center;"><strong>LEAVE DAYS</strong></td>
              <td rowspan="2" style="border: 1px solid black;text-align: center;"><strong>NO OF DAYS</strong></td>
              <td colspan="3" style="border: 1px solid black;text-align: center;"><strong>TYPE OF LEAVE</strong></td>
              <td rowspan="2" style="border: 1px solid black;text-align: center;"><strong>REASON FOR LEAVE</strong></td>
              <td colspan="3" style="border: 1px solid black;text-align: center;"><strong>BALANCE LEAVE</strong></td>
            </tr>
            <tr>
                <td style="border: 1px solid black;text-align: center;"><strong>FROM</strong></td>
                <td style="border: 1px solid black;text-align: center;"><strong>TO</strong></td>
                <td style="border: 1px solid black;text-align: center;"><strong>CL</strong></td>
                <td style="border: 1px solid black;text-align: center;"><strong>SL</strong></td>
                <td style="border: 1px solid black;text-align: center;"><strong>EL</strong></td>
                <td style="border: 1px solid black;text-align: center;"><strong>CL</strong></td>
                <td style="border: 1px solid black;text-align: center;"><strong>SL</strong></td>
                <td style="border: 1px solid black;text-align: center;"><strong>EL</strong></td>
                
            </tr>
                {rows}
        </table>
    </div>
    """
    return data



import frappe
from frappe.utils import getdate

@frappe.whitelist()
def restrict_leave(doc, method):
    if doc.leave_type == 'Casual Leave (CL)':
        if doc.total_leave_days>2:
            frappe.throw("Maximum 2 Casual leaves are allowed per month.")
        from_date = getdate(doc.from_date)
        to_date = getdate(doc.to_date)

        start = get_first_day(to_date)  
        last = get_last_day(to_date)

        leave = frappe.db.sql("""
            SELECT SUM(total_leave_days) as total_leave 
            FROM `tabLeave Application` 
            WHERE employee = %s 
            AND name != %s
            AND leave_type = 'Casual Leave (CL)'
            AND (
                (from_date >= %s AND from_date <= %s)  -- Leaves starting in the month
                OR (to_date >= %s AND to_date <= %s)  -- Leaves ending in the month
                OR (from_date <= %s AND to_date >= %s)  -- Leaves spanning across the month
            )
            AND docstatus != 2
        """, (doc.employee,doc.name, start, last, start, last, start, last), as_dict=True)
        
        total_leave = leave[0].total_leave or 0
        if frappe.db.exists("Leave Application",{'docstatus':['!=',2],'employee':doc.employee,'total_leave_days':2,'to_date':start}):
            total_leave=total_leave-1
        if frappe.db.exists("Leave Application",{'docstatus':['!=',2],'employee':doc.employee,'total_leave_days':2,'from_date':last}):
            total_leave=total_leave-1
        # total_leave += doc.total_leave_days
        if total_leave > 2:
            frappe.throw(f"Already 2 Casual Leaves applied in {to_date.strftime('%B')}.")
        else:
            total_leave+=doc.total_leave_days
            if total_leave > 2:
                frappe.throw(f"Only 2 Casual Leaves allowed for {to_date.strftime('%B')}.")

import frappe
from frappe.utils import get_first_day, get_last_day

@frappe.whitelist()
def restrict_leave_cl(doc, method):
    if doc.leave_type == 'Casual Leave (CL)':
        yesterday=add_days(doc.from_date,-1)
        while True:
            hh=check_holiday(yesterday,doc.employee)    
            if not hh:
                break      
            yesterday = add_days(yesterday, -1) 
        if frappe.db.exists("Leave Application",{'docstatus':['!=',2],'employee':doc.employee,'to_date':yesterday,'leave_type':'Sick Leave (SL)','total_leave_days':['>=',2]}):
            frappe.throw("Casual Leave (CL) is restricted to apply followed by Sick Leave (SL)")
        else:
            if frappe.db.exists("Leave Application",{'docstatus':['!=',2],'employee':doc.employee,'to_date':yesterday,'leave_type':'Sick Leave (SL)','total_leave_days':['<=',1]}):
                fdate=frappe.db.get_value("Leave Application",{'docstatus':['!=',2],'employee':doc.employee,'to_date':yesterday,'leave_type':'Sick Leave (SL)','total_leave_days':['<=',1]},['from_date'])
                yesterday=add_days(fdate,-1)
                while True:
                    hh=check_holiday(yesterday,doc.employee)    
                    if not hh:
                        break      
                    yesterday = add_days(yesterday, -1)
                if frappe.db.exists("Leave Application",{'docstatus':['!=',2],'employee':doc.employee,'to_date':yesterday,'leave_type':'Sick Leave (SL)','total_leave_days':['<=',1]}):
                    frappe.throw("Casual Leave (CL) is restricted to apply followed by Sick Leave (SL)")

