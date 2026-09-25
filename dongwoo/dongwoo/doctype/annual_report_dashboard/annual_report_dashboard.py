# Copyright (c) 2025, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta, date, time
import datetime as dt
class AnnualReportDashboard(Document):
	pass

from datetime import datetime

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
                where docstatus != 2 and workflow_state != 'Rejected' and employee = %(employee)s
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
    <h2 class='text-center' style="color: black;">Form No: 15</h2>
    <h5 style="text-align: center;">(Prescribed under Rules 87 & 88 of Tamilnadu Factories Rules, 1950)</h5>
    <h3 style="text-align: center;">DWSI - LEAVE CARD FOR THE YEAR - {year}</h3>
    <div style="overflow-x: auto; color: black;">
            <table border="1" style="width: 100%; border-collapse: collapse; text-align: left;border: none;">
                <tr>
                    <td colspan="2" style ='border: none;'><strong>NAME</strong></td>
                    <td colspan="5" style ='border: none;'>:&nbsp;&nbsp;{emp_data['first_name']}</td>
                    <td colspan="2" style ='border: none;'><strong>DIVISION</strong></td>
                    <td colspan="1" style ='border: none;'>:&nbsp;&nbsp;{emp_data['employee_type']}</td>
                    <td colspan="3" style="border: 1px solid black;"><strong>Total Leave in {year}</strong></td>
                </tr>
                <tr>
                    <td colspan="2" style ='border: none;'><strong>DESIGNATION</strong></td>
                    <td colspan="5" style ='border: none;'>:&nbsp;&nbsp;{emp_data['designation']}</td>
                    <td colspan="2" style ='border: none;'><strong>DEPT</strong></td>
                    <td colspan="1" style ='border: none;'>:&nbsp;&nbsp;{emp_data['department']}</td>
                    <td style="border: 1px solid black;text-align: center;"><strong>CL</strong></td>
                    <td style="border: 1px solid black;text-align: center;"><strong>SL</strong></td>
                    <td style="border: 1px solid black;text-align: center;"><strong>EL</strong></td>
                </tr>
                <tr>
                    <td colspan="2" style ='border: none;'><strong>EMP NO</strong></td>
                    <td colspan="5" style ='border: none;'>:&nbsp;&nbsp;{employee}</td>
                    <td colspan="2" style ='border: none;'><strong>DOJ</strong></td>
                    <td colspan="1" style ='border: none;'>:&nbsp;&nbsp;{doj}</td>
                    <td style="border: 1px solid black;text-align: right;"><strong>{allocated_cl}</strong></td>
                    <td style="border: 1px solid black;text-align: right;"><strong>{allocated_sl}</strong></td>
                    <td style="border: 1px solid black;text-align: right;"><strong>{allocated_el}</strong></td>
                </tr>
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




@frappe.whitelist(allow_guest=True)
def get_permission_data(year,from_date, to_date, employee): 
    from_date_ = datetime.strptime(from_date, "%Y-%m-%d").strftime('%d-%m-%Y')
    to_date_ = datetime.strptime(to_date, "%Y-%m-%d").strftime('%d-%m-%Y')
    emp_data_list = frappe.db.get_all('Employee',{'name':employee},['first_name','date_of_joining','department','designation','employee_type'])
    emp_data = emp_data_list[0] 
    rows = ""
    count = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24']
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    m_index= -1
    index1 = -1
    index2 = 0
    for c in range(1, 25, (25 - 1) // 12):
        m_index+=1
        index1 += 2
        index2 += 2
        start_date, end_date = get_month_start_and_end(year, months[m_index])
        # frappe.errprint(f"{start_date}{end_date}")
        permission_data = frappe.db.sql("""
            select posting_date,permission_date,total_time,reason,permission_from_time,permission_to_time,modified,session,shift
            from `tabPermission`
            where docstatus != 2 and employee = %(employee)s
                and (permission_date between %(from_date)s and %(to_date)s)
                order by creation 
            """, {
                "from_date": start_date,
                "to_date": end_date,
                "employee":employee
            },
        as_dict = True)
        frappe.errprint(len(permission_data))
        if permission_data:
            first_permission = True
            total_perm_hours =0
            creation_date2 =''
            modified_date2 =''
            permission_date2 =''
            permission_from_time2 =''
            permission_to_time2 =''
            total_time2 = 0
            reason2 =''
            for perm in permission_data:
                frappe.errprint(perm)
                permission = perm
                if permission:
                    if first_permission:
                        first_permission = False
                        creation_date1 = permission['posting_date'].strftime('%d-%m-%Y') if permission['posting_date'] else ''
                        modified_date1 = permission['modified'].strftime('%d-%m-%Y') if permission['modified'] else ''
                        permission_date1 = permission['permission_date'].strftime('%d-%m-%Y') if permission['permission_date'] else ''
                        total_time1=permission['total_time'] if permission['total_time'] else 0.0
                        reason1 = permission['reason'] if permission['reason'] else ''
                        total_perm_hours += float(total_time1)
                        shift1 = permission['shift']
                        session1 = permission['session']
                        
                        frappe.errprint(shift1)
                        if shift1:
                            frappe.errprint(session1)
                            if session1 == 'First Half':
                                get_shift_time = frappe.db.get_value('Shift Type',{'name':shift1},['start_time'])
                                frappe.errprint(get_shift_time)
                                permission_from_time1 = get_shift_time
                                if total_time1 == 1:
                                    frappe.errprint(total_time1)
                                    permission_to_time1 = timedelta(hours=1) + get_shift_time
                                elif total_time1 == 2:
                                    permission_to_time1 = timedelta(hours=2) + get_shift_time
                                elif total_time1 == 3:
                                    permission_to_time1 = timedelta(hours=3) + get_shift_time
                                elif total_time1 == 4:
                                    permission_to_time1 = timedelta(hours=4) + get_shift_time
                            elif session1 == 'Second Half':
                                frappe.errprint('aaaa')
                                get_shift_end_time = frappe.db.get_value('Shift Type',{'name':shift1},['end_time'])
                                permission_to_time1 = get_shift_end_time
                                if total_time1 == 1:
                                    frappe.errprint(permission_from_time1)
                                    permission_from_time1 = get_shift_end_time - timedelta(hours=1)
                                    frappe.errprint(permission_from_time1)
                                elif total_time1 == 2:
                                    permission_from_time1 = get_shift_end_time - timedelta(hours=2)
                                elif total_time1 == 3:
                                    permission_from_time1 = get_shift_end_time - timedelta(hours=3)
                                elif total_time1 == 4:
                                    permission_from_time1 = get_shift_end_time - timedelta(hours=4)
                            else:
                                permission_from_time1 = permission['permission_from_time'] if permission['permission_from_time'] else ''
                                permission_to_time1 = permission['permission_to_time'] if permission['permission_to_time'] else ''

                    elif not first_permission:
                        creation_date2 = permission['posting_date'].strftime('%d-%m-%Y') if permission['posting_date'] else ''
                        modified_date2 = permission['modified'].strftime('%d-%m-%Y') if permission['modified'] else ''
                        permission_date2 = permission['permission_date'].strftime('%d-%m-%Y') if permission['permission_date'] else ''
                        permission_from_time2 = permission['permission_from_time'] if permission['permission_from_time'] else ''
                        permission_to_time2 = permission['permission_to_time'] if permission['permission_to_time'] else ''
                        total_time2 = permission['total_time'] if permission['total_time'] else 0.0
                        reason2 = permission['reason'] if permission['reason'] else ''
                        total_perm_hours += float(total_time2)
                        shift2 =permission['shift']
                        session2 = permission['session']
                        frappe.errprint(shift2)
                        if shift2:
                            frappe.errprint(session2)
                            if session2 == 'First Half':
                                get_shift_start_time2 = frappe.db.get_value('Shift Type',{'name':shift2},['start_time'])
                                permission_from_time2 = get_shift_start_time2
                                frappe.errprint(get_shift_start_time2)
                                if total_time2 == 1:
                                    frappe.errprint(total_time2)
                                    permission_to_time2 = timedelta(hours=1) + get_shift_start_time2
                                elif total_time2 == 2:
                                    permission_to_time2 = timedelta(hours=2) + get_shift_start_time2
                                elif total_time2 == 3:
                                    permission_to_time2 = timedelta(hours=3) + get_shift_start_time2
                                elif total_time2 == 4:
                                    permission_to_time2 = timedelta(hours=4) + get_shift_start_time2
                            elif session2 == 'Second Half':
                                frappe.errprint(session2)
                                frappe.errprint("total_time2")
                                get_shift_end_time2 = frappe.db.get_value('Shift Type',{'name':shift2},['end_time'])
                                permission_to_time2 = get_shift_end_time2
                                frappe.errprint(get_shift_end_time2)
                                frappe.errprint(total_time2)
                                if int(total_time2) == 1:
                                    frappe.errprint(get_shift_end_time2)
                                    permission_from_time2 = get_shift_end_time2 - timedelta(hours=1)
                                    frappe.errprint(get_shift_end_time2)
                                elif total_time2 == 2:
                                    permission_from_time2 = get_shift_end_time2 - timedelta(hours=2)
                                elif total_time2 == 3:
                                    permission_from_time2 = get_shift_end_time2 - timedelta(hours=3)
                                elif total_time2 == 4:
                                    permission_from_time2 = get_shift_end_time2 - timedelta(hours=4)
                            else:
                                permission_from_time2 = permission['permission_from_time'] if permission['permission_from_time'] else ''
                                permission_to_time2 = permission['permission_to_time'] if permission['permission_to_time'] else ''
            rows += f"""
                <tr>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{index1}</td>
                    <td rowspan="2" style="text-align: center; border: 1px solid black;">{months[m_index]}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{creation_date1}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{modified_date1}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{permission_date1}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{permission_from_time1}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{permission_to_time1}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{total_time1}</td>
                    <td rowspan="2" style="text-align: center; border: 1px solid black;">{total_perm_hours}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{reason1}</td>
                </tr>
                <tr>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{index2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{creation_date2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{modified_date2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{permission_date2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{permission_from_time2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{permission_to_time2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{total_time2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{reason2}</td>
                </tr>
                """        
        else:
            rows += f"""
                <tr>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{index1}</td>
                    <td rowspan="2" style="text-align: center; border: 1px solid black;">{months[m_index]}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td rowspan="2" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                </tr>
                <tr>
                    <td colspan="1" style="text-align: center;border: 1px solid black;">{index2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                </tr>
            """
        
    doj = emp_data['date_of_joining'].strftime('%d-%m-%Y')
    data = f"""
    <h3 style="text-align: center;">DWSI - PERMISSION CARD FOR THE YEAR - {year}</h3>
    <div style="overflow-x: auto; color: black;">

        <table border="0" style="width: 100%; border-collapse: collapse; text-align: left;border: none;">
            <tr>
                <td colspan="3"><strong>NAME</strong></td>
                <td colspan="4">:&nbsp;&nbsp;{emp_data['first_name']}</td>
                <td colspan="1"><strong>DIVISION</strong></td>
                <td>:&nbsp;&nbsp;{emp_data['employee_type']}</td>
            </tr>
            <tr>
                <td colspan="3"><strong>DESIGNATION</strong></td>
                <td colspan="4">:&nbsp;&nbsp;{emp_data['designation']}</td>
                <td colspan="1"><strong>DEPT</strong></td>
                <td>:&nbsp;&nbsp;{emp_data['department']}</td>
            </tr>
            <tr>
                <td colspan="3"><strong>EMP NO</strong></td>
                <td colspan="4">:&nbsp;&nbsp;{employee}</td>
                <td colspan="1"><strong>DOJ</strong></td>
                <td>:&nbsp;&nbsp;{doj}</td>
            </tr>

            <tr>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">S.No.</th>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">MONTH</th>
              <th rowspan ="2" style="text-align: center; border: 1px solid black;">APPLTN. DATE</th>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">APPRVL DATE</th>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">PERMISSION DATE</th>
              <th colspan="2" style="text-align: center; border: 1px solid black;">PERMISSION HOURS</th>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">TOTAL HOURS</th>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">ACCUMULATED HOURS</th>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">REASON FOR PERMISSION</th>
            </tr>
            <tr>
                <th style="text-align: center; border: 1px solid black;">FROM</th>
                <th style="text-align: center; border: 1px solid black;">TO</th>
            </tr>
                {rows}
        </table>
    </div>
    """
    return data



from datetime import date
from calendar import monthrange

@frappe.whitelist()
def get_month_start_and_end(year, month):
    # Convert year to integer
    year = int(year)
    
    # Convert month name to its corresponding integer
    month_map = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }
    month = month_map[month]

    start_date = date(year, month, 1)
    last_day = monthrange(year, month)[1]
    end_date = date(year, month, last_day)
    
    return start_date, end_date

