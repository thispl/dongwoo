# Copyright (c) 2024, TEAMPROO and contributors
# For license information, please see license.txt

# Copyright (c) 2024, TEAMPRO and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from email import message
import re
from frappe import _
import frappe
from frappe.model.document import Document
from datetime import date, timedelta, datetime,time
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,

    nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime,today, format_date)
# import pandas as pd
import math
from frappe.utils import add_months, cint, flt, getdate, time_diff_in_hours,formatdate
import datetime as dt
from datetime import datetime, timedelta
from dongwoo.mark_attendance import mark_wh_ot_with_employee, mark_att_present_with_employee,mark_att_with_employee,mark_late_early_with_employee,update_regularize_ot_with_employee


class AttendanceRegularize(Document):
    def validate(self):    
        if frappe.db.exists("Attendance Regularize",{"attendance_date":self.attendance_date,'employee':self.employee,'docstatus':['!=',2],'name':['!=',self.name]}):
            formatted_date = formatdate(self.attendance_date, "dd-mm-yyyy")
            frappe.throw(f"Already another Attendance Regularize found on the <b>{formatted_date}</b>")
    # def on_submit(self):
    #     if self.corrected_shift or self.corrected_in or self.corrected_out :
    #         att = frappe.db.get_value("Attendance",{"employee": self.employee,"attendance_date": self.attendance_date,"docstatus": ["!=", 2]},"name")

    #         if att:
    #             frappe.db.set_value("Attendance", att, {"shift": self.corrected_shift,"regularize_marked": 1,"attendance_regularize": self.name})

    #             if self.in_time:
    #                 frappe.db.set_value("Attendance", att, "in_time", self.corrected_in)

    #             if self.out_time:
    #                 frappe.db.set_value("Attendance", att, "out_time", self.corrected_out)

    #             if self.ot_hours:
    #                 frappe.db.set_value("Attendance", att, "overtime_hours", self.corrected_ot)

    #         # if frappe.db.exists('Attendance',{'employee':self.employee,'attendance_date':self.attendance_date,'docstatus':['!=',2]}):
    #         #     att=frappe.db.get_value('Attendance',{'employee':self.employee,'attendance_date':self.attendance_date,'docstatus':['!=',2]},['name'])
    #         #     frappe.db.set_value('Attendance', att, 'shift', self.corrected_shift)
    #         #     if self.in_time==1:
    #         #         frappe.db.set_value('Attendance', att, 'in_time', self.corrected_in)
    #         #     if self.out_time==1:
    #         #         frappe.db.set_value('Attendance', att, 'out_time', self.corrected_out)
    #         #     if self.ot_hours==1:
    #         #         frappe.db.set_value('Attendance', att, 'overtime_hours', self.corrected_ot)
    #         #     frappe.db.set_value('Attendance', att,'regularize_marked', 1)
    #         #     frappe.db.set_value('Attendance', att,'attendance_regularize', self.name)
               
    #             # mark_wh_ot_with_employee(self.attendance_date,self.attendance_date,self.employee)
    #             # update_regularize_ot_with_employee(self.attendance_date,self.attendance_date,self.employee)
    #             # mark_late_early_with_employee(self.attendance_date,self.attendance_date,self.employee)
    #             # mark_att_present_with_employee(self.attendance_date,self.attendance_date,self.employee)
                    
    def on_submit(self):

        if not (self.corrected_shift or self.corrected_in or self.corrected_out or self.corrected_ot):
            return

        att_name = frappe.db.get_value(
            "Attendance",
            {
                "employee": self.employee,
                "attendance_date": self.attendance_date,
                "docstatus": ["!=", 2]
            },
            "name"
        )

        if not att_name:
            return

        # Build a single update dict to minimize database lock time
        update_values = {
            "regularize_marked": 1,
            "attendance_regularize": self.name,
        }

        if self.corrected_shift:
            update_values["shift"] = self.corrected_shift
        if self.corrected_in:
            update_values["in_time"] = self.corrected_in
        if self.corrected_out:
            update_values["out_time"] = self.corrected_out
        if self.corrected_ot:
            update_values["overtime_hours"] = self.corrected_ot

        frappe.db.set_value("Attendance", att_name, update_values, update_modified=False)

                
    def on_cancel(self):
        att = frappe.db.exists('Attendance',{'employee':self.employee,'attendance_date':self.attendance_date,'docstatus':["!=",2]})
        if att:
            att_reg = frappe.db.get_value('Attendance',{'name':att},['attendance_regularize'])
            if att_reg == self.name:
                update_values = {
                    'attendance_regularize': '',
                    'total_working_hours': "00:00:00",
                    'working_hours': "0.0",
                    'extra_hours': "0.0",
                    'total_extra_hours': "00:00:00",
                    'total_overtime_hours': "00:00:00",
                    'overtime_hours': "0.0",
                    'shift': '',
                    'in_time': None,
                    'out_time': None,
                    'late_entry': 0,
                    'late_entry_time': "00:00:00",
                    'regularize_marked': 0,
                    'early_exit': 0,
                    'status': 'Absent',
                    'early_out_time': "00:00:00",
                }
                frappe.db.set_value('Attendance', att, update_values, update_modified=False)

