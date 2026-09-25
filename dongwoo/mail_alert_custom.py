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
def create_hooks_att11():
    job = frappe.db.exists('Scheduled Job Type', 'create_woff11')
    if not job:
        att = frappe.new_doc("Scheduled Job Type")
        att.update({
            "method": 'dongwoo.mail_alert_custom.create_off111',
            "frequency": 'Cron',
            "cron_format": "0 9 * * *"
        })
        att.save(ignore_permissions=True)

@frappe.whitelist()
def create_off111():
    from_date = add_days(today(),-1)
    to_date = today()
    attendance=frappe.db.get_all("Attendance",{"attendance_date":("Between",(from_date,to_date)),"docstatus":['!=',2]},['*'])
    for doc in attendance:
        if doc.employee_type == "Staff" and doc.in_time and doc.out_time:
            print('1')
            shift=''
            if doc.shift:
                print('2')
                if doc.shift=="A":
                    shift='C'
                    shiftdate=add_days(doc.attendance_date,1)
                elif doc.shift=="B":
                    shift='A'
                    shiftdate=add_days(doc.attendance_date,1)
                else:
                    shift='B'
                    shiftdate=add_days(doc.attendance_date,2)
                shift_end=frappe.db.get_value("Shift Type",{'name':shift},['end_time'])
                shift_etime = datetime.strptime(str(shift_end), '%H:%M:%S').time()
                shift_start_datetime = datetime.combine(shiftdate, shift_etime)
                if doc.working_hours >= 24 and  doc.out_time >= shift_start_datetime:
                    print('3')
                    hh=check_holiday(shiftdate,doc.employee)
                    if not hh:
                        print('4')
                        if not frappe.db.exists("Shift Assignment", {'employee': doc.employee, 'start_date': shiftdate, 'end_date': shiftdate, 'docstatus': ['!=',2]}):
                            print('5')
                            sa = frappe.new_doc('Shift Assignment')
                            sa.employee = doc.employee
                            sa.shift_type = "WW"
                            sa.start_date = shiftdate
                            sa.end_date = shiftdate
                            sa.reason = 'Week Off automatically created for 24 hours working'
                            sa.save(ignore_permissions=True)
                            sa.submit()
                            frappe.db.commit()
                        else:
                            if frappe.db.exists("Shift Assignment", {'employee': doc.employee, 'start_date': shiftdate, 'end_date': shiftdate, 'docstatus': 1}):
                                print('6')
                                sa_exist=frappe.get_doc("Shift Assignment", {'employee': doc.employee, 'start_date': shiftdate, 'end_date': shiftdate, 'docstatus': 1})
                                sa_exist.cancel() 
                                frappe.db.commit()
                                sa = frappe.new_doc('Shift Assignment')
                                sa.employee = doc.employee
                                sa.shift_type = "WW"
                                sa.start_date = shiftdate
                                sa.end_date = shiftdate
                                sa.reason = 'Week Off automatically created for 24 hours working'
                                sa.save(ignore_permissions=True)
                                sa.submit()
                                frappe.db.commit()



@frappe.whitelist()
#send a mail alert if any scheduled job failed
def schedule_log_fail(doc,method):
    if doc.status=='Failed':
        message = """
        The schedule Job type <b>{}</b> is failed. <br>Kindly check the log <b>{}</b>
        """.format(doc.scheduled_job_type,doc.name)
        frappe.sendmail(
                recipients=["erp@groupteampro.com"],
                subject='Scheduled Job type failed (DWSI)',
                message=message
            )
        
@frappe.whitelist()
def create_overtime_approver_hr():
    job = frappe.db.exists('Scheduled Job Type', 'overtime_approver_hr')
    if not job:
        att = frappe.new_doc("Scheduled Job Type")
        att.update({
            "method": 'dongwoo.mail_alert_custom.overtime_approver_hr',
            "frequency": 'Cron',
            "cron_format": "0 10 * * *"
        })
        att.save(ignore_permissions=True)