# Copyright (c) 2025, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta, date, time

class AnnualReportDashboard(Document):
	pass

from datetime import datetime

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
                where docstatus != 2 and workflow_state != 'Rejected' and employee = %(employee)s
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
    <h2 class='text-center' style="color: black;">Form No: 15</h2>
    <h5 style="text-align: center;">(Prescribed under Rules 87 & 88 of Tamilnadu Factories Rules, 1950)</h5>
    <h3 style="text-align: center;">DWSI - LEAVE CARD FOR THE YEAR - {year}</h3>
    <div style="overflow-x: auto; color: black;">
            <table border="1" style="width: 100%; border-collapse: collapse; text-align: left;border: none;">
                <tr>
                    <td colspan="2" style ='border: none;'><strong>NAME</strong></td>
                    <td colspan="5" style ='border: none;'>:&nbsp;&nbsp;{emp_data['first_name']}</td>
                    <td colspan="2" style ='border: none;'><strong>DIVISION</strong></td>
                    <td colspan="1" style ='border: none;'>:&nbsp;&nbsp;{emp_data['employee_type']}</td>
                    <td colspan="3" style="border: 1px solid black;"><strong>Total Leave in {year}</strong></td>
                </tr>
                <tr>
                    <td colspan="2" style ='border: none;'><strong>DESIGNATION</strong></td>
                    <td colspan="5" style ='border: none;'>:&nbsp;&nbsp;{emp_data['designation']}</td>
                    <td colspan="2" style ='border: none;'><strong>DEPT</strong></td>
                    <td colspan="1" style ='border: none;'>:&nbsp;&nbsp;{emp_data['department']}</td>
                    <td style="border: 1px solid black;text-align: center;"><strong>CL</strong></td>
                    <td style="border: 1px solid black;text-align: center;"><strong>SL</strong></td>
                    <td style="border: 1px solid black;text-align: center;"><strong>EL</strong></td>
                </tr>
                <tr>
                    <td colspan="2" style ='border: none;'><strong>EMP NO</strong></td>
                    <td colspan="5" style ='border: none;'>:&nbsp;&nbsp;{employee}</td>
                    <td colspan="2" style ='border: none;'><strong>DOJ</strong></td>
                    <td colspan="1" style ='border: none;'>:&nbsp;&nbsp;{doj}</td>
                    <td style="border: 1px solid black;text-align: right;"><strong>{allocated_cl}</strong></td>
                    <td style="border: 1px solid black;text-align: right;"><strong>{allocated_sl}</strong></td>
                    <td style="border: 1px solid black;text-align: right;"><strong>{allocated_el}</strong></td>
                </tr>
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




