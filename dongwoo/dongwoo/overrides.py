from email import message
import frappe
from frappe import _
import datetime, math
from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip
from hrms.hr.doctype.shift_assignment.shift_assignment import ShiftAssignment
from itertools import chain
from hrms.hr.utils import get_holiday_dates_for_employee
from dongwoo.mark_attendance import check_nhfh
from hrms.hr.utils import get_holidays_for_employee
from frappe.utils import cstr, add_days, date_diff,format_datetime,ceil,flt
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime, format_date,get_time)
from datetime import time,timedelta
from frappe.utils import getdate
class CustomSalarySlip(SalarySlip):

    def get_payment_days(self, joining_date, relieving_date, include_holidays_in_total_working_days):
        if not joining_date:
            joining_date, relieving_date = frappe.get_cached_value(
                "Employee", self.employee, ["date_of_joining", "relieving_date"]
            )

        start_date = getdate(self.start_date)
        if joining_date:
            if getdate(self.start_date) <= joining_date <= getdate(self.end_date):
                start_date = joining_date
            elif joining_date > getdate(self.end_date):
                return

        end_date = getdate(self.end_date)
        if relieving_date:
            if getdate(self.start_date) <= relieving_date <= getdate(self.end_date):
                end_date = relieving_date
            elif relieving_date < getdate(self.start_date):
                frappe.throw(_("Employee relieved on {0} must be set as 'Left'").format(relieving_date))

        payment_days = date_diff(end_date, start_date) + 1

        if not cint(include_holidays_in_total_working_days):
            ww_count = frappe.db.count("Shift Assignment",{"employee":self.employee,"shift_type":"WW","start_date": ["between", [self.start_date,self.end_date]]})
            holidays = self.get_holidays_for_employee(start_date, end_date) 
            payment_days -= len(holidays) + ww_count
        frappe.errprint("payment_days")
        frappe.errprint(payment_days)
        return payment_days

    def get_holidays_for_employee(self, start_date, end_date):
        
        return get_holiday_dates_for_employee(self.employee, start_date, end_date)

    def get_date_details(self):
        # employee = frappe.get_doc("Employee", self.employee)

        # relieving_date = employee.relieving_date

        # end_date = self.end_date
        # frappe.errprint(relieving_date)
        # frappe.errprint(end_date)
        # if employee.relieving_date and getdate(employee.relieving_date) < getdate(self.end_date):
        #     end_date = getdate(employee.relieving_date)
        #     attendance_list = frappe.get_all(
        #         "Attendance",
        #         filters={
        #             "employee": self.employee,
        #             "attendance_date": ["between", [self.start_date, end_date]],
        #             "docstatus": 1
        #         },
        #         fields=["attendance_date", "status"]
        #     )
        #     payment_days = 0

        #     for att in attendance_list:
        #         if att.status == "Present":
        #             payment_days += 1
        #         elif att.status == "Half Day":
        #             payment_days += 0.5

        #     self.payment_days = payment_days
        #     frappe.errprint(payment_days)

        if self.employee_type == 'Staff':
            ot_hrs = frappe.db.sql("""
                SELECT SUM(overtime_hours) AS ot_total 
                FROM `tabAttendance`
                WHERE attendance_date BETWEEN %s AND %s 
                AND employee = %s 
                AND docstatus = 1
            """, (self.start_date, self.end_date, self.employee), as_dict=True)
            if ot_hrs and len(ot_hrs) > 0:
                self.ot_hours=ot_hrs[0].ot_total or 0
            else:
                self.ot_hours=0
                
           
        # elif self.employee_type == 'Worker' or self.employee_type == "D . Trainee" or self.employee_type == 'Contract Employee':
        # 	ot_hrs = frappe.db.sql("""
        # 	SELECT SUM(total_hours) AS ot_total 
        # 	FROM `tabOvertime Request`
        # 	WHERE ot_date BETWEEN %s AND %s 
        #     AND is_considered_as != 'Compensatory Off'
        # 	AND employee = %s 
        # 	AND docstatus = 1
        # 	""", (self.start_date, self.end_date, self.employee), as_dict=True)
        # 	if ot_hrs and len(ot_hrs) > 0:
        # 		self.ot_hours = ot_hrs[0].ot_total or 0
        # 	else:
        # 		self.ot_hours = 0
        
        elif self.employee_type in ['Worker', 'D . Trainee', 'Contract Employee','GET','NAPS']:
            dates = get_dates(self.start_date, self.end_date)
            overtime_hours = 0
            for date in dates:
                if frappe.db.exists('Overtime Request', {
                    'ot_date': date,
                    'is_considered_as': 'Overtime',
                    'employee': self.employee,
                    'docstatus': 1
                }):
                    ot_hrs = frappe.db.sql("""
                        SELECT SUM(total_hours) AS ot_total 
                        FROM `tabOvertime Request`
                        WHERE ot_date BETWEEN %s AND %s 
                        AND is_considered_as != 'Compensatory Off'
                        AND employee = %s 
                        AND docstatus = 1
                    """, (date, date, self.employee), as_dict=True)

                    overtime_hours += ot_hrs[0].ot_total if ot_hrs and ot_hrs[0].ot_total else 0

                else:
                    att_hrs = frappe.db.sql("""
                        SELECT SUM(overtime_hours) AS ot_total 
                        FROM `tabAttendance`
                        WHERE attendance_date BETWEEN %s AND %s 
                        AND employee = %s 
                        AND docstatus != 2
                    """, (date, date, self.employee), as_dict=True)

                    overtime_hours += att_hrs[0].ot_total if att_hrs and att_hrs[0].ot_total else 0

            self.ot_hours = overtime_hours

        else:
            self.ot_hours = 0
        if self.employee_type=='Contract Employee':
            fhot=0
            fh_att=frappe.db.get_all("Attendance",{"attendance_date":('Between',(self.start_date, self.end_date)),'employee':self.employee,'docstatus':['!=',2]},['attendance_date','overtime_hours'])
            for fh in fh_att:
                is_fh1=check_nhfh(fh.attendance_date,self.employee)
                if is_fh1 is None:
                    is_fh = 0
                else:
                    is_fh = is_fh1
                if is_fh1=='FH':
                    fhot+=fh.overtime_hours
            self.fh_ot_hours=fhot
            pre_count=frappe.db.count("Attendance",{"attendance_date":('Between',(self.start_date, self.end_date)),'employee':self.employee,'docstatus':['!=',2],'status':'Present'})
            half=frappe.db.count("Attendance",{"attendance_date":('Between',(self.start_date, self.end_date)),'employee':self.employee,'docstatus':['!=',2],'status':'Half Day'})
            if half > 0:
                half=half*0.5
            else:
                half=0
            tot_pre_count=pre_count+half
            self.present_days_=tot_pre_count
            ww_count=frappe.db.count("Attendance",{"attendance_date":('Between',(self.start_date, self.end_date)),'employee':self.employee,'docstatus':['!=',2],'shift':'WW'})
            # self.week_off_count_=ww_count
            holiday_list = frappe.db.get_value("Employee", self.employee, "holiday_list")

            nhfh_count = frappe.db.count("Holiday", {
                "parent": holiday_list,
                "parenttype": "Holiday List",
                "holiday_date": ["between", [self.start_date, self.end_date]]
            })
            self.week_off_count_ = ww_count + nhfh_count
            
            total_working_days = self.total_working_days or 0
            self.present_days_for_month = total_working_days - self.week_off_count_
            # self.present_days_for_month = self.total_working_days-self.week_off_count_

        if self.employee_type=="Worker" or self.employee_type=="D . Trainee" or self.employee_type=="NAPS" or self.employee_type=="GET":
            # if self.is_new():
            b_pre = frappe.db.count("Attendance", {
                "employee": self.employee,
                "attendance_date": ['between', (self.start_date, self.end_date)],
                "b_allowance": 1,
                "docstatus": ['!=',2]
            })
            c_pre = frappe.db.count("Attendance", {
                "employee": self.employee,
                "attendance_date": ['between', (self.start_date, self.end_date)],
                "c_allowance": 1,
                "docstatus": ['!=',2]
            })
            
            self.custom_no_of_2_shift=b_pre
            self.custom_no_of_3_shift=c_pre
            # self.save(ignore_permissions=True)
            if self.payment_days==self.total_working_days:
                if self.employee_type=="Worker":
                    l_count = frappe.db.count("Attendance", {
                    "employee": self.employee,
                    "attendance_date": ('between', (self.start_date, self.end_date)),
                    "leave_application": ('!=',''),
                    "docstatus": 1
                    })
                    if l_count<1:
                        self.att_bonus=800
                    else:
                        self.att_bonus=0
                if self.employee_type=="D . Trainee" or self.employee_type=="GET" or self.employee_type == "NAPS":
                    l_count = frappe.db.count("Attendance", {
                    "employee": self.employee,
                    "attendance_date": ('between', (self.start_date, self.end_date)),
                    "leave_application": ('!=',''),
                    "docstatus": 1
                    })
                    if l_count<1:
                        self.att_bonus=800
                    else:
                        if l_count==1:
                            l_name = frappe.db.get_value("Attendance", {
                            "employee": self.employee,
                            "leave_application": ('!=',''),
                            "docstatus": 1},['leave_application'])
                            ltype=frappe.db.get_value("Leave Application",{'name':l_name},['leave_type'])
                            
                            if ltype=="Casual Leave (CL)":
                                self.att_bonus=500
                            else:
                                self.att_bonus=0     
                        else:
                            self.att_bonus=0 
                if self.employee_type == "NAPS":
                    l_count = frappe.db.count("Attendance", {
                        "employee": self.employee,
                        "attendance_date": ('between', (self.start_date, self.end_date)),
                        "leave_application": ('!=',''),
                        "leave_type":"Casual Leave (CL)",
                        "docstatus": 1
                        })
                    if l_count<1:
                        self.att_bonus=800
                    else:
                        if l_count==1:
                            l_name = frappe.db.get_value("Attendance", {
                            "employee": self.employee,
                            "leave_application": ('!=',''),
                            "docstatus": 1},['leave_application'])
                            ltype=frappe.db.get_value("Leave Application",{'name':l_name},['leave_type'])
                            
                            if ltype=="Casual Leave (CL)":
                                self.att_bonus=500
                            else:
                                self.att_bonus=0     
                        else:
                            self.att_bonus=0 
            else:
                self.att_bonus=0

        if self.employee_type=="Staff":
            special_amt = frappe.db.sql("""
                SELECT SUM(amount) AS amt_total 
                FROM `tabSpecial Allowance`
                WHERE working_date BETWEEN %s AND %s 
                AND employee = %s 
                AND docstatus = 1
            """, (self.start_date, self.end_date, self.employee), as_dict=True)
            if special_amt and len(special_amt) > 0:
                self.special_all=special_amt[0].amt_total or 0
            else:
                self.special_all=0
        if self.employee_type:
            self.festival_allowance=0
            holiday_dates = get_holiday_dates_for_employee(self.employee, self.start_date, self.end_date)
            for h in holiday_dates:
                if self.employee_type=='Staff' or self.employee_type=="Worker" :
                    if frappe.db.exists("Attendance", {"attendance_date": h, "working_hours": [">=", 7], "docstatus": ["!=", 2], "employee": self.employee}):
                        check_hh=check_holiday(h,self.employee)
                        if check_hh:
                            if self.employee_type=='Staff':
                                # frappe.errprint(h)
                                if check_hh=='F':
                                    self.festival_allowance+=1000
                                elif check_hh=='N':
                                    self.festival_allowance+=250
                                else:
                                    self.festival_allowance+=0
                            elif self.employee_type=="Worker" :
                                if check_hh=='F':
                                    self.festival_allowance+=300
                                elif check_hh=='N':
                                    self.festival_allowance+=200
                                else:
                                    self.festival_allowance+=0
                # elif self.employee_type=='Contract Employee':
                else:
                    if frappe.db.exists("Attendance", {"attendance_date": h, "status": 'Present',"overtime_hours": [">=", 7], "docstatus": ["!=", 2], "employee": self.employee}):
                        check_hh=check_holiday(h,self.employee)
                        if check_hh:
                            if self.employee_type=='Contract Employee':
                                if check_hh=='F' or check_hh=='N':
                                    self.festival_allowance+=150
                            if self.employee_type=="D . Trainee" or self.employee_type=="GET" or self.employee_type=="NAPS":
                                if check_hh=='F':
                                    self.festival_allowance+=300
                                elif check_hh=='N':
                                    self.festival_allowance+=200
                                else:
                                    self.festival_allowance+=0