#will send a mail of last three days pending Overtime Request Repot to all HR Users
@frappe.whitelist()
def overtime_approver_hr():
    day = add_days(frappe.utils.today(), -3)
    
    # Query to get all open Permissions
    ot_application = frappe.db.sql("""
        SELECT * FROM `tabOvertime Request`
        WHERE posting_date <= '%s' AND workflow_state not in ('Draft', 'Cancelled', 'Approved', 'Rejected') 
        ORDER BY employee
    """ % (day), as_dict=True)
    
    if ot_application:
        # Prepare the table header and content
        data = """
            <div style="text-align: center;">
                <h2 style="font-size: 16px;">Overtime Request Application Report</h2>
            </div>
            <table style="border-collapse: collapse; width: 100%; border: 1px solid black; font-size: 10px;">
                <tr style="border: 1px solid black;">
                    <th style="padding: 4px; border: 1px solid black;">Employee</th>
                    <th style="padding: 4px; border: 1px solid black;">Employee Name</th>
                    <th style="padding: 4px; border: 1px solid black;">Department</th>
                    <th style="padding: 4px; border: 1px solid black;">Posting Date</th>
                    <th style="padding: 4px; border: 1px solid black;">OT Date</th>
                    <th style="padding: 4px; border: 1px solid black;">From Time</th>
                    <th style="padding: 4px; border: 1px solid black;">To Time</th>
                    <th style="padding: 4px; border: 1px solid black;">OT Hours</th>
                    <th style="padding: 4px; border: 1px solid black;">Status</th>
                </tr>
        """
        for ot in ot_application:
            data += """
            <tr style="border: 1px solid black;">
                <td style="padding: 4px; border: 1px solid black;">{0}</td>
                <td style="padding: 4px; border: 1px solid black;">{1}</td>
                <td style="padding: 4px; border: 1px solid black;">{2}</td>
                <td style="padding: 4px; border: 1px solid black;text-align: center;">{3}</td>
                <td style="padding: 4px; border: 1px solid black;text-align: center;">{4}</td>
                <td style="padding: 4px; border: 1px solid black;text-align: center;">{5}</td>
                <td style="padding: 4px; border: 1px solid black;text-align: center;">{6}</td>
                <td style="padding: 4px; border: 1px solid black;text-align: center;">{7}</td>
                <td style="padding: 4px; border: 1px solid black;text-align: center;">{8}</td>
            </tr>
            """.format(ot.employee, ot.employee_name, ot.department, format_date(ot.posting_date) or '', 
                       format_date(ot.ot_date) or ' ', ot.from_time, ot.to_time, ot.total_hours, ot.workflow_state)
        
        data += "</table>"

        # Query to get all users with the HR role
        hr_users = frappe.db.sql("""
            SELECT DISTINCT user.name 
            FROM `tabUser` AS user 
            INNER JOIN `tabHas Role` AS role 
            ON user.name = role.parent 
            WHERE role.role = 'HR Manager' 
            AND user.enabled = 1
        """, as_list=True)

        recipients = [user[0] for user in hr_users]
        # recipients = ['amar.p@groupteampro.com']

        # Send the email to all HR users with pending Permissions
        frappe.sendmail(
            recipients=recipients,
            subject='Overtime Request Application Report',
            message="""Dear Sir,<br><br>
                        Kindly find the attached employee's pending Overtime Request Application List:<br>{0}
                     """.format(data)
        )


@frappe.whitelist()
def create_permission_approvers():
    job = frappe.db.exists('Scheduled Job Type', 'permission_approvers')
    if not job:
        att = frappe.new_doc("Scheduled Job Type")
        att.update({
            "method": 'dongwoo.mail_alert_custom.permission_approvers',
            "frequency": 'Cron',
            "cron_format": "0 10 * * *"
        })
        att.save(ignore_permissions=True)

