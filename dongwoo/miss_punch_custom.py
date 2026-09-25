
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
def miss_punch_mail11():
    job = frappe.db.exists('Scheduled Job Type', 'Miss_punch_mail11')
    if not job:
        emc = frappe.new_doc("Scheduled Job Type")
        emc.update({
            "method": 'dongwoo.miss_punch_custom.send_miss_punch_report_mail11',
            "frequency": 'Cron',
            "cron_format": '0 10 * * *'
        })
        emc.save(ignore_permissions=True)


import frappe
from frappe.utils import nowdate, add_days, format_datetime

@frappe.whitelist()
def send_miss_punch_report_mail11():
    yesterday = add_days(nowdate(), -1)

    records = frappe.db.sql("""
        SELECT 
            emp.name AS employee_id,
            emp.employee_name,
            att.attendance_date,
            att.in_time,
            att.out_time,
            att.status,
            att.late_entry_time,
            att.early_out_time
        FROM `tabAttendance` att
        JOIN `tabEmployee` emp ON att.employee = emp.name
        WHERE att.attendance_date = %s
        AND att.status != 'On Leave'
        AND (
            (att.in_time IS NOT NULL AND att.out_time IS NULL)
            OR
            (att.in_time IS NULL AND att.out_time IS NOT NULL)
        )
        ORDER BY emp.employee_name
    """, (yesterday,), as_dict=1)

    if not records:
        return

    message = f"""
    <p>Dear Sir/Mam,</p>
    <p>Kindly find the below attached <b>Miss Punch List</b> for yesterday.</p>
    """

    table = """
        <table border="1" cellspacing="0" cellpadding="5" style="border-collapse:collapse; width:120%;">
            <tr style="background-color:#00008b; color:white; text-align:center;">
                <th style="text-align:center; width:5%;">S.No</th>
                <th style="text-align:center; width:10%;">Employee</th>
                <th style="text-align:center; width:15%;">Employee Name</th>
                <th style="text-align:center; width:15%;">Attendance Date</th>
                <th style="text-align:center; width:20%;">In Time</th>
                <th style="text-align:center; width:20%;">Out Time</th>
                <th style="text-align:center; width:10%;">Status</th>
                <th style="text-align:center; width:10%;">Late Entry</th>
                <th style="text-align:center; width:10%;">Early Exit</th>
            </tr>
    """

    for i, r in enumerate(records, start=1):
        table += f"""
            <tr>
                <td style="text-align:center; width:5%;">{i}</td>
                <td style="text-align:left; width:10%;">{r.employee_id}</td>
                <td style="text-align:left; width:20%;">{r.employee_name}</td>
                <td style="text-align:left; width:10%;">{formatdate(r.attendance_date, "dd-MM-yyyy")}</td>
                <td style="text-align:left; width:15%;">{format_datetime(r.in_time, "dd-MM-yyyy HH:mm") if r.in_time else ''}</td>
                <td style="text-align:left; width:15%;">{format_datetime(r.out_time, "dd-MM-yyyy HH:mm") if r.out_time else ''}</td>
                <td style="text-align:left; width:10%;">{r.status}</td>
                <td style="text-align:left; width:7%;">{r.late_entry or ''}</td>
                <td style="text-align:left; width:8%;">{r.early_exit or ''}</td>
            </tr>
        """
    table += "</table>"
    message += table
    message += "<p>Regards,<br>HR Department</p>"
    frappe.sendmail(
        recipients=["sivarenisha.m@groupteampro.com","info@dwsi.co.in","vishnu@dwsi.co.in","vishal@dwsi.co.in"],
        subject=f"Miss Punch Report - {formatdate(yesterday)}",
        message=message
    )