def check_holiday(date, emp):
    holiday_list = frappe.db.get_value('Employee', {'name': emp}, 'holiday_list')
    
    holiday = frappe.db.sql("""
        SELECT `tabHoliday`.holiday_date, `tabHoliday`.weekly_off, `tabHoliday`.festival_holiday, `tabHoliday`.national_holiday
        FROM `tabHoliday List`
        LEFT JOIN `tabHoliday` ON `tabHoliday`.parent = `tabHoliday List`.name
        WHERE `tabHoliday List`.name = %s AND holiday_date = %s
    """, (holiday_list, date), as_dict=True)
    
    if holiday:
        holiday = holiday[0]  
        doj = frappe.db.get_value("Employee", {'name': emp}, "date_of_joining")        
        if doj and holiday.holiday_date and doj < holiday.holiday_date:
            if holiday.festival_holiday == 1:
                return "F"  
            elif holiday.national_holiday == 1:
                return "N"
            else:
                return "W"  
    return None 

# class CustomShiftAssignment(ShiftAssignment):
#     def on_submit(self):
#         if self.shift_type!='WW':
#             if frappe.db.exists("Attendance", {"attendance_date": self.start_date, "employee": self.employee, "docstatus": ["!=",2]}):
#                 att=frappe.db.get_value("Attendance", {"attendance_date": self.start_date, "employee": self.employee, "docstatus": ["!=",2]},['name'])
#                 frappe.db.set_value("Attendance",att,'actual_shift',self.shift_type)
#             else:
#                 att = frappe.new_doc("Attendance")
#                 att.employee = self.employee
#                 att.actual_shift =self.shift_type
#                 att.attendance_date = self.start_date
#                 att.status = 'Absent'
#                 att.total_working_hours = '00:00:00'
#                 att.total_extra_hours = '00:00:00'
#                 att.total_overtime_hours = '00:00:00'
#                 att.save()
        