#will send a mail of last three days pending Permission Repot to all level approvers
@frappe.whitelist()
def permission_approvers():
    day = add_days(frappe.utils.today(), -3)
    
    def send_email_report(approver_field, approver_level, workflow_state):
        user_list = frappe.db.sql(f"""
            SELECT {approver_field} 
            FROM `tabPermission` 
            WHERE {approver_field} IS NOT NULL 
            GROUP BY {approver_field}
        """, as_dict=True)
        
        for user in user_list:
            approver_email = user.get(approver_field)
            if not approver_email:
                continue
            
            permission_apps = frappe.db.sql(f"""
                SELECT employee, employee_name, department, posting_date, permission_date, permission_hour, workflow_state
                FROM `tabPermission`
                WHERE {approver_field} = %s AND posting_date <= %s AND workflow_state = %s
            """, (approver_email, day, workflow_state), as_dict=True)
            
            # Send message if no Permissions are found
            # if not permission_apps:
            # 	print("hi")
            # 	continue
            
            data = """
                <div style="text-align: center;">
                    <h2 style="font-size: 16px;">Permission Application Report</h2>
                </div>
                <table style="border-collapse: collapse; width: 100%; border: 1px solid black; font-size: 10px;">
                    <tr style="border: 1px solid black;">
                        <th style="padding: 4px; border: 1px solid black;">Employee</th>
                        <th style="padding: 4px; border: 1px solid black;">Employee Name</th>
                        <th style="padding: 4px; border: 1px solid black;">Department</th>
                        <th style="padding: 4px; border: 1px solid black;">Posting Date</th>
                        <th style="padding: 4px; border: 1px solid black;">Permission Date</th>
                        <th style="padding: 4px; border: 1px solid black;">Permission Hour</th>
                        <th style="padding: 4px; border: 1px solid black;">Status</th>
                    </tr>
            """
            
            for pa in permission_apps:
                data += f"""
                    <tr style="border: 1px solid black;">
                        <td style="padding: 4px; border: 1px solid black;">{pa.employee}</td>
                        <td style="padding: 4px; border: 1px solid black;">{pa.employee_name}</td>
                        <td style="padding: 4px; border: 1px solid black;">{pa.department}</td>
                        <td style="padding: 4px; border: 1px solid black; text-align: center;">{format_date(pa.posting_date) or ''}</td>
                        <td style="padding: 4px; border: 1px solid black; text-align: center;">{format_date(pa.permission_date) or ' '}</td>
                        <td style="padding: 4px; border: 1px solid black; text-align: center;">{pa.permission_hour}</td>
                        <td style="padding: 4px; border: 1px solid black; text-align: center;">{pa.workflow_state}</td>
                    </tr>
                """
            
            data += "</table>"
            if permission_apps:
                frappe.sendmail(
                    recipients=[approver_email],
                    # recipients=['amar.p@groupteampro.com', 'jeniba.a@groupteampro.com'], 
                    subject=f'Permission Application - Pending for Level {approver_level} Approver',
                    message=f"""Dear Sir,<br><br>
                    Kindly find the attached employee's pending Permission Application List :<br>{data}"""
                )
    
    send_email_report('level_1_approver', 1, 'Pending for Level 1 Approver')
    send_email_report('level_2_approver', 2, 'Pending for Level 2 Approver')
    send_email_report('level_3_approver', 3, 'Pending for Level 3 Approver')
    send_email_report('level_4_approver', 4, 'Pending for Level 4 Approver')
    send_email_report('level_5_approver', 5, 'Pending for Level 5 Approver')
    send_email_report('level_6_approver', 6, 'Pending for Level 6 Approver')
    send_email_report('level_7_approver', 7, 'Pending for Level 7 Approver')
    send_email_report('level_8_approver', 8, 'Pending for Level 8 Approver')
    send_email_report('level_9_approver', 9, 'Pending for Level 9 Approver')
    send_email_report('level_10_approver', 10, 'Pending for Level 10 Approver')
 



@frappe.whitelist()
def create_permission_approver_hr():
    job = frappe.db.exists('Scheduled Job Type', 'permission_approver_hr')
    if not job:
        att = frappe.new_doc("Scheduled Job Type")
        att.update({
            "method": 'dongwoo.mail_alert_custom.permission_approver_hr',
            "frequency": 'Cron',
            "cron_format": "0 10 * * *"
        })
        att.save(ignore_permissions=True)


