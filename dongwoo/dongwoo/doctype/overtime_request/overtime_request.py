# Copyright (c) 2023, TEAMPRO and contributors
# For license information, please see license.txt
import frappe
from datetime import datetime , timedelta
from frappe import throw,_
from frappe.utils import cstr, add_days, date_diff, getdate, format_date
import frappe
from frappe.model.document import Document
from frappe.utils import date_diff
from datetime import datetime, time
from datetime import date,datetime,timedelta
import calendar
from frappe.utils import getdate, add_days, date_diff
from dongwoo.mark_attendance import check_holiday

from frappe.utils import (
    add_days,
    ceil,
    cint,
    comma_and,
    flt,
    get_link_to_form,
    getdate,
    now_datetime,
    datetime,get_first_day,get_last_day,
    nowdate,
    today,
)
class OvertimeRequest(Document):
    # def after_insert(self):
    #     ret=get_attendance_values(self.employee,self.ot_date)
    #     if ret!='No':
    #         frappe.db.set_value("Overtime Request",self.name,'shift',ret['shift'])
    #         frappe.db.set_value("Overtime Request",self.name,'total_hour',ret['total_working_hours'])
    def on_cancel(self):
        if self.is_considered_as=='Compensatory Off':
            to_date=add_days(self.ot_date,30)
            to_date=getdate(to_date)
            leave_allocation  = frappe.db.sql(
                    """
                    SELECT
                        name
                    FROM `tabLeave Allocation`
                    WHERE employee=%(employee)s AND leave_type='Compensatory Off'
                        AND docstatus=1
                        AND (from_date between %(from_date)s AND %(to_date)s
                            OR to_date between %(from_date)s AND %(to_date)s
                            OR (from_date < %(from_date)s AND to_date > %(to_date)s))
                """,
                    {"from_date": self.ot_date, "to_date": to_date, "employee": self.employee},
                    as_dict=1,
                )
            if leave_allocation:
                hh=check_holiday(self.ot_date,self.employee) 
                if hh:
                    if self.shift=='C':
                        if self.total_hours >= 7 and self.total_hours < 14:
                            leave=1
                        elif self.total_hours >= 14 and self.total_hours < 21:
                            leave=2
                        elif self.total_hours >= 21:
                            leave=3
                        else:
                            leave=0
                    else:
                        if self.total_hours >= 8 and self.total_hours < 16:
                            leave=1
                        elif self.total_hours >= 16 and self.total_hours < 24:
                            leave=2
                        elif self.total_hours >= 24:
                            leave=3
                        else:
                            leave=0
                else:
                    if self.shift=='B':
                        if self.total_hours >= 7 and self.total_hours < 15:
                            leave=1
                        elif self.total_hours >= 15 and self.total_hours < 23:
                            leave=2
                        elif self.total_hours >= 23:
                            leave=3
                        else:
                            leave=0
                    else:
                        if self.total_hours >= 8 and self.total_hours < 16:
                            leave=1
                        elif self.total_hours >= 16 and self.total_hours < 24:
                            leave=2
                        elif self.total_hours >= 24:
                            leave=3
                        else:
                            leave=0
                la_name = leave_allocation[0].get('name')
                la = frappe.get_doc('Leave Allocation',la_name)
                la.new_leaves_allocated-= leave
                la.total_leaves_allocated-= leave
                la.save(ignore_permissions=True)
                frappe.db.commit()
                # frappe.db.set_value("Leave Allocation",la_name,'new_leaves_allocated',la.new_leaves_allocated-leave)
                # frappe.db.set_value("Leave Allocation",la_name,'total_leaves_allocated',la.total_leaves_allocated-leave)
    def validate(self):
        if frappe.db.exists("Overtime Request",{'employee':self.employee,'ot_date':self.ot_date,'docstatus':['!=',2],'name':['!=',self.name]}):
            frappe.throw("Already another request found for the same date")
        if self.total_hours==0:
            frappe.throw("Insufficient OT hours to raise request")
        if self.employee_type=='Worker':
            gross=frappe.db.get_value('Employee',{'name':self.name},['actual_gross'])
            if self.is_considered_as=='' or self.is_considered_as=='Overtime':
                if gross:
                    self.overtime_amount=(gross/209)*2*self.total_hours
        if self.docstatus==0:
            otdate = getdate(self.ot_date)
            year = otdate.year
            month = otdate.month
            total_days_in_month = calendar.monthrange(year, month)[1]
            if self.employee_type=='Worker':
                gross=frappe.db.get_value('Employee',{'name':self.employee},['actual_gross'])
                if self.is_considered_as=='' or self.is_considered_as=='Overtime':
                    if gross:
                        self.overtime_amount=(gross/209)*2*self.total_hours
                
            if self.employee_type=='Contract Employee':
                gross=frappe.db.get_value('Employee',{'name':self.employee},['revised_gross'])
                if self.is_considered_as=='' or self.is_considered_as=='Overtime':
                    if gross:
                        self.overtime_amount=(gross/8)*self.total_hours  
            if self.employee_type=='D . Trainee':
                gross=frappe.db.get_value('Employee',{'name':self.employee},['actual_gross'])
                if self.is_considered_as=='' or self.is_considered_as=='Overtime':
                    if gross:
                        self.overtime_amount=((gross/total_days_in_month)/8)*2*self.total_hours

    def on_submit(self):
        if self.is_considered_as == 'Compensatory Off':
            to_date=add_days(self.ot_date,90)
            to_date=getdate(to_date)
            employee=frappe.get_all('Employee',{'status':'Active'},['*'])
            leave_allocation  = frappe.db.sql(
                """
                SELECT
                    name
                FROM `tabLeave Allocation`
                WHERE employee=%(employee)s AND leave_type='Compensatory Off'
                    AND docstatus=1
                    AND (from_date between %(from_date)s AND %(to_date)s
                        OR to_date between %(from_date)s AND %(to_date)s
                        OR (from_date < %(from_date)s AND to_date > %(to_date)s))
            """,
                {"from_date": self.ot_date, "to_date": to_date, "employee": self.employee},
                as_dict=1,
            )
            
            if leave_allocation:
                hh=check_holiday(self.ot_date,self.employee) 
                if hh:
                    if self.shift=='C':
                        if self.total_hours >= 7 and self.total_hours < 14:
                            leave=1
                        elif self.total_hours >= 14 and self.total_hours < 21:
                            leave=2
                        elif self.total_hours >= 21:
                            leave=3
                        else:
                            leave=0
                    else:
                        if self.total_hours >= 8 and self.total_hours < 16:
                            leave=1
                        elif self.total_hours >= 16 and self.total_hours < 24:
                            leave=2
                        elif self.total_hours >= 24:
                            leave=3
                        else:
                            leave=0
                else:
                    if self.shift=='B':
                        if self.total_hours >= 7 and self.total_hours < 15:
                            leave=1
                        elif self.total_hours >= 15 and self.total_hours < 23:
                            leave=2
                        elif self.total_hours >= 23:
                            leave=3
                        else:
                            leave=0
                    else:
                        if self.total_hours >= 8 and self.total_hours < 16:
                            leave=1
                        elif self.total_hours >= 16 and self.total_hours < 24:
                            leave=2
                        elif self.total_hours >= 24:
                            leave=3
                        else:
                            leave=0



                la_name = leave_allocation[0].get('name')
                la = frappe.get_doc('Leave Allocation',la_name)
                if getdate(la.to_date) < to_date:
                    la.to_date=to_date
                if getdate(la.from_date) > getdate(self.ot_date):
                    date_difference = date_diff(self.ot_date,la.from_date)
                    from_date =self.ot_date
                    from_date = add_days(from_date,date_difference) 
                    la.from_date=from_date
                la.new_leaves_allocated+= leave
                la.total_leaves_allocated+= leave
                la.save(ignore_permissions=True)
                frappe.db.commit()
            else:
                hh=check_holiday(self.ot_date,self.employee) 
                if hh:
                    if self.shift=='C':
                        if self.total_hours >= 7 and self.total_hours < 14:
                            leave=1
                        elif self.total_hours >= 14 and self.total_hours < 21:
                            leave=2
                        elif self.total_hours >= 21:
                            leave=3
                        else:
                            leave=0
                    else:
                        if self.total_hours >= 8 and self.total_hours < 16:
                            leave=1
                        elif self.total_hours >= 16 and self.total_hours < 24:
                            leave=2
                        elif self.total_hours >= 24:
                            leave=3
                        else:
                            leave=0
                else:
                    if self.shift=='B':
                        if self.total_hours >= 7 and self.total_hours < 15:
                            leave=1
                        elif self.total_hours >= 15 and self.total_hours < 23:
                            leave=2
                        elif self.total_hours >= 23:
                            leave=3
                        else:
                            leave=0
                    else:
                        if self.total_hours >= 8 and self.total_hours < 16:
                            leave=1
                        elif self.total_hours >= 16 and self.total_hours < 24:
                            leave=2
                        elif self.total_hours >= 24:
                            leave=3
                        else:
                            leave=0
                la=frappe.new_doc('Leave Allocation')
                la.employee=self.employee
                la.leave_type='Compensatory Off'
                la.from_date=self.ot_date
                la.to_date=to_date
                la.new_leaves_allocated=leave
                la.save(ignore_permissions=True)
                frappe.db.commit()
                la.submit()

            
                    
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
                try:
                    out_time = datetime.strptime(out_time, '%Y-%m-%d %H:%M:%S') 
                except ValueError:
                    return {"error": "Invalid datetime format in out_time"}

            out_time_str = out_time.strftime('%H:%M:%S')
            return {
                'shift': attendance_doc[0]['shift'],
                'out_time': out_time_str,
                'total_working_hours': attendance_doc[0]['total_working_hours'],
                'total_overtime_hours': attendance_doc[0]['overtime_hours']
            }
        else:
            return 'No'
    # frappe.errprint()
    else:
        frappe.throw(_('No attendance record found for the specified employee and date.'))
        return 'No'
    