@frappe.whitelist()
def get_children(parent=None, company=None, exclude_node=None):
    filters = [["status", "!=", "Left"]]
    if company and company != "All Companies":
        filters.append(["company", "=", company])
        filters.append(["employee_type", "!=", "Contract Employee"])

    if parent and company and parent != company:
        filters.append(["reports_to", "=", parent])
    else:
        filters.append(["reports_to", "=", ""])

    if exclude_node:
        filters.append(["name", "!=", exclude_node])

    employees = frappe.get_list(
        "Employee",
        fields=["employee_name as name", "name as id", "reports_to", "image", "designation as title"],
        filters=filters,
        order_by="name",
    )

    for employee in employees:
        is_expandable = frappe.db.count("Employee", filters={"reports_to": employee.get("id")})
        employee.connections = get_connections(employee.id)
        employee.expandable = 1 if is_expandable else 0

    return employees


def get_connections(employee):
    num_connections = 0

    nodes_to_expand = frappe.get_list("Employee", filters=[["reports_to", "=", employee]])
    num_connections += len(nodes_to_expand)

    while nodes_to_expand:
        parent = nodes_to_expand.pop(0)
        descendants = frappe.get_list("Employee", filters=[["reports_to", "=", parent.name]])
        num_connections += len(descendants)
        nodes_to_expand.extend(descendants)

    return num_connections

@frappe.whitelist()
def get_dates(from_date ,to_date):
	no_of_days = date_diff(add_days(to_date, 1), from_date)
	dates = [add_days(from_date, i) for i in range(0, no_of_days)]
	return dates