@frappe.whitelist()
def permission_approver_hr():
    day = add_days(frappe.utils.today(), -3)
    permission_application = frappe.db.sql("""
        SELECT * FROM `tabPermission`
        WHERE posting_date <= '%s' AND workflow_state not in ('Draft', 'Cancelled', 'Approved', 'Rejected') 
        ORDER BY employee
    """ % (day), as_dict=True)
    
    if permission_application:
        data = """
            <div style="text-align: center;">
                <h2 style="font-size: 16px;">Permission Application Report</h2>
            </div>
            <table style="border-collapse: collapse; width: 100%; border: 1px solid black; font-size: 10px;">
                <tr style="border: 1px solid black;">
                    <th style="padding: 4px; border: 1px solid black;">Employee</th>
                    <th style="padding: 4px; border: 1px solid black;">Employee Name</th>
                    <th style="padding: 4px; border: 1px solid black;">Department</th>
                    <th style="padding: 4px; border: 1px solid black;">Posting Date</th>
                    <th style="padding: 4px; border: 1px solid black;">Permission Date</th>
                    <th style="padding: 4px; border: 1px solid black;">Permission Hour</th>
                    <th style="padding: 4px; border: 1px solid black;">Status</th>
                </tr>
        """
        for pa in permission_application:
            data += """
            <tr style="border: 1px solid black;">
                <td style="padding: 4px; border: 1px solid black;">{0}</td>
                <td style="padding: 4px; border: 1px solid black;">{1}</td>
                <td style="padding: 4px; border: 1px solid black;">{2}</td>
                <td style="padding: 4px; border: 1px solid black;text-align: center;">{3}</td>
                <td style="padding: 4px; border: 1px solid black;text-align: center;">{4}</td>
                <td style="padding: 4px; border: 1px solid black;text-align: center;">{5}</td>
                <td style="padding: 4px; border: 1px solid black;text-align: center;">{6}</td>
            </tr>
            """.format(pa.employee, pa.employee_name, pa.department, format_date(pa.posting_date) or '', 
                       format_date(pa.permission_date) or ' ', pa.permission_hour, pa.workflow_state)
        
        data += "</table>"

        # Query to get all users with the HR role
        hr_users = frappe.db.sql("""
            SELECT DISTINCT user.name 
            FROM `tabUser` AS user 
            INNER JOIN `tabHas Role` AS role 
            ON user.name = role.parent 
            WHERE role.role = 'HR Manager' 
            AND user.enabled = 1
        """, as_list=True)

        recipients = [user[0] for user in hr_users]
        # recipients = ['amar.p@groupteampro.com']
    
        frappe.sendmail(
            recipients=recipients,
            subject='Permission Application Report',
            message="""Dear Sir,<br><br>
                        Kindly find the attached employee's pending Permission List:<br>{0}
                     """.format(data)
        )


@frappe.whitelist()
def create_onduty_approvers():
    job = frappe.db.exists('Scheduled Job Type', 'onduty_approvers')
    if not job:
        att = frappe.new_doc("Scheduled Job Type")
        att.update({
            "method": 'dongwoo.mail_alert_custom.onduty_approvers',
            "frequency": 'Cron',
            "cron_format": "0 10 * * *"
        })
        att.save(ignore_permissions=True)

