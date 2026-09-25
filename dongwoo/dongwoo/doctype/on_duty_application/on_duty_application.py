# Copyright (c) 2023, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from dongwoo.mark_attendance import mark_wh_ot_with_employee
from dongwoo.mark_attendance import mark_att_present_with_employee
from frappe.utils import (getdate, cint, add_months, date_diff, add_days)
class OnDutyApplication(Document):
    def after_insert(self):
        name=self.shift
        session=self.session
        shift_doc = frappe.get_doc("Shift Type", name)
    
        if shift_doc:
            # Calculate hours and minutes from timedelta objects
            start_hours, start_minutes = divmod(shift_doc.start_time.seconds // 60, 60)
            end_hours, end_minutes = divmod(shift_doc.end_time.seconds // 60, 60)
            
            # Convert hours and minutes to strings and format the time data
            start_time = timedelta(hours=start_hours, minutes=start_minutes)
            end_time = timedelta(hours=end_hours, minutes=end_minutes)
            
            # If session is Full Day, return start time and end time directly
            if session == "Full Day":
                start_time_str = '{:02}:{:02}'.format(start_hours, start_minutes)
                end_time_str = '{:02}:{:02}'.format(end_hours, end_minutes)
                self.from_time=start_time_str
                self.to_time=end_time_str
            
            # If session is First Half, calculate mid time between start and end time
            elif session == "First Half":
                mid_time = (start_time + (end_time - start_time) / 2)
                mid_hours, mid_minutes = divmod(mid_time.seconds // 60, 60)
                start_time_str = '{:02}:{:02}'.format(start_hours, start_minutes)
                end_time_str = '{:02}:{:02}'.format(mid_hours, mid_minutes)
                self.from_time=start_time_str
                self.to_time=end_time_str
            
            # If session is Second Half, calculate mid time between start and end time
            elif session == "Second Half":
                mid_time = (start_time + (end_time - start_time) / 2)
                mid_hours, mid_minutes = divmod(mid_time.seconds // 60, 60)
                start_time_str = '{:02}:{:02}'.format(mid_hours, mid_minutes)
                end_time_str = '{:02}:{:02}'.format(end_hours, end_minutes)
                self.from_time=start_time_str
                self.to_time=end_time_str
        return {}
    def validate(self):
        emp_status = frappe.db.get_value('Employee',{'name':self.employee},['status'])
        if emp_status and emp_status != 'Active':
            frappe.throw('On Duty Application is only allowed for Active Employees')
        name=self.shift
        session=self.session
        shift_doc = frappe.get_doc("Shift Type", name)
    
        if shift_doc:
            # Calculate hours and minutes from timedelta objects
            start_hours, start_minutes = divmod(shift_doc.start_time.seconds // 60, 60)
            end_hours, end_minutes = divmod(shift_doc.end_time.seconds // 60, 60)
            
            # Convert hours and minutes to strings and format the time data
            start_time = timedelta(hours=start_hours, minutes=start_minutes)
            end_time = timedelta(hours=end_hours, minutes=end_minutes)
            
            # If session is Full Day, return start time and end time directly
            if session == "Full Day":
                start_time_str = '{:02}:{:02}'.format(start_hours, start_minutes)
                end_time_str = '{:02}:{:02}'.format(end_hours, end_minutes)
                self.from_time=start_time_str
                self.to_time=end_time_str
            
            # If session is First Half, calculate mid time between start and end time
            elif session == "First Half":
                mid_time = (start_time + (end_time - start_time) / 2)
                mid_hours, mid_minutes = divmod(mid_time.seconds // 60, 60)
                start_time_str = '{:02}:{:02}'.format(start_hours, start_minutes)
                end_time_str = '{:02}:{:02}'.format(mid_hours, mid_minutes)
                self.from_time=start_time_str
                self.to_time=end_time_str
            
            # If session is Second Half, calculate mid time between start and end time
            elif session == "Second Half":
                mid_time = (start_time + (end_time - start_time) / 2)
                mid_hours, mid_minutes = divmod(mid_time.seconds // 60, 60)
                start_time_str = '{:02}:{:02}'.format(mid_hours, mid_minutes)
                end_time_str = '{:02}:{:02}'.format(end_hours, end_minutes)
                self.from_time=start_time_str
                self.to_time=end_time_str
        if self.session=='Flexible':
            if self.od_duration==0:
                frappe.throw("From time should be less than to time. Kindly check again")
    def on_submit(self):
        # set the od application name in attendance
        if self.shift=='C':
            shiftdate = add_days(self.od_date,-1)
        else:
            shiftdate=self.od_date
        if frappe.db.exists("Attendance",{"attendance_date":shiftdate,'employee':self.employee,'docstatus':("!=",2)}):
            att=frappe.get_doc("Attendance",{"attendance_date":shiftdate,'employee':self.employee,'docstatus':("!=",2)})
            frappe.db.set_value("Attendance",att.name,"on_duty_application",self.name)
            frappe.db.set_value("Attendance",att.name,"shift",self.shift)
            if self.session=='Flexible':
                frappe.db.set_value("Attendance",att.name,"session",self.session)
                frappe.db.set_value("Attendance",att.name,"from_time",self.ffrom_time)
                frappe.db.set_value("Attendance",att.name,"to_time",self.tto_time)
            else:
                # frappe.db.set_value("Attendance",att.name,"session",self.session)
                frappe.db.set_value("Attendance",att.name,"session_from_time",self.from_time)
                frappe.db.set_value("Attendance",att.name,"session_to_time",self.to_time)
            nextdate = add_days(self.od_date,1)
            mark_wh_ot_with_employee(shiftdate,self.od_date,self.employee)
            mark_att_present_with_employee(shiftdate,self.od_date,self.employee)
    def on_cancel(self):
        # remove the od application from attendance
        if self.shift=='C':
            shiftdate = add_days(self.od_date,-1)
        else:
            shiftdate=self.od_date
        if frappe.db.exists("Attendance",{"attendance_date":shiftdate,'employee':self.employee,'docstatus':("!=",2)}):
            att=frappe.get_doc("Attendance",{"attendance_date":shiftdate,'employee':self.employee,'docstatus':("!=",2)})
            frappe.db.set_value("Attendance",att.name,"on_duty_application",'')
            frappe.db.set_value("Attendance",att.name,"shift",self.shift)
            frappe.db.set_value("Attendance",att.name,"session_from_time","00:00:00")
            frappe.db.set_value("Attendance",att.name,"session_to_time","00:00:00")
            frappe.db.set_value("Attendance",att.name,"session",'')
            frappe.db.set_value("Attendance",att.name,"from_time",None)
            frappe.db.set_value("Attendance",att.name,"to_time",None)
            nextdate = add_days(self.od_date,1)
            if att.in_time and att.out_time:
                mark_wh_ot_with_employee(self.od_date,shiftdate,self.employee)  
            else:
                frappe.db.set_value("Attendance",att.name,"status",'Absent')
                frappe.db.set_value('Attendance', att.name, 'total_working_hours', "00:00:00")
                frappe.db.set_value('Attendance', att.name, 'working_hours', "0.0")
                frappe.db.set_value('Attendance', att.name, 'extra_hours', "0.0")
                frappe.db.set_value('Attendance', att.name, 'total_extra_hours', "00:00:00")
                frappe.db.set_value('Attendance', att.name, 'total_overtime_hours', "00:00:00")
                frappe.db.set_value('Attendance', att.name, 'overtime_hours', "0.0")    
@frappe.whitelist()
def get_employee_approvers(employee_id):
    # Fetch Employee document based on the selected employee_id
    employee_doc = frappe.get_doc('Employee', employee_id)

    # Extract approver details from the Employee document
    level_1_approver = employee_doc.get('level_1_approver')
    level_2_approver = employee_doc.get('level_2_approver')
    level_3_approver = employee_doc.get('level_3_approver')

    # Return a dictionary with the required values
    return {
        'level_1_approver': level_1_approver,
        'level_2_approver': level_2_approver,
        'level_3_approver': level_3_approver
    }

import frappe
from datetime import timedelta

@frappe.whitelist()
def get_shift_time(name, session):
    # Fetch the "Start Time" and "End Time" values based on the selected "Shift Type"
    shift_doc = frappe.get_doc("Shift Type", name)
    
    if shift_doc:
        # Calculate hours and minutes from timedelta objects
        start_hours, start_minutes = divmod(shift_doc.start_time.seconds // 60, 60)
        end_hours, end_minutes = divmod(shift_doc.end_time.seconds // 60, 60)
        
        # Convert hours and minutes to strings and format the time data
        start_time = timedelta(hours=start_hours, minutes=start_minutes)
        end_time = timedelta(hours=end_hours, minutes=end_minutes)
        
        # If session is Full Day, return start time and end time directly
        if session == "Full Day":
            start_time_str = frappe.db.get_value("Shift Type",{'name':name},['start_time'])
            end_time_str = frappe.db.get_value("Shift Type",{'name':name},['end_time'])
            return {
                "start_time": start_time_str,
                "end_time": end_time_str
            }
        
        # If session is First Half, calculate mid time between start and end time
        elif session == "First Half":
            if name=='B':
                return {
                "start_time": '17:00:00',
                "end_time": '21:15:00'
                }
            else:
                mid_time = (start_time + (end_time - start_time) / 2)
                mid_hours, mid_minutes = divmod(mid_time.seconds // 60, 60)
                start_time_str = '{:02}:{:02}'.format(start_hours, start_minutes)
                end_time_str = '{:02}:{:02}'.format(mid_hours, mid_minutes)
                return {
                    "start_time": start_time_str,
                    "end_time": end_time_str
                }
        
        # If session is Second Half, calculate mid time between start and end time
        elif session == "Second Half":
            if name=='B':
                return {
                "start_time": '21:15:00',
                "end_time": '01:30:00'
                }
            else:
                mid_time = (start_time + (end_time - start_time) / 2)
                mid_hours, mid_minutes = divmod(mid_time.seconds // 60, 60)
                start_time_str = '{:02}:{:02}'.format(mid_hours, mid_minutes)
                end_time_str = '{:02}:{:02}'.format(end_hours, end_minutes)
                return {
                    "start_time": start_time_str,
                    "end_time": end_time_str
                }

    return {}
@frappe.whitelist()
def get_employee_status(employee):
    emp_status = frappe.db.get_value('Employee',{'name':employee},['status'])
    return emp_status