@frappe.whitelist(allow_guest=True)
def get_permission_data(year,from_date, to_date, employee): 
    from_date_ = datetime.strptime(from_date, "%Y-%m-%d").strftime('%d-%m-%Y')
    to_date_ = datetime.strptime(to_date, "%Y-%m-%d").strftime('%d-%m-%Y')
    emp_data_list = frappe.db.get_all('Employee',{'name':employee},['first_name','date_of_joining','department','designation','employee_type'])
    emp_data = emp_data_list[0] 
    rows = ""
    count = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24']
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    m_index= -1
    index1 = -1
    index2 = 0
    for c in range(1, 25, (25 - 1) // 12):
        m_index+=1
        index1 += 2
        index2 += 2
        start_date, end_date = get_month_start_and_end(year, months[m_index])
        # frappe.errprint(f"{start_date}{end_date}")
        permission_data = frappe.db.sql("""
            select posting_date,permission_date,total_time,reason,permission_from_time,permission_to_time,modified,session,shift
            from `tabPermission`
            where docstatus != 2 and employee = %(employee)s
                and (permission_date between %(from_date)s and %(to_date)s)
                order by creation 
            """, {
                "from_date": start_date,
                "to_date": end_date,
                "employee":employee
            },
        as_dict = True)
        frappe.errprint(len(permission_data))
        if permission_data:
            first_permission = True
            total_perm_hours =0
            creation_date2 =''
            modified_date2 =''
            permission_date2 =''
            permission_from_time2 =''
            permission_to_time2 =''
            total_time2 = 0
            reason2 =''
            for perm in permission_data:
                frappe.errprint(perm)
                permission = perm
                if permission:
                    if first_permission:
                        first_permission = False
                        creation_date1 = permission['posting_date'].strftime('%d-%m-%Y') if permission['posting_date'] else ''
                        modified_date1 = permission['modified'].strftime('%d-%m-%Y') if permission['modified'] else ''
                        permission_date1 = permission['permission_date'].strftime('%d-%m-%Y') if permission['permission_date'] else ''
                        total_time1=permission['total_time'] if permission['total_time'] else 0.0
                        reason1 = permission['reason'] if permission['reason'] else ''
                        total_perm_hours += float(total_time1)
                        shift1 = permission['shift']
                        session1 = permission['session']
                        
                        frappe.errprint(shift1)
                        if shift1:
                            frappe.errprint(session1)
                            if session1 == 'First Half':
                                get_shift_time = frappe.db.get_value('Shift Type',{'name':shift1},['start_time'])
                                frappe.errprint(get_shift_time)
                                permission_from_time1 = get_shift_time
                                if total_time1 == 1:
                                    frappe.errprint(total_time1)
                                    permission_to_time1 = timedelta(hours=1) + get_shift_time
                                elif total_time1 == 2:
                                    permission_to_time1 = timedelta(hours=2) + get_shift_time
                                elif total_time1 == 3:
                                    permission_to_time1 = timedelta(hours=3) + get_shift_time
                                elif total_time1 == 4:
                                    permission_to_time1 = timedelta(hours=4) + get_shift_time
                            elif session1 == 'Second Half':
                                frappe.errprint('aaaa')
                                get_shift_end_time = frappe.db.get_value('Shift Type',{'name':shift1},['end_time'])
                                permission_to_time1 = get_shift_end_time
                                if total_time1 == 1:
                                    frappe.errprint(permission_from_time1)
                                    permission_from_time1 = get_shift_end_time - timedelta(hours=1)
                                    frappe.errprint(permission_from_time1)
                                elif total_time1 == 2:
                                    permission_from_time1 = get_shift_end_time - timedelta(hours=2)
                                elif total_time1 == 3:
                                    permission_from_time1 = get_shift_end_time - timedelta(hours=3)
                                elif total_time1 == 4:
                                    permission_from_time1 = get_shift_end_time - timedelta(hours=4)
                            else:
                                permission_from_time1 = permission['permission_from_time'] if permission['permission_from_time'] else ''
                                permission_to_time1 = permission['permission_to_time'] if permission['permission_to_time'] else ''

                    elif not first_permission:
                        creation_date2 = permission['posting_date'].strftime('%d-%m-%Y') if permission['posting_date'] else ''
                        modified_date2 = permission['modified'].strftime('%d-%m-%Y') if permission['modified'] else ''
                        permission_date2 = permission['permission_date'].strftime('%d-%m-%Y') if permission['permission_date'] else ''
                        permission_from_time2 = permission['permission_from_time'] if permission['permission_from_time'] else ''
                        permission_to_time2 = permission['permission_to_time'] if permission['permission_to_time'] else ''
                        total_time2 = permission['total_time'] if permission['total_time'] else 0.0
                        reason2 = permission['reason'] if permission['reason'] else ''
                        total_perm_hours += float(total_time2)
                        shift2 =permission['shift']
                        session2 = permission['session']
                        frappe.errprint(shift2)
                        if shift2:
                            frappe.errprint(session2)
                            if session2 == 'First Half':
                                get_shift_start_time2 = frappe.db.get_value('Shift Type',{'name':shift2},['start_time'])
                                permission_from_time2 = get_shift_start_time2
                                frappe.errprint(get_shift_start_time2)
                                if total_time2 == 1:
                                    frappe.errprint(total_time2)
                                    permission_to_time2 = timedelta(hours=1) + get_shift_start_time2
                                elif total_time2 == 2:
                                    permission_to_time2 = timedelta(hours=2) + get_shift_start_time2
                                elif total_time2 == 3:
                                    permission_to_time2 = timedelta(hours=3) + get_shift_start_time2
                                elif total_time2 == 4:
                                    permission_to_time2 = timedelta(hours=4) + get_shift_start_time2
                            elif session2 == 'Second Half':
                                frappe.errprint(session2)
                                frappe.errprint("total_time2")
                                get_shift_end_time2 = frappe.db.get_value('Shift Type',{'name':shift2},['end_time'])
                                permission_to_time2 = get_shift_end_time2
                                frappe.errprint(get_shift_end_time2)
                                frappe.errprint(total_time2)
                                if int(total_time2) == 1:
                                    frappe.errprint(get_shift_end_time2)
                                    permission_from_time2 = get_shift_end_time2 - timedelta(hours=1)
                                    frappe.errprint(get_shift_end_time2)
                                elif total_time2 == 2:
                                    permission_from_time2 = get_shift_end_time2 - timedelta(hours=2)
                                elif total_time2 == 3:
                                    permission_from_time2 = get_shift_end_time2 - timedelta(hours=3)
                                elif total_time2 == 4:
                                    permission_from_time2 = get_shift_end_time2 - timedelta(hours=4)
                            else:
                                permission_from_time2 = permission['permission_from_time'] if permission['permission_from_time'] else ''
                                permission_to_time2 = permission['permission_to_time'] if permission['permission_to_time'] else ''
            rows += f"""
                <tr>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{index1}</td>
                    <td rowspan="2" style="text-align: center; border: 1px solid black;">{months[m_index]}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{creation_date1}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{modified_date1}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{permission_date1}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{permission_from_time1}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{permission_to_time1}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{total_time1}</td>
                    <td rowspan="2" style="text-align: center; border: 1px solid black;">{total_perm_hours}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{reason1}</td>
                </tr>
                <tr>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{index2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{creation_date2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{modified_date2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{permission_date2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{permission_from_time2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{permission_to_time2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{total_time2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{reason2}</td>
                </tr>
                """        
        else:
            rows += f"""
                <tr>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{index1}</td>
                    <td rowspan="2" style="text-align: center; border: 1px solid black;">{months[m_index]}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td rowspan="2" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                </tr>
                <tr>
                    <td colspan="1" style="text-align: center;border: 1px solid black;">{index2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                </tr>
            """
        
    doj = emp_data['date_of_joining'].strftime('%d-%m-%Y')
    data = f"""
    <h3 style="text-align: center;">DWSI - PERMISSION CARD FOR THE YEAR - {year}</h3>
    <div style="overflow-x: auto; color: black;">

        <table border="0" style="width: 100%; border-collapse: collapse; text-align: left;border: none;">
            <tr>
                <td colspan="3"><strong>NAME</strong></td>
                <td colspan="4">:&nbsp;&nbsp;{emp_data['first_name']}</td>
                <td colspan="1"><strong>DIVISION</strong></td>
                <td>:&nbsp;&nbsp;{emp_data['employee_type']}</td>
            </tr>
            <tr>
                <td colspan="3"><strong>DESIGNATION</strong></td>
                <td colspan="4">:&nbsp;&nbsp;{emp_data['designation']}</td>
                <td colspan="1"><strong>DEPT</strong></td>
                <td>:&nbsp;&nbsp;{emp_data['department']}</td>
            </tr>
            <tr>
                <td colspan="3"><strong>EMP NO</strong></td>
                <td colspan="4">:&nbsp;&nbsp;{employee}</td>
                <td colspan="1"><strong>DOJ</strong></td>
                <td>:&nbsp;&nbsp;{doj}</td>
            </tr>

            <tr>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">S.No.</th>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">MONTH</th>
              <th rowspan ="2" style="text-align: center; border: 1px solid black;">APPLTN. DATE</th>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">APPRVL DATE</th>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">PERMISSION DATE</th>
              <th colspan="2" style="text-align: center; border: 1px solid black;">PERMISSION HOURS</th>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">TOTAL HOURS</th>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">ACCUMULATED HOURS</th>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">REASON FOR PERMISSION</th>
            </tr>
            <tr>
                <th style="text-align: center; border: 1px solid black;">FROM</th>
                <th style="text-align: center; border: 1px solid black;">TO</th>
            </tr>
                {rows}
        </table>
    </div>
    """
    return data



from datetime import date
from calendar import monthrange

@frappe.whitelist()
def get_month_start_and_end(year, month):
    # Convert year to integer
    year = int(year)
    
    # Convert month name to its corresponding integer
    month_map = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }
    month = month_map[month]

    start_date = date(year, month, 1)
    last_day = monthrange(year, month)[1]
    end_date = date(year, month, last_day)
    
    return start_date, end_date

# Copyright (c) 2025, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta, date, time

class AnnualReportDashboard(Document):
	pass

from datetime import datetime

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
                where docstatus != 2 and workflow_state != 'Rejected' and employee = %(employee)s
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
    <h2 class='text-center' style="color: black;">Form No: 15</h2>
    <h5 style="text-align: center;">(Prescribed under Rules 87 & 88 of Tamilnadu Factories Rules, 1950)</h5>
    <h3 style="text-align: center;">DWSI - LEAVE CARD FOR THE YEAR - {year}</h3>
    <div style="overflow-x: auto; color: black;">
            <table border="1" style="width: 100%; border-collapse: collapse; text-align: left;border: none;">
                <tr>
                    <td colspan="2" style ='border: none;'><strong>NAME</strong></td>
                    <td colspan="5" style ='border: none;'>:&nbsp;&nbsp;{emp_data['first_name']}</td>
                    <td colspan="2" style ='border: none;'><strong>DIVISION</strong></td>
                    <td colspan="1" style ='border: none;'>:&nbsp;&nbsp;{emp_data['employee_type']}</td>
                    <td colspan="3" style="border: 1px solid black;"><strong>Total Leave in {year}</strong></td>
                </tr>
                <tr>
                    <td colspan="2" style ='border: none;'><strong>DESIGNATION</strong></td>
                    <td colspan="5" style ='border: none;'>:&nbsp;&nbsp;{emp_data['designation']}</td>
                    <td colspan="2" style ='border: none;'><strong>DEPT</strong></td>
                    <td colspan="1" style ='border: none;'>:&nbsp;&nbsp;{emp_data['department']}</td>
                    <td style="border: 1px solid black;text-align: center;"><strong>CL</strong></td>
                    <td style="border: 1px solid black;text-align: center;"><strong>SL</strong></td>
                    <td style="border: 1px solid black;text-align: center;"><strong>EL</strong></td>
                </tr>
                <tr>
                    <td colspan="2" style ='border: none;'><strong>EMP NO</strong></td>
                    <td colspan="5" style ='border: none;'>:&nbsp;&nbsp;{employee}</td>
                    <td colspan="2" style ='border: none;'><strong>DOJ</strong></td>
                    <td colspan="1" style ='border: none;'>:&nbsp;&nbsp;{doj}</td>
                    <td style="border: 1px solid black;text-align: right;"><strong>{allocated_cl}</strong></td>
                    <td style="border: 1px solid black;text-align: right;"><strong>{allocated_sl}</strong></td>
                    <td style="border: 1px solid black;text-align: right;"><strong>{allocated_el}</strong></td>
                </tr>
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