@frappe.whitelist()
def get_assigned_shift_details(emp,att_date):
    datalist = []
    data = {}
    assigned_shift = frappe.get_value("Employee",{'name':emp},['default_shift'])
    if assigned_shift != ' ':
        shift_in_time = frappe.db.get_value('Shift Type',{'name':assigned_shift},['start_time'])
        shift_out_time = frappe.db.get_value('Shift Type',{'name':assigned_shift},['end_time'])
    else:
        shift_in_time = ' '
        shift_out_time = ' '
    if frappe.db.exists('Attendance',{'employee':emp,'attendance_date':att_date,'docstatus':['!=',2]}):
        if frappe.db.get_value('Attendance',{'employee':emp,'docstatus':['!=',2],'attendance_date':att_date},['in_time']):
            first_in_time = frappe.db.get_value('Attendance',{'docstatus':['!=',2],'employee':emp,'attendance_date':att_date},['in_time'])
        else:
            first_in_time = ' ' 
        if frappe.db.get_value('Attendance',{'employee':emp,'docstatus':['!=',2],'attendance_date':att_date},['out_time']):
            last_out_time = frappe.db.get_value('Attendance',{'docstatus':['!=',2],'employee':emp,'attendance_date':att_date},['out_time'])  
        else:
            last_out_time = ' '
        if frappe.db.get_value('Attendance',{'employee':emp,'docstatus':['!=',2],'attendance_date':att_date},['shift']):
            attendance_shift = frappe.db.get_value('Attendance',{'docstatus':['!=',2],'employee':emp,'attendance_date':att_date},['shift'])   
        else:
            attendance_shift = ' '
        attendance_marked = frappe.db.get_value('Attendance',{'docstatus':['!=',2],'employee':emp,'attendance_date':att_date},['name'])
        data.update({
            'assigned_shift':assigned_shift or ' ',
            'shift_in_time':shift_in_time or '00:00:00',
            'shift_out_time':shift_out_time or '00:00:00',
            'attendance_shift':attendance_shift or ' ',
            'first_in_time':first_in_time,
            'last_out_time':last_out_time,
            'attendance_marked':attendance_marked 
        })
        datalist.append(data.copy())
        return datalist	 
    else:
        frappe.throw(_("Attendance not Marked"))


@frappe.whitelist()
def validate_attendance_regularize_duplication(employee,att_date):
    exisiting=frappe.db.exists("Attendance Regularize",{'employee':employee,'attendance_date':att_date,'docstatus':['!=',2]})
    if exisiting:
        return "Already Applied"
    

                