@frappe.whitelist()
def onduty_approvers():
    day = add_days(frappe.utils.today(), -3)
    
    def send_email_report(approver_field, approver_level, workflow_state):
        user_list = frappe.db.sql(f"""
            SELECT {approver_field} 
            FROM `tabOn Duty Application` 
            WHERE {approver_field} IS NOT NULL 
            GROUP BY {approver_field}
        """, as_dict=True)
        
        for user in user_list:
            approver_email = user.get(approver_field)
            if not approver_email:
                continue
            
            onduty_apps = frappe.db.sql(f"""
                SELECT employee, employee_name, department, posting_date, od_date, session, workflow_state
                FROM `tabOn Duty Application`
                WHERE {approver_field} = %s AND posting_date <= %s AND workflow_state = %s
            """, (approver_email, day, workflow_state), as_dict=True)
            
            # Send message if no On Duty Applications are found
            # if not onduty_apps:
            # 	print("hi")
            # 	continue
            
            data = """
                <div style="text-align: center;">
                    <h2 style="font-size: 16px;">On Duty Application Report</h2>
                </div>
                <table style="border-collapse: collapse; width: 100%; border: 1px solid black; font-size: 10px;">
                    <tr style="border: 1px solid black;">
                        <th style="padding: 4px; border: 1px solid black;">Employee</th>
                        <th style="padding: 4px; border: 1px solid black;">Employee Name</th>
                        <th style="padding: 4px; border: 1px solid black;">Department</th>
                        <th style="padding: 4px; border: 1px solid black;">Posting Date</th>
                        <th style="padding: 4px; border: 1px solid black;">OD Date</th>
                        <th style="padding: 4px; border: 1px solid black;">Session</th>
                        <th style="padding: 4px; border: 1px solid black;">Status</th>
                    </tr>
            """
            
            for od in onduty_apps:
                data += f"""
                    <tr style="border: 1px solid black;">
                        <td style="padding: 4px; border: 1px solid black;">{od.employee}</td>
                        <td style="padding: 4px; border: 1px solid black;">{od.employee_name}</td>
                        <td style="padding: 4px; border: 1px solid black;">{od.department}</td>
                        <td style="padding: 4px; border: 1px solid black; text-align: center;">{format_date(od.posting_date) or ''}</td>
                        <td style="padding: 4px; border: 1px solid black; text-align: center;">{format_date(od.od_date) or ' '}</td>
                        <td style="padding: 4px; border: 1px solid black; text-align: center;">{od.session}</td>
                        <td style="padding: 4px; border: 1px solid black; text-align: center;">{od.workflow_state}</td>
                    </tr>
                """
            
            data += "</table>"
            if onduty_apps:
                frappe.sendmail(
                    recipients=[approver_email],
                    # recipients=['amar.p@groupteampro.com', 'jeniba.a@groupteampro.com'], 
                    subject=f'On Duty Application - Pending for Level {approver_level} Approver',
                    message=f"""Dear Sir,<br><br>
                    Kindly find the attached employee's pending On Duty Application List :<br>{data}"""
                )
    
    # Send reports for each level
    send_email_report('level_1_approver', 1, 'Pending for Level 1 Approver')
    send_email_report('level_2_approver', 2, 'Pending for Level 2 Approver')
    send_email_report('level_3_approver', 3, 'Pending for Level 3 Approver')
    send_email_report('level_4_approver', 4, 'Pending for Level 4 Approver')
    send_email_report('level_5_approver', 5, 'Pending for Level 5 Approver')
    send_email_report('level_6_approver', 6, 'Pending for Level 6 Approver')
    send_email_report('level_7_approver', 7, 'Pending for Level 7 Approver')
    send_email_report('level_8_approver', 8, 'Pending for Level 8 Approver')
    send_email_report('level_9_approver', 9, 'Pending for Level 9 Approver')
    send_email_report('level_10_approver', 10, 'Pending for Level 10 Approver')


@frappe.whitelist()
def create_onduty_approvers_hr():
    job = frappe.db.exists('Scheduled Job Type', 'onduty_approvers_hr')
    if not job:
        att = frappe.new_doc("Scheduled Job Type")
        att.update({
            "method": 'dongwoo.mail_alert_custom.onduty_approvers_hr',
            "frequency": 'Cron',
            "cron_format": "0 10 * * *"
        })
        att.save(ignore_permissions=True)