@frappe.whitelist(allow_guest=True)
def get_permission_data(year,from_date, to_date, employee): 
    from_date_ = datetime.strptime(from_date, "%Y-%m-%d").strftime('%d-%m-%Y')
    to_date_ = datetime.strptime(to_date, "%Y-%m-%d").strftime('%d-%m-%Y')
    emp_data_list = frappe.db.get_all('Employee',{'name':employee},['first_name','date_of_joining','department','designation','employee_type'])
    emp_data = emp_data_list[0] 
    rows = ""
    count = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24']
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    m_index= -1
    index1 = -1
    index2 = 0
    for c in range(1, 25, (25 - 1) // 12):
        m_index+=1
        index1 += 2
        index2 += 2
        start_date, end_date = get_month_start_and_end(year, months[m_index])
        # frappe.errprint(f"{start_date}{end_date}")
        permission_data = frappe.db.sql("""
            select posting_date,permission_date,total_time,reason,permission_from_time,permission_to_time,modified,session,shift
            from `tabPermission`
            where docstatus != 2 and employee = %(employee)s
                and (permission_date between %(from_date)s and %(to_date)s)
                order by creation 
            """, {
                "from_date": start_date,
                "to_date": end_date,
                "employee":employee
            },
        as_dict = True)
        frappe.errprint(len(permission_data))
        if permission_data:
            first_permission = True
            total_perm_hours =0
            creation_date2 =''
            modified_date2 =''
            permission_date2 =''
            permission_from_time2 =''
            permission_to_time2 =''
            total_time2 = 0
            reason2 =''
            for perm in permission_data:
                frappe.errprint(perm)
                permission = perm
                if permission:
                    if first_permission:
                        first_permission = False
                        creation_date1 = permission['posting_date'].strftime('%d-%m-%Y') if permission['posting_date'] else ''
                        modified_date1 = permission['modified'].strftime('%d-%m-%Y') if permission['modified'] else ''
                        permission_date1 = permission['permission_date'].strftime('%d-%m-%Y') if permission['permission_date'] else ''
                        total_time1=permission['total_time'] if permission['total_time'] else 0.0
                        reason1 = permission['reason'] if permission['reason'] else ''
                        total_perm_hours += float(total_time1)
                        shift1 = permission['shift']
                        session1 = permission['session']
                        
                        frappe.errprint(shift1)
                        if shift1:
                            frappe.errprint(session1)
                            if session1 == 'First Half':
                                get_shift_time = frappe.db.get_value('Shift Type',{'name':shift1},['start_time'])
                                frappe.errprint(get_shift_time)
                                permission_from_time1 = get_shift_time
                                if total_time1 == 1:
                                    frappe.errprint(total_time1)
                                    permission_to_time1 = timedelta(hours=1) + get_shift_time
                                elif total_time1 == 2:
                                    permission_to_time1 = timedelta(hours=2) + get_shift_time
                                elif total_time1 == 3:
                                    permission_to_time1 = timedelta(hours=3) + get_shift_time
                                elif total_time1 == 4:
                                    permission_to_time1 = timedelta(hours=4) + get_shift_time
                            elif session1 == 'Second Half':
                                frappe.errprint('aaaa')
                                get_shift_end_time = frappe.db.get_value('Shift Type',{'name':shift1},['end_time'])
                                permission_to_time1 = get_shift_end_time
                                if total_time1 == 1:
                                    frappe.errprint(permission_from_time1)
                                    permission_from_time1 = get_shift_end_time - timedelta(hours=1)
                                    frappe.errprint(permission_from_time1)
                                elif total_time1 == 2:
                                    permission_from_time1 = get_shift_end_time - timedelta(hours=2)
                                elif total_time1 == 3:
                                    permission_from_time1 = get_shift_end_time - timedelta(hours=3)
                                elif total_time1 == 4:
                                    permission_from_time1 = get_shift_end_time - timedelta(hours=4)
                            else:
                                permission_from_time1 = permission['permission_from_time'] if permission['permission_from_time'] else ''
                                permission_to_time1 = permission['permission_to_time'] if permission['permission_to_time'] else ''

                    elif not first_permission:
                        creation_date2 = permission['posting_date'].strftime('%d-%m-%Y') if permission['posting_date'] else ''
                        modified_date2 = permission['modified'].strftime('%d-%m-%Y') if permission['modified'] else ''
                        permission_date2 = permission['permission_date'].strftime('%d-%m-%Y') if permission['permission_date'] else ''
                        permission_from_time2 = permission['permission_from_time'] if permission['permission_from_time'] else ''
                        permission_to_time2 = permission['permission_to_time'] if permission['permission_to_time'] else ''
                        total_time2 = permission['total_time'] if permission['total_time'] else 0.0
                        reason2 = permission['reason'] if permission['reason'] else ''
                        total_perm_hours += float(total_time2)
                        shift2 =permission['shift']
                        session2 = permission['session']
                        frappe.errprint(shift2)
                        if shift2:
                            frappe.errprint(session2)
                            if session2 == 'First Half':
                                get_shift_start_time2 = frappe.db.get_value('Shift Type',{'name':shift2},['start_time'])
                                permission_from_time2 = get_shift_start_time2
                                frappe.errprint(get_shift_start_time2)
                                if total_time2 == 1:
                                    frappe.errprint(total_time2)
                                    permission_to_time2 = timedelta(hours=1) + get_shift_start_time2
                                elif total_time2 == 2:
                                    permission_to_time2 = timedelta(hours=2) + get_shift_start_time2
                                elif total_time2 == 3:
                                    permission_to_time2 = timedelta(hours=3) + get_shift_start_time2
                                elif total_time2 == 4:
                                    permission_to_time2 = timedelta(hours=4) + get_shift_start_time2
                            elif session2 == 'Second Half':
                                frappe.errprint(session2)
                                frappe.errprint("total_time2")
                                get_shift_end_time2 = frappe.db.get_value('Shift Type',{'name':shift2},['end_time'])
                                permission_to_time2 = get_shift_end_time2
                                frappe.errprint(get_shift_end_time2)
                                frappe.errprint(total_time2)
                                if int(total_time2) == 1:
                                    frappe.errprint(get_shift_end_time2)
                                    permission_from_time2 = get_shift_end_time2 - timedelta(hours=1)
                                    frappe.errprint(get_shift_end_time2)
                                elif total_time2 == 2:
                                    permission_from_time2 = get_shift_end_time2 - timedelta(hours=2)
                                elif total_time2 == 3:
                                    permission_from_time2 = get_shift_end_time2 - timedelta(hours=3)
                                elif total_time2 == 4:
                                    permission_from_time2 = get_shift_end_time2 - timedelta(hours=4)
                            else:
                                permission_from_time2 = permission['permission_from_time'] if permission['permission_from_time'] else ''
                                permission_to_time2 = permission['permission_to_time'] if permission['permission_to_time'] else ''
            rows += f"""
                <tr>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{index1}</td>
                    <td rowspan="2" style="text-align: center; border: 1px solid black;">{months[m_index]}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{creation_date1}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{modified_date1}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{permission_date1}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{permission_from_time1}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{permission_to_time1}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{total_time1}</td>
                    <td rowspan="2" style="text-align: center; border: 1px solid black;">{total_perm_hours}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{reason1}</td>
                </tr>
                <tr>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{index2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{creation_date2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{modified_date2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{permission_date2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{permission_from_time2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{permission_to_time2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{total_time2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{reason2}</td>
                </tr>
                """        
        else:
            rows += f"""
                <tr>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{index1}</td>
                    <td rowspan="2" style="text-align: center; border: 1px solid black;">{months[m_index]}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td rowspan="2" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                </tr>
                <tr>
                    <td colspan="1" style="text-align: center;border: 1px solid black;">{index2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                </tr>
            """
        
    doj = emp_data['date_of_joining'].strftime('%d-%m-%Y')
    data = f"""
    <h3 style="text-align: center;">DWSI - PERMISSION CARD FOR THE YEAR - {year}</h3>
    <div style="overflow-x: auto; color: black;">

        <table border="0" style="width: 100%; border-collapse: collapse; text-align: left;border: none;">
            <tr>
                <td colspan="3"><strong>NAME</strong></td>
                <td colspan="4">:&nbsp;&nbsp;{emp_data['first_name']}</td>
                <td colspan="1"><strong>DIVISION</strong></td>
                <td>:&nbsp;&nbsp;{emp_data['employee_type']}</td>
            </tr>
            <tr>
                <td colspan="3"><strong>DESIGNATION</strong></td>
                <td colspan="4">:&nbsp;&nbsp;{emp_data['designation']}</td>
                <td colspan="1"><strong>DEPT</strong></td>
                <td>:&nbsp;&nbsp;{emp_data['department']}</td>
            </tr>
            <tr>
                <td colspan="3"><strong>EMP NO</strong></td>
                <td colspan="4">:&nbsp;&nbsp;{employee}</td>
                <td colspan="1"><strong>DOJ</strong></td>
                <td>:&nbsp;&nbsp;{doj}</td>
            </tr>

            <tr>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">S.No.</th>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">MONTH</th>
              <th rowspan ="2" style="text-align: center; border: 1px solid black;">APPLTN. DATE</th>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">APPRVL DATE</th>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">PERMISSION DATE</th>
              <th colspan="2" style="text-align: center; border: 1px solid black;">PERMISSION HOURS</th>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">TOTAL HOURS</th>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">ACCUMULATED HOURS</th>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">REASON FOR PERMISSION</th>
            </tr>
            <tr>
                <th style="text-align: center; border: 1px solid black;">FROM</th>
                <th style="text-align: center; border: 1px solid black;">TO</th>
            </tr>
                {rows}
        </table>
    </div>
    """
    return data



from datetime import date
from calendar import monthrange

@frappe.whitelist()
def get_month_start_and_end(year, month):
    # Convert year to integer
    year = int(year)
    
    # Convert month name to its corresponding integer
    month_map = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }
    month = month_map[month]

    start_date = date(year, month, 1)
    last_day = monthrange(year, month)[1]
    end_date = date(year, month, last_day)
    
    return start_date, end_date

# Copyright (c) 2025, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta, date, time

class AnnualReportDashboard(Document):
	pass

