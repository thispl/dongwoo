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



def create_salary_structure_assignment(doc, method=None):

    # if not doc.is_new():
    #     return

    if not doc.employee_type or not doc.company:
        return
    salary_structure_map = {
        "Staff": "Staff",
        "Worker": "Worker",
        "NAPS": "NAPS",
        "D . Trainee": "Trainee",
        "Contract Employee": "Contractor SS"
    }

    salary_structure = salary_structure_map.get(doc.employee_type)

    if not salary_structure:
        return

    exists = frappe.db.exists(
        "Salary Structure Assignment",
        {
            "employee": doc.name,
            "salary_structure": salary_structure,
            "docstatus": ["!=", 2]
        }
    )

    if exists:
        return

    ssa = frappe.new_doc("Salary Structure Assignment")
    ssa.employee = doc.name
    # ssa.company = doc.company
    ssa.salary_structure = salary_structure
    ssa.from_date = doc.date_of_joining
    # ssa.payroll_frequency = "Monthly"

    ssa.insert(ignore_permissions=True)
    ssa.submit()

    frappe.msgprint(
        "Salary Structure Assignment has been created against this employee."
    )




@frappe.whitelist()
def inactive_employee(doc,method):
    if doc.status=="Active":
        if doc.relieving_date:
            throw(_("Please remove the relieving date for the Active Employee."))


@frappe.whitelist()
def emp_type_order(doc,method):
    # frappe.errprint("HelloWorld")
    if doc.employee_type=="Staff":
        doc.employee_type_order='1'
    elif doc.employee_type=="Worker":
        doc.employee_type_order='2'
    elif doc.employee_type=="D . Trainee":
        doc.employee_type_order='3'
    elif doc.employee_type=="NAPS":
        doc.employee_type_order='4'
    elif doc.employee_type=="Contract Employee":
        doc.employee_type_order='5'
    else:
        doc.employee_type_order='6'





@frappe.whitelist()
def check_hra(doc, method):

    if not doc.gross_pay or doc.gross_pay <= 0:
        fields = [
            "basic","house_rent_allowance","medical_allowance",
            "conveyance_allowance","education_allowance",
            "leave_and_travel_allowance","dress_allowance",
            "pf","esi","ctc","bonus","gratuity",
            "leave_encashment_el","leve_encashment_cl"
        ]
        for f in fields:
            doc.set(f, 0)
        return

    gross = doc.gross_pay

    # Fixed benefits
    ayudha_pooja_gift = 10000
    birthday_coupon_self_and_spouse = 1000
    group_medi_claim_policy = 16000
    uniform_or_shoe = 3225

    # Salary split
    doc.basic = gross * 0.60
    doc.house_rent_allowance = gross * 0.20
    doc.medical_allowance = gross * 0.05
    doc.conveyance_allowance = gross * 0.04
    doc.education_allowance = gross * 0.04
    doc.leave_and_travel_allowance = gross * 0.04
    doc.dress_allowance = gross * 0.03
    doc.stipend = gross
    doc.actual_gross = gross

    # PF
    if doc.basic <= 15000:
        doc.pf = doc.basic * 0.13 * 12
    else:
        doc.pf = 1950 * 12

    # ESI
    if gross < 21000:
        doc.esi = gross * 0.0325 * 12
    else:
        doc.esi = 0

    # Leave encashment
    doc.leave_encashment_el = (gross / 30)
    doc.leve_encashment_cl = (gross / 30)

    # Bonus & gratuity
    doc.bonus = (doc.basic * 12 * 0.17) / 12
    doc.gratuity = round((doc.basic / 26 * 15) / 12)

    # CTC
    doc.ctc = (
        ayudha_pooja_gift +
        birthday_coupon_self_and_spouse +
        group_medi_claim_policy +
        uniform_or_shoe +
        doc.basic + doc.pf + doc.esi +
        doc.leave_encashment_el + doc.leve_encashment_cl +
        doc.bonus + doc.gratuity +
        doc.house_rent_allowance +
        doc.medical_allowance +
        doc.education_allowance +
        doc.leave_and_travel_allowance +
        doc.dress_allowance +
        doc.conveyance_allowance
    )