#will send a mail of last three days pending On Duty Application Repot for all HR Users
@frappe.whitelist()
def onduty_approver_hr():
    day = add_days(frappe.utils.today(), -3)
    onduty_application = frappe.db.sql("""
        SELECT * FROM `tabOn Duty Application`
        WHERE posting_date <= '%s' and workflow_state not in ('Cancelled', 'Approved', 'Rejected', 'Draft') 
        ORDER BY employee
    """ %(day), as_dict=True)
    if onduty_application:

        data = """
            <div style="text-align: center;">
                <h2 style="font-size: 16px;">On Duty Application Report</h2>
            </div>
            <table style="border-collapse: collapse; width: 100%; border: 1px solid black; font-size: 10px;">
                <tr style="border: 1px solid black;">
                    <th style="padding: 4px; border: 1px solid black;">Employee</th>
                    <th style="padding: 4px; border: 1px solid black;">Employee Name</th>
                    <th style="padding: 4px; border: 1px solid black;">Department</th>
                    <th style="padding: 4px; border: 1px solid black;">Posting Date</th>
                    <th style="padding: 4px; border: 1px solid black;">OD Date</th>
                    <th style="padding: 4px; border: 1px solid black;">Session</th>
                    <th style="padding: 4px; border: 1px solid black;">Status</th>
                </tr>
        """
        for od in onduty_application:
            data += """
            <tr style="border: 1px solid black;">
                <td style="padding: 4px; border: 1px solid black;">{0}</td>
                <td style="padding: 4px; border: 1px solid black;">{1}</td>
                <td style="padding: 4px; border: 1px solid black;">{2}</td>
                <td style="padding: 4px; border: 1px solid black;text-align: center;">{3}</td>
                <td style="padding: 4px; border: 1px solid black;text-align: center;">{4}</td>
                <td style="padding: 4px; border: 1px solid black;text-align: center;">{5}</td>
                <td style="padding: 4px; border: 1px solid black;text-align: center;">{6}</td>
            </tr>
            """.format(od.employee, od.employee_name, od.department, format_date(od.posting_date) or '', 
                       format_date(od.od_date) or ' ', od.session, od.workflow_state)
        
        data += "</table>"

        hr_users = frappe.db.sql("""
            SELECT DISTINCT user.name 
            FROM `tabUser` AS user 
            INNER JOIN `tabHas Role` AS role 
            ON user.name = role.parent 
            WHERE role.role = 'HR Manager' 
            AND user.enabled = 1
        """, as_list=True)

        recipients = [user[0] for user in hr_users]

        frappe.sendmail(
            recipients=recipients,
            subject='On Duty Application Report',
            message="""Dear Sir,<br><br>
                        Kindly find the attached employee's pending On Duty Application List:<br>{0}
                     """.format(data)
        )


@frappe.whitelist()
def create_leave_approvers():
    job = frappe.db.exists('Scheduled Job Type', 'leave_approvers')
    if not job:
        att = frappe.new_doc("Scheduled Job Type")
        att.update({
            "method": 'dongwoo.mail_alert_custom.leave_approvers',
            "frequency": 'Cron',
            "cron_format": "0 10 * * *"
        })
        att.save(ignore_permissions=True)