from datetime import datetime

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
                where docstatus != 2 and workflow_state != 'Rejected' and employee = %(employee)s
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
    <h2 class='text-center' style="color: black;">Form No: 15</h2>
    <h5 style="text-align: center;">(Prescribed under Rules 87 & 88 of Tamilnadu Factories Rules, 1950)</h5>
    <h3 style="text-align: center;">DWSI - LEAVE CARD FOR THE YEAR - {year}</h3>
    <div style="overflow-x: auto; color: black;">
            <table border="1" style="width: 100%; border-collapse: collapse; text-align: left;border: none;">
                <tr>
                    <td colspan="2" style ='border: none;'><strong>NAME</strong></td>
                    <td colspan="5" style ='border: none;'>:&nbsp;&nbsp;{emp_data['first_name']}</td>
                    <td colspan="2" style ='border: none;'><strong>DIVISION</strong></td>
                    <td colspan="1" style ='border: none;'>:&nbsp;&nbsp;{emp_data['employee_type']}</td>
                    <td colspan="3" style="border: 1px solid black;"><strong>Total Leave in {year}</strong></td>
                </tr>
                <tr>
                    <td colspan="2" style ='border: none;'><strong>DESIGNATION</strong></td>
                    <td colspan="5" style ='border: none;'>:&nbsp;&nbsp;{emp_data['designation']}</td>
                    <td colspan="2" style ='border: none;'><strong>DEPT</strong></td>
                    <td colspan="1" style ='border: none;'>:&nbsp;&nbsp;{emp_data['department']}</td>
                    <td style="border: 1px solid black;text-align: center;"><strong>CL</strong></td>
                    <td style="border: 1px solid black;text-align: center;"><strong>SL</strong></td>
                    <td style="border: 1px solid black;text-align: center;"><strong>EL</strong></td>
                </tr>
                <tr>
                    <td colspan="2" style ='border: none;'><strong>EMP NO</strong></td>
                    <td colspan="5" style ='border: none;'>:&nbsp;&nbsp;{employee}</td>
                    <td colspan="2" style ='border: none;'><strong>DOJ</strong></td>
                    <td colspan="1" style ='border: none;'>:&nbsp;&nbsp;{doj}</td>
                    <td style="border: 1px solid black;text-align: right;"><strong>{allocated_cl}</strong></td>
                    <td style="border: 1px solid black;text-align: right;"><strong>{allocated_sl}</strong></td>
                    <td style="border: 1px solid black;text-align: right;"><strong>{allocated_el}</strong></td>
                </tr>
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




@frappe.whitelist(allow_guest=True)
def get_permission_data(year,from_date, to_date, employee): 
    from_date_ = datetime.strptime(from_date, "%Y-%m-%d").strftime('%d-%m-%Y')
    to_date_ = datetime.strptime(to_date, "%Y-%m-%d").strftime('%d-%m-%Y')
    emp_data_list = frappe.db.get_all('Employee',{'name':employee},['first_name','date_of_joining','department','designation','employee_type'])
    emp_data = emp_data_list[0] 
    rows = ""
    count = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24']
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    m_index= -1
    index1 = -1
    index2 = 0
    for c in range(1, 25, (25 - 1) // 12):
        m_index+=1
        index1 += 2
        index2 += 2
        start_date, end_date = get_month_start_and_end(year, months[m_index])
        # frappe.errprint(f"{start_date}{end_date}")
        permission_data = frappe.db.sql("""
            select posting_date,permission_date,total_time,reason,permission_from_time,permission_to_time,modified,session,shift
            from `tabPermission`
            where docstatus != 2 and employee = %(employee)s
                and (permission_date between %(from_date)s and %(to_date)s)
                order by creation 
            """, {
                "from_date": start_date,
                "to_date": end_date,
                "employee":employee
            },
        as_dict = True)
        frappe.errprint(len(permission_data))
        if permission_data:
            first_permission = True
            total_perm_hours =0
            creation_date2 =''
            modified_date2 =''
            permission_date2 =''
            permission_from_time2 =''
            permission_to_time2 =''
            total_time2 = 0
            reason2 =''
            for perm in permission_data:
                frappe.errprint(perm)
                permission = perm
                if permission:
                    if first_permission:
                        first_permission = False
                        creation_date1 = permission['posting_date'].strftime('%d-%m-%Y') if permission['posting_date'] else ''
                        modified_date1 = permission['modified'].strftime('%d-%m-%Y') if permission['modified'] else ''
                        permission_date1 = permission['permission_date'].strftime('%d-%m-%Y') if permission['permission_date'] else ''
                        total_time1=permission['total_time'] if permission['total_time'] else 0.0
                        reason1 = permission['reason'] if permission['reason'] else ''
                        total_perm_hours += float(total_time1)
                        shift1 = permission['shift']
                        session1 = permission['session']
                        
                        frappe.errprint(shift1)
                        if shift1:
                            frappe.errprint(session1)
                            if session1 == 'First Half':
                                get_shift_time = frappe.db.get_value('Shift Type',{'name':shift1},['start_time'])
                                frappe.errprint(get_shift_time)
                                permission_from_time1 = get_shift_time
                                if total_time1 == 1:
                                    frappe.errprint(total_time1)
                                    permission_to_time1 = timedelta(hours=1) + get_shift_time
                                elif total_time1 == 2:
                                    permission_to_time1 = timedelta(hours=2) + get_shift_time
                                elif total_time1 == 3:
                                    permission_to_time1 = timedelta(hours=3) + get_shift_time
                                elif total_time1 == 4:
                                    permission_to_time1 = timedelta(hours=4) + get_shift_time
                            elif session1 == 'Second Half':
                                frappe.errprint('aaaa')
                                get_shift_end_time = frappe.db.get_value('Shift Type',{'name':shift1},['end_time'])
                                permission_to_time1 = get_shift_end_time
                                if total_time1 == 1:
                                    frappe.errprint(permission_from_time1)
                                    permission_from_time1 = get_shift_end_time - timedelta(hours=1)
                                    frappe.errprint(permission_from_time1)
                                elif total_time1 == 2:
                                    permission_from_time1 = get_shift_end_time - timedelta(hours=2)
                                elif total_time1 == 3:
                                    permission_from_time1 = get_shift_end_time - timedelta(hours=3)
                                elif total_time1 == 4:
                                    permission_from_time1 = get_shift_end_time - timedelta(hours=4)
                            else:
                                permission_from_time1 = permission['permission_from_time'] if permission['permission_from_time'] else ''
                                permission_to_time1 = permission['permission_to_time'] if permission['permission_to_time'] else ''

                    elif not first_permission:
                        creation_date2 = permission['posting_date'].strftime('%d-%m-%Y') if permission['posting_date'] else ''
                        modified_date2 = permission['modified'].strftime('%d-%m-%Y') if permission['modified'] else ''
                        permission_date2 = permission['permission_date'].strftime('%d-%m-%Y') if permission['permission_date'] else ''
                        permission_from_time2 = permission['permission_from_time'] if permission['permission_from_time'] else ''
                        permission_to_time2 = permission['permission_to_time'] if permission['permission_to_time'] else ''
                        total_time2 = permission['total_time'] if permission['total_time'] else 0.0
                        reason2 = permission['reason'] if permission['reason'] else ''
                        total_perm_hours += float(total_time2)
                        shift2 =permission['shift']
                        session2 = permission['session']
                        frappe.errprint(shift2)
                        if shift2:
                            frappe.errprint(session2)
                            if session2 == 'First Half':
                                get_shift_start_time2 = frappe.db.get_value('Shift Type',{'name':shift2},['start_time'])
                                permission_from_time2 = get_shift_start_time2
                                frappe.errprint(get_shift_start_time2)
                                if total_time2 == 1:
                                    frappe.errprint(total_time2)
                                    permission_to_time2 = timedelta(hours=1) + get_shift_start_time2
                                elif total_time2 == 2:
                                    permission_to_time2 = timedelta(hours=2) + get_shift_start_time2
                                elif total_time2 == 3:
                                    permission_to_time2 = timedelta(hours=3) + get_shift_start_time2
                                elif total_time2 == 4:
                                    permission_to_time2 = timedelta(hours=4) + get_shift_start_time2
                            elif session2 == 'Second Half':
                                frappe.errprint(session2)
                                frappe.errprint("total_time2")
                                get_shift_end_time2 = frappe.db.get_value('Shift Type',{'name':shift2},['end_time'])
                                permission_to_time2 = get_shift_end_time2
                                frappe.errprint(get_shift_end_time2)
                                frappe.errprint(total_time2)
                                if int(total_time2) == 1:
                                    frappe.errprint(get_shift_end_time2)
                                    permission_from_time2 = get_shift_end_time2 - timedelta(hours=1)
                                    frappe.errprint(get_shift_end_time2)
                                elif total_time2 == 2:
                                    permission_from_time2 = get_shift_end_time2 - timedelta(hours=2)
                                elif total_time2 == 3:
                                    permission_from_time2 = get_shift_end_time2 - timedelta(hours=3)
                                elif total_time2 == 4:
                                    permission_from_time2 = get_shift_end_time2 - timedelta(hours=4)
                            else:
                                permission_from_time2 = permission['permission_from_time'] if permission['permission_from_time'] else ''
                                permission_to_time2 = permission['permission_to_time'] if permission['permission_to_time'] else ''
            rows += f"""
                <tr>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{index1}</td>
                    <td rowspan="2" style="text-align: center; border: 1px solid black;">{months[m_index]}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{creation_date1}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{modified_date1}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{permission_date1}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{permission_from_time1}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{permission_to_time1}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{total_time1}</td>
                    <td rowspan="2" style="text-align: center; border: 1px solid black;">{total_perm_hours}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{reason1}</td>
                </tr>
                <tr>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{index2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{creation_date2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{modified_date2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{permission_date2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{permission_from_time2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{permission_to_time2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{total_time2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{reason2}</td>
                </tr>
                """        
        else:
            rows += f"""
                <tr>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{index1}</td>
                    <td rowspan="2" style="text-align: center; border: 1px solid black;">{months[m_index]}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td rowspan="2" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                </tr>
                <tr>
                    <td colspan="1" style="text-align: center;border: 1px solid black;">{index2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                </tr>
            """
        
    doj = emp_data['date_of_joining'].strftime('%d-%m-%Y')
    data = f"""
    <h3 style="text-align: center;">DWSI - PERMISSION CARD FOR THE YEAR - {year}</h3>
    <div style="overflow-x: auto; color: black;">

        <table border="0" style="width: 100%; border-collapse: collapse; text-align: left;border: none;">
            <tr>
                <td colspan="3"><strong>NAME</strong></td>
                <td colspan="4">:&nbsp;&nbsp;{emp_data['first_name']}</td>
                <td colspan="1"><strong>DIVISION</strong></td>
                <td>:&nbsp;&nbsp;{emp_data['employee_type']}</td>
            </tr>
            <tr>
                <td colspan="3"><strong>DESIGNATION</strong></td>
                <td colspan="4">:&nbsp;&nbsp;{emp_data['designation']}</td>
                <td colspan="1"><strong>DEPT</strong></td>
                <td>:&nbsp;&nbsp;{emp_data['department']}</td>
            </tr>
            <tr>
                <td colspan="3"><strong>EMP NO</strong></td>
                <td colspan="4">:&nbsp;&nbsp;{employee}</td>
                <td colspan="1"><strong>DOJ</strong></td>
                <td>:&nbsp;&nbsp;{doj}</td>
            </tr>

            <tr>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">S.No.</th>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">MONTH</th>
              <th rowspan ="2" style="text-align: center; border: 1px solid black;">APPLTN. DATE</th>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">APPRVL DATE</th>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">PERMISSION DATE</th>
              <th colspan="2" style="text-align: center; border: 1px solid black;">PERMISSION HOURS</th>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">TOTAL HOURS</th>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">ACCUMULATED HOURS</th>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">REASON FOR PERMISSION</th>
            </tr>
            <tr>
                <th style="text-align: center; border: 1px solid black;">FROM</th>
                <th style="text-align: center; border: 1px solid black;">TO</th>
            </tr>
                {rows}
        </table>
    </div>
    """
    return data



from datetime import date
from calendar import monthrange

@frappe.whitelist()
def get_month_start_and_end(year, month):
    # Convert year to integer
    year = int(year)
    
    # Convert month name to its corresponding integer
    month_map = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }
    month = month_map[month]

    start_date = date(year, month, 1)
    last_day = monthrange(year, month)[1]
    end_date = date(year, month, last_day)
    
    return start_date, end_date