@frappe.whitelist()
def get_start_time(employee, ot_date, shift):
    hh=check_holiday(ot_date,employee) 
    if hh:
        start=frappe.db.get_value("Shift Type",{'name':shift},['start_time'])
        in_time=frappe.db.get_value("Attendance",{'employee':employee,'attendance_date':ot_date,'docstatus':['!=',2]},['in_time'])
        if start:
            if isinstance(start, datetime.timedelta):  # Convert timedelta to time
                start = (datetime.datetime.min + start).time()
        if in_time:
            in_time=in_time.time()
            if in_time>start:
                start=in_time
    else:
        start=frappe.db.get_value("Shift Type",{'name':shift},['end_time'])
    return start

@frappe.whitelist()
def check_for_ot_hrs(employee, ot_date):
    hh=check_holiday(ot_date,employee) 
    ot_hrs=frappe.db.get_value('Attendance',{'employee':employee,'attendance_date':ot_date,'docstatus':['!=',2]},['overtime_hours'])
    shift=frappe.db.get_value('Attendance',{'employee':employee,'attendance_date':ot_date,'docstatus':['!=',2]},['shift'])
    if shift:
        if not hh:    
            if shift=='B':
                if ot_hrs >= 7:
                    return "yes"
                else:
                    return "no"
            else:
                if ot_hrs >= 8:
                    return "yes"
                else:
                    return "no"
        else:
            if shift=='C':
                if ot_hrs>=7:
                    return 'yes'
                else:
                    return 'no'
            else:
                if ot_hrs>=8:
                    return 'yes'
                else:
                    return 'no'
    else:
        frappe.throw("No shift marked on Attendance")