#send a mail to all level Approvers with the report of lasy three days pending leave applications
@frappe.whitelist()
def leave_approvers():
    day = add_days(frappe.utils.today(), -3)
    def send_email_report(approver_field, approver_level, workflow_state):
        user_list = frappe.db.sql(f"""
            SELECT {approver_field} 
            FROM `tabLeave Application` 
            WHERE {approver_field} IS NOT NULL 
            GROUP BY {approver_field}
        """, as_dict=True)
        
        for user in user_list:
            approver_email = user.get(approver_field)
            if not approver_email:
                continue
            
            leave_apps = frappe.db.sql(f"""
                SELECT employee, employee_name, department, leave_type, from_date, to_date, workflow_state
                FROM `tabLeave Application`
                WHERE {approver_field} = %s AND from_date <= %s AND workflow_state = %s
            """, (approver_email, day, workflow_state), as_dict=True)
            
            # Send message if no leave applications are found
            # if not leave_apps:
            # 	print("hi")
            # 	continue
            
            data = """
                <div style="text-align: center;">
                    <h2 style="font-size: 16px;">Leave Application Report</h2>
                </div>
                <table style="border-collapse: collapse; width: 100%; border: 1px solid black; font-size: 10px;">
                    <tr style="border: 1px solid black;">
                        <th style="padding: 4px; border: 1px solid black;">Employee</th>
                        <th style="padding: 4px; border: 1px solid black;">Employee Name</th>
                        <th style="padding: 4px; border: 1px solid black;">Department</th>
                        <th style="padding: 4px; border: 1px solid black;">Leave Type</th>
                        <th style="padding: 4px; border: 1px solid black;">From Date</th>
                        <th style="padding: 4px; border: 1px solid black;">To Date</th>
                        <th style="padding: 4px; border: 1px solid black;">Status</th>
                    </tr>
            """
            
            for la in leave_apps:
                data += f"""
                    <tr style="border: 1px solid black;">
                        <td style="padding: 4px; border: 1px solid black;">{la.employee}</td>
                        <td style="padding: 4px; border: 1px solid black;">{la.employee_name}</td>
                        <td style="padding: 4px; border: 1px solid black;">{la.department}</td>
                        <td style="padding: 4px; border: 1px solid black; text-align: center;">{la.leave_type}</td>
                        <td style="padding: 4px; border: 1px solid black; text-align: center;">{format_date(la.from_date) or ' '}</td>
                        <td style="padding: 4px; border: 1px solid black; text-align: center;">{format_date(la.to_date) or ' '}</td>
                        <td style="padding: 4px; border: 1px solid black; text-align: center;">{la.workflow_state}</td>
                    </tr>
                """
            
            data += "</table>"
            if leave_apps:
                frappe.sendmail(
                    recipients=[approver_email],
                    subject=f'Leave Application - Pending for Level {approver_level} Approver',
                    message=f"""Dear Sir,<br><br>
                    Kindly find the attached employee's pending Leave Application List :<br>{data}"""
                )
    
    send_email_report('approver_1', 1, 'Pending for Level 1 Approver')
    send_email_report('approver_2', 2, 'Pending for Level 2 Approver')
    send_email_report('approver_3', 3, 'Pending for Level 3 Approver')
    send_email_report('approver_4', 4, 'Pending for Level 4 Approver')
    send_email_report('approver_5', 5, 'Pending for Level 5 Approver')
    send_email_report('approver_6', 6, 'Pending for Level 6 Approver')
    send_email_report('approver_7', 7, 'Pending for Level 7 Approver')
    send_email_report('approver_8', 8, 'Pending for Level 8 Approver')
    send_email_report('approver_9', 9, 'Pending for Level 9 Approver')
    send_email_report('approver_10', 10, 'Pending for Level 10 Approver')




@frappe.whitelist()
def create_job_fail1():
    job = frappe.db.exists('Scheduled Job Type', 'cron_failed1')
    if not job:
        emc = frappe.new_doc("Scheduled Job Type")
        emc.update({
            "method": 'dongwoo.mail_alert_custom.cron_failed_method1',
            "frequency": 'Cron',
            "cron_format": '*/5 * * * *'
        })
        emc.save(ignore_permissions=True)

@frappe.whitelist()
def cron_failed_method1():
    cutoff_time = datetime.now() - timedelta(minutes=5)
    failed_jobs = frappe.get_all(
        "Scheduled Job Log",
        filters={
            "status": "Failed",
            "creation": [">=", cutoff_time]
        },
        fields=["scheduled_job_type"]
    )
    unique_job_types = set()
    for job in failed_jobs:
        unique_job_types.add(job['scheduled_job_type'])

    for job_type in unique_job_types:
        frappe.sendmail(
            recipients = ["erp@groupteampro.com","jeniba.a@groupteampro.com"],
            subject = 'Failed Cron List - DONGWOO',
            message = 'Dear Sir / Mam <br> Kindly find the below failed Scheduled Job  %s'%(job_type)
        )