# Copyright (c) 2025, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta, date, time

class AnnualReportDashboard(Document):
	pass

from datetime import datetime

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
                where docstatus != 2 and workflow_state != 'Rejected' and employee = %(employee)s
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
    <h2 class='text-center' style="color: black;">Form No: 15</h2>
    <h5 style="text-align: center;">(Prescribed under Rules 87 & 88 of Tamilnadu Factories Rules, 1950)</h5>
    <h3 style="text-align: center;">DWSI - LEAVE CARD FOR THE YEAR - {year}</h3>
    <div style="overflow-x: auto; color: black;">
            <table border="1" style="width: 100%; border-collapse: collapse; text-align: left;border: none;">
                <tr>
                    <td colspan="2" style ='border: none;'><strong>NAME</strong></td>
                    <td colspan="5" style ='border: none;'>:&nbsp;&nbsp;{emp_data['first_name']}</td>
                    <td colspan="2" style ='border: none;'><strong>DIVISION</strong></td>
                    <td colspan="1" style ='border: none;'>:&nbsp;&nbsp;{emp_data['employee_type']}</td>
                    <td colspan="3" style="border: 1px solid black;"><strong>Total Leave in {year}</strong></td>
                </tr>
                <tr>
                    <td colspan="2" style ='border: none;'><strong>DESIGNATION</strong></td>
                    <td colspan="5" style ='border: none;'>:&nbsp;&nbsp;{emp_data['designation']}</td>
                    <td colspan="2" style ='border: none;'><strong>DEPT</strong></td>
                    <td colspan="1" style ='border: none;'>:&nbsp;&nbsp;{emp_data['department']}</td>
                    <td style="border: 1px solid black;text-align: center;"><strong>CL</strong></td>
                    <td style="border: 1px solid black;text-align: center;"><strong>SL</strong></td>
                    <td style="border: 1px solid black;text-align: center;"><strong>EL</strong></td>
                </tr>
                <tr>
                    <td colspan="2" style ='border: none;'><strong>EMP NO</strong></td>
                    <td colspan="5" style ='border: none;'>:&nbsp;&nbsp;{employee}</td>
                    <td colspan="2" style ='border: none;'><strong>DOJ</strong></td>
                    <td colspan="1" style ='border: none;'>:&nbsp;&nbsp;{doj}</td>
                    <td style="border: 1px solid black;text-align: right;"><strong>{allocated_cl}</strong></td>
                    <td style="border: 1px solid black;text-align: right;"><strong>{allocated_sl}</strong></td>
                    <td style="border: 1px solid black;text-align: right;"><strong>{allocated_el}</strong></td>
                </tr>
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




@frappe.whitelist(allow_guest=True)
def get_permission_data(year,from_date, to_date, employee): 
    from_date_ = datetime.strptime(from_date, "%Y-%m-%d").strftime('%d-%m-%Y')
    to_date_ = datetime.strptime(to_date, "%Y-%m-%d").strftime('%d-%m-%Y')
    emp_data_list = frappe.db.get_all('Employee',{'name':employee},['first_name','date_of_joining','department','designation','employee_type'])
    emp_data = emp_data_list[0] 
    rows = ""
    count = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24']
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    m_index= -1
    index1 = -1
    index2 = 0
    for c in range(1, 25, (25 - 1) // 12):
        m_index+=1
        index1 += 2
        index2 += 2
        start_date, end_date = get_month_start_and_end(year, months[m_index])
        # frappe.errprint(f"{start_date}{end_date}")
        permission_data = frappe.db.sql("""
            select posting_date,permission_date,total_time,reason,permission_from_time,permission_to_time,modified,session,shift
            from `tabPermission`
            where docstatus != 2 and employee = %(employee)s
                and (permission_date between %(from_date)s and %(to_date)s)
                order by creation 
            """, {
                "from_date": start_date,
                "to_date": end_date,
                "employee":employee
            },
        as_dict = True)
        frappe.errprint(len(permission_data))
        if permission_data:
            first_permission = True
            total_perm_hours =0
            creation_date2 =''
            modified_date2 =''
            permission_date2 =''
            permission_from_time2 =''
            permission_to_time2 =''
            total_time2 = 0
            reason2 =''
            for perm in permission_data:
                frappe.errprint(perm)
                permission = perm
                if permission:
                    if first_permission:
                        first_permission = False
                        creation_date1 = permission['posting_date'].strftime('%d-%m-%Y') if permission['posting_date'] else ''
                        modified_date1 = permission['modified'].strftime('%d-%m-%Y') if permission['modified'] else ''
                        permission_date1 = permission['permission_date'].strftime('%d-%m-%Y') if permission['permission_date'] else ''
                        total_time1=permission['total_time'] if permission['total_time'] else 0.0
                        reason1 = permission['reason'] if permission['reason'] else ''
                        total_perm_hours += float(total_time1)
                        shift1 = permission['shift']
                        session1 = permission['session']
                        
                        frappe.errprint(shift1)
                        if shift1:
                            frappe.errprint(session1)
                            if session1 == 'First Half':
                                get_shift_time = frappe.db.get_value('Shift Type',{'name':shift1},['start_time'])
                                frappe.errprint(get_shift_time)
                                permission_from_time1 = get_shift_time
                                if total_time1 == 1:
                                    frappe.errprint(total_time1)
                                    permission_to_time1 = timedelta(hours=1) + get_shift_time
                                elif total_time1 == 2:
                                    permission_to_time1 = timedelta(hours=2) + get_shift_time
                                elif total_time1 == 3:
                                    permission_to_time1 = timedelta(hours=3) + get_shift_time
                                elif total_time1 == 4:
                                    permission_to_time1 = timedelta(hours=4) + get_shift_time
                            elif session1 == 'Second Half':
                                frappe.errprint('aaaa')
                                get_shift_end_time = frappe.db.get_value('Shift Type',{'name':shift1},['end_time'])
                                permission_to_time1 = get_shift_end_time
                                if total_time1 == 1:
                                    frappe.errprint(permission_from_time1)
                                    permission_from_time1 = get_shift_end_time - timedelta(hours=1)
                                    frappe.errprint(permission_from_time1)
                                elif total_time1 == 2:
                                    permission_from_time1 = get_shift_end_time - timedelta(hours=2)
                                elif total_time1 == 3:
                                    permission_from_time1 = get_shift_end_time - timedelta(hours=3)
                                elif total_time1 == 4:
                                    permission_from_time1 = get_shift_end_time - timedelta(hours=4)
                            else:
                                permission_from_time1 = permission['permission_from_time'] if permission['permission_from_time'] else ''
                                permission_to_time1 = permission['permission_to_time'] if permission['permission_to_time'] else ''

                    elif not first_permission:
                        creation_date2 = permission['posting_date'].strftime('%d-%m-%Y') if permission['posting_date'] else ''
                        modified_date2 = permission['modified'].strftime('%d-%m-%Y') if permission['modified'] else ''
                        permission_date2 = permission['permission_date'].strftime('%d-%m-%Y') if permission['permission_date'] else ''
                        permission_from_time2 = permission['permission_from_time'] if permission['permission_from_time'] else ''
                        permission_to_time2 = permission['permission_to_time'] if permission['permission_to_time'] else ''
                        total_time2 = permission['total_time'] if permission['total_time'] else 0.0
                        reason2 = permission['reason'] if permission['reason'] else ''
                        total_perm_hours += float(total_time2)
                        shift2 =permission['shift']
                        session2 = permission['session']
                        frappe.errprint(shift2)
                        if shift2:
                            frappe.errprint(session2)
                            if session2 == 'First Half':
                                get_shift_start_time2 = frappe.db.get_value('Shift Type',{'name':shift2},['start_time'])
                                permission_from_time2 = get_shift_start_time2
                                frappe.errprint(get_shift_start_time2)
                                if total_time2 == 1:
                                    frappe.errprint(total_time2)
                                    permission_to_time2 = timedelta(hours=1) + get_shift_start_time2
                                elif total_time2 == 2:
                                    permission_to_time2 = timedelta(hours=2) + get_shift_start_time2
                                elif total_time2 == 3:
                                    permission_to_time2 = timedelta(hours=3) + get_shift_start_time2
                                elif total_time2 == 4:
                                    permission_to_time2 = timedelta(hours=4) + get_shift_start_time2
                            elif session2 == 'Second Half':
                                frappe.errprint(session2)
                                frappe.errprint("total_time2")
                                get_shift_end_time2 = frappe.db.get_value('Shift Type',{'name':shift2},['end_time'])
                                permission_to_time2 = get_shift_end_time2
                                frappe.errprint(get_shift_end_time2)
                                frappe.errprint(total_time2)
                                if int(total_time2) == 1:
                                    frappe.errprint(get_shift_end_time2)
                                    permission_from_time2 = get_shift_end_time2 - timedelta(hours=1)
                                    frappe.errprint(get_shift_end_time2)
                                elif total_time2 == 2:
                                    permission_from_time2 = get_shift_end_time2 - timedelta(hours=2)
                                elif total_time2 == 3:
                                    permission_from_time2 = get_shift_end_time2 - timedelta(hours=3)
                                elif total_time2 == 4:
                                    permission_from_time2 = get_shift_end_time2 - timedelta(hours=4)
                            else:
                                permission_from_time2 = permission['permission_from_time'] if permission['permission_from_time'] else ''
                                permission_to_time2 = permission['permission_to_time'] if permission['permission_to_time'] else ''
            rows += f"""
                <tr>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{index1}</td>
                    <td rowspan="2" style="text-align: center; border: 1px solid black;">{months[m_index]}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{creation_date1}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{modified_date1}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{permission_date1}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{permission_from_time1}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{permission_to_time1}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{total_time1}</td>
                    <td rowspan="2" style="text-align: center; border: 1px solid black;">{total_perm_hours}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{reason1}</td>
                </tr>
                <tr>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{index2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{creation_date2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{modified_date2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{permission_date2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{permission_from_time2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{permission_to_time2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{total_time2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{reason2}</td>
                </tr>
                """        
        else:
            rows += f"""
                <tr>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{index1}</td>
                    <td rowspan="2" style="text-align: center; border: 1px solid black;">{months[m_index]}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td rowspan="2" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                </tr>
                <tr>
                    <td colspan="1" style="text-align: center;border: 1px solid black;">{index2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                </tr>
            """
        
    doj = emp_data['date_of_joining'].strftime('%d-%m-%Y')
    data = f"""
    <h3 style="text-align: center;">DWSI - PERMISSION CARD FOR THE YEAR - {year}</h3>
    <div style="overflow-x: auto; color: black;">

        <table border="0" style="width: 100%; border-collapse: collapse; text-align: left;border: none;">
            <tr>
                <td colspan="3"><strong>NAME</strong></td>
                <td colspan="4">:&nbsp;&nbsp;{emp_data['first_name']}</td>
                <td colspan="1"><strong>DIVISION</strong></td>
                <td>:&nbsp;&nbsp;{emp_data['employee_type']}</td>
            </tr>
            <tr>
                <td colspan="3"><strong>DESIGNATION</strong></td>
                <td colspan="4">:&nbsp;&nbsp;{emp_data['designation']}</td>
                <td colspan="1"><strong>DEPT</strong></td>
                <td>:&nbsp;&nbsp;{emp_data['department']}</td>
            </tr>
            <tr>
                <td colspan="3"><strong>EMP NO</strong></td>
                <td colspan="4">:&nbsp;&nbsp;{employee}</td>
                <td colspan="1"><strong>DOJ</strong></td>
                <td>:&nbsp;&nbsp;{doj}</td>
            </tr>

            <tr>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">S.No.</th>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">MONTH</th>
              <th rowspan ="2" style="text-align: center; border: 1px solid black;">APPLTN. DATE</th>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">APPRVL DATE</th>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">PERMISSION DATE</th>
              <th colspan="2" style="text-align: center; border: 1px solid black;">PERMISSION HOURS</th>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">TOTAL HOURS</th>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">ACCUMULATED HOURS</th>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">REASON FOR PERMISSION</th>
            </tr>
            <tr>
                <th style="text-align: center; border: 1px solid black;">FROM</th>
                <th style="text-align: center; border: 1px solid black;">TO</th>
            </tr>
                {rows}
        </table>
    </div>
    """
    return data



from datetime import date
from calendar import monthrange

@frappe.whitelist()
def get_month_start_and_end(year, month):
    # Convert year to integer
    year = int(year)
    
    # Convert month name to its corresponding integer
    month_map = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }
    month = month_map[month]

    start_date = date(year, month, 1)
    last_day = monthrange(year, month)[1]
    end_date = date(year, month, last_day)
    
    return start_date, end_date

