# Copyright (c) 2023, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import (
    DATE_FORMAT,
    add_days,
    add_to_date,
    cint,
    comma_and,
    date_diff,
    flt,
    get_link_to_form,
    getdate,
)
from dateutil.relativedelta import relativedelta

class ReportDashboard(Document):
    def validate(self):
        if self.report and self.report=='Monthly Salary Report':
            if self.start_date:
                start_date=getdate(self.start_date)
                if start_date.day!=1:
                    self.start_date=''
                    frappe.throw("Kindly check the start date")
                if not frappe.db.exists("Salary Slip",{'start_date':start_date}):
                    self.start_date=''
                    frappe.throw('No salary slip found for this period')
@frappe.whitelist()
def get_end_date(start_date, frequency):
    if not frappe.db.exists("Salary Slip",{'start_date':start_date}):
        rep = frappe.get_single("Report Dashboard")
        rep.start_date = ''
        rep.end_date = ''
        rep.save() 
        frappe.throw('No salary slip found for this period')
    start_date = getdate(start_date)
    if start_date.day!=1:
        rep = frappe.get_single("Report Dashboard")
        rep.start_date = ''
        rep.save()  
        frappe.throw("Kindly check the start Date")
    frequency = frequency.lower() if frequency else "monthly"
    kwargs = (
        get_frequency_kwargs(frequency) if frequency != "bimonthly" else get_frequency_kwargs("monthly")
    )
    end_date = add_to_date(start_date, **kwargs) - relativedelta(days=1)
    if frequency == "monthly":
        return dict(end_date=end_date.strftime(DATE_FORMAT))

    else:
        return dict(end_date="")


def get_frequency_kwargs(frequency_name):
    frequency_dict = {
        "monthly": {"months": 1},
        "fortnightly": {"days": 14},
        "weekly": {"days": 7},
        "daily": {"days": 1},
    }
    return frequency_dict.get(frequency_name)



# @frappe.whitelist()
# def get_latest_rq_job():
#     latest_job = frappe.get_last_doc('RQ Job')
#     return latest_job
        
    