# Copyright (c) 2025, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta, date, time

class AnnualReportDashboard(Document):
	pass

from datetime import datetime

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
    <h2 class='text-center' style="color: black;">Form No: 15</h2>
    <h5 style="text-align: center;">(Prescribed under Rules 87 & 88 of Tamilnadu Factories Rules, 1950)</h5>
    <h3 style="text-align: center;">DWSI - LEAVE CARD FOR THE YEAR - {year}</h3>
    <div style="overflow-x: auto; color: black;">
            <table border="1" style="width: 100%; border-collapse: collapse; text-align: left;border: none;">
                <tr>
                    <td colspan="2" style ='border: none;'><strong>NAME</strong></td>
                    <td colspan="5" style ='border: none;'>:&nbsp;&nbsp;{emp_data['first_name']}</td>
                    <td colspan="2" style ='border: none;'><strong>DIVISION</strong></td>
                    <td colspan="1" style ='border: none;'>:&nbsp;&nbsp;{emp_data['employee_type']}</td>
                    <td colspan="3" style="border: 1px solid black;"><strong>Total Leave in {year}</strong></td>
                </tr>
                <tr>
                    <td colspan="2" style ='border: none;'><strong>DESIGNATION</strong></td>
                    <td colspan="5" style ='border: none;'>:&nbsp;&nbsp;{emp_data['designation']}</td>
                    <td colspan="2" style ='border: none;'><strong>DEPT</strong></td>
                    <td colspan="1" style ='border: none;'>:&nbsp;&nbsp;{emp_data['department']}</td>
                    <td style="border: 1px solid black;text-align: center;"><strong>CL</strong></td>
                    <td style="border: 1px solid black;text-align: center;"><strong>SL</strong></td>
                    <td style="border: 1px solid black;text-align: center;"><strong>EL</strong></td>
                </tr>
                <tr>
                    <td colspan="2" style ='border: none;'><strong>EMP NO</strong></td>
                    <td colspan="5" style ='border: none;'>:&nbsp;&nbsp;{employee}</td>
                    <td colspan="2" style ='border: none;'><strong>DOJ</strong></td>
                    <td colspan="1" style ='border: none;'>:&nbsp;&nbsp;{doj}</td>
                    <td style="border: 1px solid black;text-align: right;"><strong>{allocated_cl}</strong></td>
                    <td style="border: 1px solid black;text-align: right;"><strong>{allocated_sl}</strong></td>
                    <td style="border: 1px solid black;text-align: right;"><strong>{allocated_el}</strong></td>
                </tr>
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




@frappe.whitelist(allow_guest=True)
def get_permission_data(year,from_date, to_date, employee): 
    from_date_ = datetime.strptime(from_date, "%Y-%m-%d").strftime('%d-%m-%Y')
    to_date_ = datetime.strptime(to_date, "%Y-%m-%d").strftime('%d-%m-%Y')
    emp_data_list = frappe.db.get_all('Employee',{'name':employee},['first_name','date_of_joining','department','designation','employee_type'])
    emp_data = emp_data_list[0] 
    rows = ""
    count = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24']
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    m_index= -1
    index1 = -1
    index2 = 0
    for c in range(1, 25, (25 - 1) // 12):
        m_index+=1
        index1 += 2
        index2 += 2
        start_date, end_date = get_month_start_and_end(year, months[m_index])
        # frappe.errprint(f"{start_date}{end_date}")
        permission_data = frappe.db.sql("""
            select posting_date,permission_date,total_time,reason,permission_from_time,permission_to_time,modified,session,shift
            from `tabPermission`
            where docstatus = 1 and employee = %(employee)s
                and (permission_date between %(from_date)s and %(to_date)s)
                order by creation 
            """, {
                "from_date": start_date,
                "to_date": end_date,
                "employee":employee
            },
        as_dict = True)
        frappe.errprint(len(permission_data))
        if permission_data:
            first_permission = True
            total_perm_hours =0
            creation_date2 =''
            modified_date2 =''
            permission_date2 =''
            permission_from_time2 =''
            permission_to_time2 =''
            total_time2 = ''
            reason2 =''
            second_permission = False
            for perm in permission_data:
                
                frappe.errprint(perm)
                permission = perm
                if permission:
                    if first_permission and not second_permission:
                        first_permission = False
                        second_permission =True
                        creation_date1 = permission['posting_date'].strftime('%d-%m-%Y') if permission['posting_date'] else ''
                        modified_date1 = permission['modified'].strftime('%d-%m-%Y') if permission['modified'] else ''
                        permission_date1 = permission['permission_date'].strftime('%d-%m-%Y') if permission['permission_date'] else ''
                        total_time1=permission['total_time'] if permission['total_time'] else 0.0
                        reason1 = permission['reason'] if permission['reason'] else ''
                        total_perm_hours += float(total_time1)
                        shift1 = permission['shift']
                        session1 = permission['session']
                        permission_from_time1 = permission['permission_from_time'] if permission['permission_from_time'] else ''
                        permission_to_time1 = permission['permission_to_time'] if permission['permission_to_time'] else ''
                        frappe.errprint(shift1)
                        perm_date1 = permission['permission_date']
                        if shift1:
                            frappe.errprint(session1)
                            if session1 == 'First Half':
                                get_shift_time = frappe.db.get_value('Shift Type',{'name':shift1},['start_time'])
                                frappe.errprint(get_shift_time)
                                frappe.errprint(total_time1)
                                permission_from_time1 = get_shift_time
                                if int(total_time1) == 1:
                                    frappe.errprint(total_time1)
                                    permission_to_time1 = timedelta(hours=1) + get_shift_time
                                elif int(total_time1) == 2:
                                    permission_to_time1 = timedelta(hours=2) + get_shift_time
                                elif int(total_time1) == 3:
                                    permission_to_time1 = timedelta(hours=3) + get_shift_time
                                elif int(total_time1) == 4:
                                    permission_to_time1 = timedelta(hours=4) + get_shift_time
                            elif session1 == 'Second Half':
                                frappe.errprint('aaaa')
                                get_shift_end_time = frappe.db.get_value('Shift Type',{'name':shift1},['end_time'])
                                permission_to_time1 = get_shift_end_time
                                if int(total_time1) == 1:
                                    shift_end_time = datetime.strptime(str(get_shift_end_time), '%H:%M:%S').time()
                                    end_time = dt.datetime.combine(perm_date1, shift_end_time)
                                    permission_from_time1 = end_time - timedelta(hours=1)
                                    permission_from_time1 = permission_from_time1.time().strftime("%H:%M:%S")
                                    frappe.errprint(permission_from_time1)
                                elif int(total_time1) == 2:
                                    shift_end_time = datetime.strptime(str(get_shift_end_time), '%H:%M:%S').time()
                                    end_time = dt.datetime.combine(perm_date1, shift_end_time)
                                    permission_from_time1 = end_time - timedelta(hours=2)
                                    permission_from_time1 = permission_from_time1.time().strftime("%H:%M:%S")
                                    frappe.errprint(permission_from_time1)
                                elif int(total_time1) == 3:
                                    shift_end_time = datetime.strptime(str(get_shift_end_time), '%H:%M:%S').time()
                                    end_time = dt.datetime.combine(perm_date1, shift_end_time)
                                    permission_from_time1 = end_time - timedelta(hours=3)
                                    permission_from_time1 = permission_from_time1.time().strftime("%H:%M:%S")
                                    frappe.errprint(permission_from_time1)
                                elif int(total_time1) == 4:
                                    shift_end_time = datetime.strptime(str(get_shift_end_time), '%H:%M:%S').time()
                                    end_time = dt.datetime.combine(perm_date1, shift_end_time)
                                    permission_from_time1 = end_time - timedelta(hours=4)
                                    permission_from_time1 = permission_from_time1.time().strftime("%H:%M:%S")
                                    frappe.errprint(permission_from_time1)
                            else:
                                permission_from_time1 = permission['permission_from_time'] if permission['permission_from_time'] else ''
                                permission_to_time1 = permission['permission_to_time'] if permission['permission_to_time'] else ''

                    elif second_permission and not first_permission:
                        creation_date2 = permission['posting_date'].strftime('%d-%m-%Y') if permission['posting_date'] else ''
                        modified_date2 = permission['modified'].strftime('%d-%m-%Y') if permission['modified'] else ''
                        permission_date2 = permission['permission_date'].strftime('%d-%m-%Y') if permission['permission_date'] else ''
                        permission_from_time2 = permission['permission_from_time'] if permission['permission_from_time'] else ''
                        permission_to_time2 = permission['permission_to_time'] if permission['permission_to_time'] else ''
                        total_time2 = permission['total_time'] if permission['total_time'] else 0.0
                        reason2 = permission['reason'] if permission['reason'] else ''
                        total_perm_hours += float(total_time2)
                        shift2 =permission['shift']
                        session2 = permission['session']
                        perm_date2 = permission['permission_date']
                        frappe.errprint(shift2)
                        if shift2:
                            frappe.errprint(session2)
                            if session2 == 'First Half':
                                get_shift_start_time2 = frappe.db.get_value('Shift Type',{'name':shift2},['start_time'])
                                permission_from_time2 = get_shift_start_time2
                                frappe.errprint(get_shift_start_time2)
                                if int(total_time2) == 1:
                                    permission_to_time2 = timedelta(hours=1) + get_shift_start_time2
                                elif int(total_time2) == 2:
                                    permission_to_time2 = timedelta(hours=2) + get_shift_start_time2
                                elif int(total_time2) == 3:
                                    permission_to_time2 = timedelta(hours=3) + get_shift_start_time2
                                elif int(total_time2) == 4:
                                    permission_to_time2 = timedelta(hours=4) + get_shift_start_time2
                            elif session2 == 'Second Half':
                                frappe.errprint(session2)
                                get_shift_end_time2 = frappe.db.get_value('Shift Type',{'name':shift2},['end_time'])
                                permission_to_time2 = get_shift_end_time2
                                frappe.errprint(get_shift_end_time2)
                                frappe.errprint(total_time2)
                                if int(total_time2) == 1:
                                    shift_end_time = datetime.strptime(str(get_shift_end_time2), '%H:%M:%S').time()
                                    end_time = dt.datetime.combine(perm_date2, shift_end_time)
                                    permission_from_time2 = end_time - timedelta(hours=1)
                                    permission_from_time2 = permission_from_time2.time().strftime("%H:%M:%S")
                                    frappe.errprint(permission_from_time2)
                                elif int(total_time2) == 2:
                                    shift_end_time = datetime.strptime(str(get_shift_end_time2), '%H:%M:%S').time()
                                    end_time = dt.datetime.combine(perm_date2, shift_end_time)
                                    permission_from_time2 = end_time - timedelta(hours=2)
                                    permission_from_time2 = permission_from_time2.time().strftime("%H:%M:%S")
                                    frappe.errprint(permission_from_time2)
                                elif int(total_time2) == 3:
                                    shift_end_time = datetime.strptime(str(get_shift_end_time2), '%H:%M:%S').time()
                                    end_time = dt.datetime.combine(perm_date2, shift_end_time)
                                    permission_from_time2 = end_time - timedelta(hours=3)
                                    permission_from_time2 = permission_from_time2.time().strftime("%H:%M:%S")
                                    frappe.errprint(permission_from_time2)
                                elif int(total_time2) == 4:
                                    shift_end_time = datetime.strptime(str(get_shift_end_time2), '%H:%M:%S').time()
                                    end_time = dt.datetime.combine(perm_date2, shift_end_time)
                                    permission_from_time2 = end_time - timedelta(hours=4)
                                    permission_from_time2 = permission_from_time2.time().strftime("%H:%M:%S")
                                    frappe.errprint(permission_from_time2)
                            else:
                                permission_from_time2 = permission['permission_from_time'] if permission['permission_from_time'] else ''
                                permission_to_time2 = permission['permission_to_time'] if permission['permission_to_time'] else ''
                                
            rows += f"""
                <tr>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{index1}</td>
                    <td rowspan="2" style="text-align: center; border: 1px solid black;">{months[m_index]}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{creation_date1}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{modified_date1}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{permission_date1}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{permission_from_time1}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{permission_to_time1}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{total_time1}</td>
                    <td rowspan="2" style="text-align: center; border: 1px solid black;">{total_perm_hours}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{reason1}</td>
                </tr>
                <tr>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{index2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{creation_date2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{modified_date2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{permission_date2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{permission_from_time2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{permission_to_time2}</td>
                    
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{total_time2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{reason2}</td>
                </tr>
                """        
        else:
            rows += f"""
                <tr>
                    <td colspan="1" style="text-align: center; border: 1px solid black;">{index1}</td>
                    <td rowspan="2" style="text-align: center; border: 1px solid black;">{months[m_index]}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td rowspan="2" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                </tr>
                <tr>
                    <td colspan="1" style="text-align: center;border: 1px solid black;">{index2}</td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                    <td colspan="1" style="text-align: center; border: 1px solid black;"></td>
                </tr>
            """
        
    doj = emp_data['date_of_joining'].strftime('%d-%m-%Y')
    data = f"""
    <h3 style="text-align: center;">DWSI - PERMISSION CARD FOR THE YEAR - {year}</h3>
    <div style="overflow-x: auto; color: black;">

        <table border="0" style="width: 100%; border-collapse: collapse; text-align: left;border: none;">
            <tr>
                <td colspan="3"><strong>NAME</strong></td>
                <td colspan="4">:&nbsp;&nbsp;{emp_data['first_name']}</td>
                <td colspan="1"><strong>DIVISION</strong></td>
                <td>:&nbsp;&nbsp;{emp_data['employee_type']}</td>
            </tr>
            <tr>
                <td colspan="3"><strong>DESIGNATION</strong></td>
                <td colspan="4">:&nbsp;&nbsp;{emp_data['designation']}</td>
                <td colspan="1"><strong>DEPT</strong></td>
                <td>:&nbsp;&nbsp;{emp_data['department']}</td>
            </tr>
            <tr>
                <td colspan="3"><strong>EMP NO</strong></td>
                <td colspan="4">:&nbsp;&nbsp;{employee}</td>
                <td colspan="1"><strong>DOJ</strong></td>
                <td>:&nbsp;&nbsp;{doj}</td>
            </tr>

            <tr>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">S.No.</th>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">MONTH</th>
              <th rowspan ="2" style="text-align: center; border: 1px solid black;">APPLTN. DATE</th>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">APPRVL DATE</th>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">PERMISSION DATE</th>
              <th colspan="2" style="text-align: center; border: 1px solid black;">PERMISSION HOURS</th>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">TOTAL HOURS</th>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">ACCUMULATED HOURS</th>
              <th rowspan="2" style="text-align: center; border: 1px solid black;">REASON FOR PERMISSION</th>
            </tr>
            <tr>
                <th style="text-align: center; border: 1px solid black;">FROM</th>
                <th style="text-align: center; border: 1px solid black;">TO</th>
            </tr>
                {rows}
        </table>
    </div>
    """
    return data



from datetime import date
from calendar import monthrange

@frappe.whitelist()
def get_month_start_and_end(year, month):
    # Convert year to integer
    year = int(year)
    
    # Convert month name to its corresponding integer
    month_map = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }
    month = month_map[month]

    start_date = date(year, month, 1)
    last_day = monthrange(year, month)[1]
    end_date = date(year, month, last_day)
    
    return start_date, end_date

