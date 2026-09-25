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

#use to create Employee Checkin from Unregistered Employeed Checkin
@frappe.whitelist()
def get_urc_to_ec(from_date):
    print("HI")
    urc = frappe.db.sql("""select biometric_pin,biometric_time,log_type,locationdevice_id,name from `tabUnregistered Employee Checkin` where date(biometric_time) = '%s' """%(from_date),as_dict=True)
    for uc in urc:
        pin = uc.biometric_pin
        time = uc.biometric_time
        dev = uc.locationdevice_id
        typ = uc.log_type
        nam = uc.name
        if time != "":
            if frappe.db.exists('Employee',{'name':pin}):
                if frappe.db.exists('Employee Checkin',{'biometric_pin':pin,"time":time}):
                    print("HI")
                else:
                    print("HII")
                    ec = frappe.new_doc('Employee Checkin')
                    ec.biometric_pin = pin
                    ec.employee = frappe.db.get_value('Employee',{'biometric_pin':pin},['employee_number'])
                    ec.time = time
                    ec.device_id = dev
                    ec.log_type = typ
                    ec.save(ignore_permissions=True)
                    frappe.db.commit()
                    print("Created")
                    attendance = frappe.db.sql(""" delete from `tabUnregistered Employee Checkin` where name = '%s' """%(nam))
                    print("Deleted")       
            else:
                print("hello")
    return "ok"

#displays the count of Present, Absent, leave, half day and work from home of an employee between the given period
@frappe.whitelist()
def get_summary(emp, year_start_date, year_end_date):
    att = frappe.db.sql("SELECT COUNT(*) AS count FROM `tabAttendance` WHERE employee = '%s' AND docstatus != 2 AND attendance_date BETWEEN '%s' AND '%s'" % (emp, year_start_date, year_end_date), as_dict=True) or [{'count': 0}]
    # frappe.errprint(att[0]['count'])

    att_p = frappe.db.sql("SELECT COUNT(*) AS count FROM `tabAttendance` WHERE employee = '%s' AND docstatus != 2 AND status = 'Present' AND attendance_date BETWEEN '%s' AND '%s'" % (emp, year_start_date, year_end_date), as_dict=True) or [{'count': 0}]
    # frappe.errprint(att_p[0]['count'])

    att_a = frappe.db.sql("SELECT COUNT(*) AS count FROM `tabAttendance` WHERE employee = '%s' AND docstatus != 2 AND status = 'Absent' AND attendance_date BETWEEN '%s' AND '%s'" % (emp, year_start_date, year_end_date), as_dict=True) or [{'count': 0}]
    # frappe.errprint(att_a[0]['count'])

    att_l = frappe.db.sql("SELECT COUNT(*) AS count FROM `tabAttendance` WHERE employee = '%s' AND docstatus != 2 AND status = 'On Leave' AND attendance_date BETWEEN '%s' AND '%s'" % (emp, year_start_date, year_end_date), as_dict=True) or [{'count': 0}]
    # frappe.errprint(att_l[0]['count'])

    att_h = frappe.db.sql("SELECT COUNT(*) AS count FROM `tabAttendance` WHERE employee = '%s' AND docstatus != 2 AND status = 'Half Day' AND attendance_date BETWEEN '%s' AND '%s'" % (emp, year_start_date, year_end_date), as_dict=True) or [{'count': 0}]
    # frappe.errprint(att_h[0]['count'])

    att_w = frappe.db.sql("SELECT COUNT(*) AS count FROM `tabAttendance` WHERE employee = '%s' AND docstatus != 2 AND status = 'Work From Home' AND attendance_date BETWEEN '%s' AND '%s'" % (emp, year_start_date, year_end_date), as_dict=True) or [{'count': 0}]
    # frappe.errprint(att_w[0]['count'])

    if att[0]['count'] != 0:
        p = round((att_p[0]['count'] or 0) / att[0]['count'] * 100, 2)
        # frappe.errprint(p)
        a = round((att_a[0]['count'] or 0) / att[0]['count'] * 100, 2)
        # frappe.errprint(a)
        l = round((att_l[0]['count'] or 0) / att[0]['count'] * 100, 2)
        # frappe.errprint(l)
        h = round((att_h[0]['count'] or 0) / att[0]['count'] * 100, 2)
        # frappe.errprint(h)
        w = round((att_w[0]['count'] or 0) / att[0]['count'] * 100, 2)

        data  = ''
        data = "<table style='width:100%'>"
        data += "<tr><td colspan = 24 style ='text-align:center;border:1px solid black;background-color:#3d316c;color:white;'><b>Overall Summary</b></td></tr>"
        data += "<tr><td colspan = 4 style ='text-align:center;border:1px solid black'><b>Status</b></td><td colspan = 4 style ='text-align:center;border:1px solid black'><b>Present</b></td><td colspan = 4 style ='text-align:center;border:1px solid black'><b>Absent</b></td><td colspan = 4 style ='text-align:center;border:1px solid black'><b>Half Day</b></td><td colspan = 4 style ='text-align:center;border:1px solid black'><b>On Leave</b></td><td colspan = 4 style ='text-align:center;border:1px solid black'><b>Work From Home</b></td></tr>"	
        data += "<tr><td colspan = 4 style ='text-align:center;border:1px solid black'><b>Percentage</b></td><td colspan = 4 style ='text-align:center;border:1px solid black'><b>%s</b></td><td colspan = 4 style ='text-align:center;border:1px solid black'><b>%s</b></td><td colspan = 4 style ='text-align:center;border:1px solid black'><b>%s</b></td><td colspan = 4 style ='text-align:center;border:1px solid black'><b>%s</b></td><td colspan = 4 style ='text-align:center;border:1px solid black'><b>%s</b></td></tr>"%(p,a,l,h,w)	
        data += "</table>"
        return data


#returns the employee number against the employee code
# @frappe.whitelist()
# def employee_list(employee):
#     employee=frappe.get_value("Employee",{"name":employee},["employee_number"])
#     return employee

#returns the employee number against the employee code
# @frappe.whitelist()
# def employee_list_value(employee):
#     employee=frappe.get_value("Employee",{"name":employee},["employee_number"])
#     return employee

#returns the designation in the staffing plan
@frappe.whitelist()
def update_designation(staffing_plan):
    designations = []
    staffing_plan_doc = frappe.get_doc("Staffing Plan", staffing_plan)   
    for detail in staffing_plan_doc.staffing_details:
        designations.append(detail.designation)   
    return designations,staffing_plan

#returns the Staffing Details table value against the parent Staffing Plan
# @frappe.whitelist()
# def update_designation_from_staffing_plan(staffing):
#     staff = frappe.get_all("Staffing Plan Detail",{'parent':staffing},['*'])
#     return staff

#returns the resume in the Job Applicant against the job applicant
# @frappe.whitelist()
# def update_resume(job_applicant):
#     doc=frappe.get_doc("Job Applicant",job_applicant)
#     resume = doc.resume1
#     return resume

#update the service years of all active employees in words
@frappe.whitelist()
def date_of_joining():
    doj =frappe.get_all("Employee",{"status":"Active"},["date_of_joining","service_years_in_dwsi","name"])
    for i in doj:
        if i.date_of_joining:
            if not i.service_years_in_dwsi:
                print(i.date_of_joining)
                date_of_joining = i.date_of_joining 
                today = datetime.now()
                date = date_of_joining
                year = today.year - date.year
                month = today.month - date.month
                day = today.day - date.day

                if day < 0:
                    month -= 1
                    last_month_date = today.replace(day=1) - timedelta(days=1)
                    day += last_month_date.day

                if month < 0:
                    year -= 1
                    month += 12
                value = (f"{year} Years {month} Month {day} Days")
                frappe.db.set_value("Employee",i.name,"service_years_in_dwsi",value) 

#throws an error if reliveing date is not removed for an Active Employee
@frappe.whitelist()
def inactive_employee(doc,method):
    if doc.status=="Active":
        if doc.relieving_date:
            throw(_("Please remove the relieving date for the Active Employee."))
        
@frappe.whitelist()
def employee_type():
    from_date = "2023-11-01"
    to_date = "2023-11-07"
    attendance = frappe.db.sql("""select * from `tabAttendance` where attendance_date between '%s' and '%s' """%(from_date,to_date),as_dict=True)
    # att=frappe.db.get_value("Attendance",{"attendance_date":},["employee_type"])
    for att in attendance:
        print(att.name)
        if att.employee_type=="Worker" or att.employee_type=='D . Trainee':
            workspot=frappe.db.get_value("Employee",{"employee_number":att.employee},['workspot']) or ''
            if workspot:
                print(workspot)
                frappe.db.set_value("Attendance",att.name,'workspot',workspot)
        elif att=='Contract Employee':
            workspot=frappe.db.get_value("Workspot for CL",{"employee":att.employee,"date":att.attendance_date},['workspot']) or ''
            if workspot:
                print(workspot)
                frappe.db.set_value("Attendance",att.name,'workspot',workspot)


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


@frappe.whitelist()
def del_dept():
    dept=frappe.db.get_all("Designation",['*'])
    for d in dept:
        if not frappe.db.exists("Employee",{"designation":d.name}):
            frappe.db.sql("""delete from `tabDesignation` where name = %s""", (d.name),as_dict=True)
        else:
            print("hi")


#returns the current fiscal year	
@frappe.whitelist()
def update_salary():
    current_date = frappe.utils.nowdate()
    frappe.errprint(current_date)
    current_fiscal_year = frappe.get_value("Fiscal Year",{"year_start_date": ("<=", current_date), "year_end_date": (">=", current_date)}, fieldname="name")
    return current_fiscal_year

# Late In and Early Out Penalty creation
@frappe.whitelist()
def attendance_calc(from_date,to_date):
    
    late_count=0
    late_count1=0
    ad=''
    
    employees = frappe.get_all("Employee", {"status": "Active"}, ["*"])
    
    for emp in employees:
        shifts = frappe.get_all('Shift Type', ['*'])
        
        for shift in shifts:
            late_count = frappe.db.sql("""
                SELECT COUNT(name) AS count
                FROM `tabAttendance`
                WHERE
                    employee = %s AND shift = %s
                    AND time(in_time) > %s
                    AND attendance_date BETWEEN %s AND %s
            """, (emp.name, shift.name, shift.start_time, from_date, to_date), as_dict=True)[0].count or 0

            print(f"Employee: {emp.name}, Shift: {shift.name}, shift:{shift.start_time} Late Count: {late_count}")

            late_count1 = frappe.db.sql("""
                SELECT COUNT(name) AS count
                FROM `tabAttendance`
                WHERE
                    employee = %s AND shift = %s
                    AND time(out_time) < %s
                    AND attendance_date BETWEEN %s AND %s
            """, (emp.name, shift.name, shift.start_time, from_date, to_date), as_dict=True)[0].count or 0

            print(f"Employee: {emp.name}, Shift: {shift.name}, shift:{shift.start_time} Late Count: {late_count}")
            if late_count > 0 or late_count1 > 0:
                print('hiii')

                if not frappe.db.exists("Late In and Early Out Penalty", {"employee": emp.name,"from_date":from_date,"to_date":to_date}):
                    ad = frappe.new_doc('Late In And Early Out Penalty')
                    ad.employee = emp.name
                    frappe.errprint(ad.employee)
                    ad.employee_name=emp.first_name
                    ad.designation=emp.designation
                    ad.from_date=from_date
                    ad.to_date=to_date
                    ad.total_no_of_late_in=late_count
                    ad.total_no_of_early_out=late_count1
                    total=late_count+late_count1
                    ad.total_no_of_late_deductions_day=total
                    if total > 0:
                        late=total/2
                        ad.late_penalty_day=late
                    leave=frappe.get_all('Leave Allocation',{'employee_name':emp.first_name},['*'])
                    for j in leave:
                        if j.leave_type not in ["Compensatory Off",'Sick Leave']:
                            ad.append(
                                "leave_deduction",
                                {
                                    "leave_type": j.leave_type,
                                    "leave_balance": j.new_leaves_allocated,
            },
        )

                    
                    frappe.db.commit()
                    ad.save(ignore_permissions=True)
                    frappe.errprint("Late Penalty Created via Additional Salary")
                else:
                    ad = frappe.get_doc('Late In And Early Out Penalty',{"employee": emp.name,"from_date":from_date,"to_date":to_date})
                    ad.employee = emp.name
                    ad.employee_name=emp.first_name
                    ad.designation=emp.designation
                    ad.from_date=from_date
                    ad.to_date=to_date
                    ad.total_no_of_late_in=late_count+ad.total_no_of_late_in
                    ad.total_no_of_early_out=late_count1+ad.total_no_of_early_out
                    total=late_count+late_count1
                    ad.total_no_of_late_deductions_day=total+ad.total_no_of_late_deductions_day
                    if total > 0:
                        late=total/2
                        ad.late_penalty_day=late+ad.late_penalty_day
                    frappe.db.commit()
                    ad.save(ignore_permissions=True)
                    frappe.errprint("Late Penalty Created via Additional Salary")
                # return 'ok'


@frappe.whitelist()
def delete_department():
    dept = frappe.db.sql("""update `tabAttendance` set department = "HK & Garden" where department = "Garden"  """,as_dict = True)
    emptype = frappe.db.sql("""update `tabAttendance` set employee_type = "D . Trainee" where employee_type = "Trainee"  """,as_dict = True)
    # dept = frappe.db.sql("""update `tabEmployee Transfer` where employee = "DWSI1234" """,as_dict = True)
    # dept = frappe.db.sql("""update `tabEmployee Checkin` where employee = "DWSI1234" """,as_dict = True)
    # dept = frappe.db.sql("""update `tabShift Assignment` where employee = "DWSI1234" """,as_dict = True)
    # dept = frappe.db.sql("""update `tabEmployee` where name = "DWSI1234" """,as_dict = True)
    # dept = frappe.db.sql("""update `tabDesignation` where name = "Jr. Engineer" """,as_dict = True)
    # dept = frappe.db.sql("""update `tabLeave Allocation` set department = "IT" where department = "Network"  """,as_dict = True)
    # dept = frappe.db.sql("""update `tabLeave Application` set department = "IT" where department = "Network"  """,as_dict = True)
    # dept = frappe.db.sql("""update `tabSalary Slip` set department = "IT" where department = "Network"  """,as_dict = True)
    


#returns the predefined reason for each leave type
# @frappe.whitelist()
# def get_reasons(leave_type):
#     doc = frappe.get_doc("Leave Type", leave_type)
#     reasons = [reason.pre_defined_reason for reason in doc.pre_defined_reason_table]
#     return reasons

@frappe.whitelist()
def null_attendance():
    checkin = frappe.db.sql("""
        update `tabAttendance`
        set total_overtime_hours = null
        where attendance_date between "2024-04-30" and "2024-04-30"
    """, as_dict=True)
    checkin = frappe.db.sql("""
        update `tabAttendance`
        set in_time = null
        where attendance_date between "2024-04-30" and "2024-04-30"
    """, as_dict=True)
    checkin = frappe.db.sql("""
        update `tabAttendance`
        set out_time = null
        where attendance_date between "2024-04-30" and "2024-04-30"
    """, as_dict=True)
    checkin = frappe.db.sql("""
        update `tabAttendance`
        set out_time = null
        where attendance_date between "2024-04-30" and "2024-04-30"
    """, as_dict=True)
    checkin = frappe.db.sql("""
        update `tabAttendance`
        set total_extra_hours = null
        where attendance_date between "2024-04-30" and "2024-04-30"
    """, as_dict=True)
    checkin = frappe.db.sql("""
        update `tabAttendance`
        set shift=" "
        where attendance_date between "2024-04-30" and "2024-04-30"
    """, as_dict=True)
    # checkin = frappe.db.sql("""
    #     update `tabAttendance`
    #     set extra_hours = " "
    #     where attendance_date between "2024-04-30" and "2024-04-30"
    # """, as_dict=True)
    # checkin = frappe.db.sql("""
    #     update `tabAttendance`
    #     set overtime_hours =" "
    #     where attendance_date between "2024-04-30" and "2024-04-30"
    # """, as_dict=True)
    # checkin = frappe.db.sql("""
    #     update `tabAttendance`
    #     set overtime_hours =" "
    #     where attendance_date between "2024-04-30" and "2024-04-30"
    # """, as_dict=True)
    checkin = frappe.db.sql("""
        update `tabAttendance`
        set docstatus=0
        where attendance_date between "2024-04-30" and "2024-04-30"
    """, as_dict=True)
    checkin = frappe.db.sql("""update `tabEmployee Checkin` set attendance = '' where date(time) between "2024-04-30" and "2024-04-30" """,as_dict = True)
    checkin = frappe.db.sql("""update `tabEmployee Checkin` set skip_auto_attendance = 0 where date(time) between "2024-04-30" and "2024-04-30"  """,as_dict = True)

#updates the employee_type_order on  saving the employee MIS based on the employee type
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

#update the employee number and rename the employee MIS with that employee number
@frappe.whitelist()
def update_employee_no(name,employee_number):
    frappe.db.set_value("Employee",name,'employee_number',employee_number)
    frappe.rename_doc('Employee',name ,employee_number)
    return employee_number



import frappe
from datetime import date

@frappe.whitelist()
def dob_to_age():
    employees = frappe.get_all("Employee", filters={"status": "Active"}, fields=["name", "date_of_birth", "age"])

    for e in employees:
        dob = e.date_of_birth
        
        if not dob:
            frappe.log_error(f"Missing date_of_birth for Employee {e.name}")
            continue
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        
        frappe.db.set_value("Employee", e.name, "age", age)
    frappe.db.commit()

    return f"Updated ages for {len(employees)} employees"


def create_overtime_requests():
    start_date = '2024-07-01'
    end_date = '2024-08-20'
    current_date = start_date
    while current_date <= end_date:
        attendance_records = frappe.get_all(
            "Attendance",
            filters={'docstatus': 1, 'attendance_date': current_date, 'employee_type': 'Worker'},
            fields=["employee", "attendance_date", "overtime_hours","total_working_hours","shift","in_time","out_time"]
        )
        for record in attendance_records:
            if record['overtime_hours'] > 0:
                in_time = record['in_time']
                out_time = record['out_time']
                ot = frappe.new_doc('Overtime Request')
                ot.employee = record['employee']
                ot.ot_date = record['attendance_date']
                ot.shift = record['shift']
                ot.from_time = in_time.strftime('%H:%M:%S')  
                ot.to_time = out_time.strftime('%H:%M:%S')
                ot.total_hour = record['total_working_hours']
                ot.total_hours = record['overtime_hours']
                ot.insert()
                ot.save(ignore_permissions=True)
                frappe.db.commit()
        current_date = add_days(current_date , 1)

#create Overtime Request on submission of Attendance
@frappe.whitelist()
def ot_request_creation(doc,method):
    from datetime import date
    if doc.employee_type=='Worker' and doc.overtime_hours > 0:
        frappe.errprint("working")
        in_datetime = datetime.strptime(doc.in_time, '%Y-%m-%d %H:%M:%S')
        out_datetime = datetime.strptime(doc.out_time, '%Y-%m-%d %H:%M:%S')
        ot = frappe.new_doc('Overtime Request')
        ot.employee = doc.employee
        ot.ot_date = doc.attendance_date
        ot.posting_date = date.today()
        ot.total_hour = doc.total_working_hours
        ot.shift = doc.shift
        ot.from_time = in_datetime.strftime('%H:%M:%S')  
        ot.to_time = out_datetime.strftime('%H:%M:%S')
        ot.total_hours = doc.overtime_hours
        ot.insert()
        ot.save(ignore_permissions=True)
        frappe.db.commit()





@frappe.whitelist()
def gross_change():
    emp='20121101'
    frappe.db.sql("""update `tabEmployee` set actual_gross=gross_pay where name="%s" """,(emp))

@frappe.whitelist()
def get_special_all():
    attendance=frappe.get_all("Attendance",{'employee_type':'Staff','working_hours':('>=',23),'attendance_date':('between',('2024-07-01','2024-07-31'))},['*'])
    i=0
    for att in attendance:
        day_of_week = att.attendance_date.weekday()
        if day_of_week in [0,1,2,3,4]:
            print(1000)
        elif day_of_week ==5:
            print(3500)
        elif day_of_week ==6:
            print(2500)
        print(att.attendance_date)
        i+=1
    print(i)

@frappe.whitelist()
def mark_wh_ot_manual():
    from_date = '2024-09-03'
    to_date = '2024-09-04'
    mark_wh_ot(from_date, to_date)

def mark_wh_ot(from_date, to_date):

    attendance = frappe.db.get_all('Attendance', {'attendance_date': ('between', (from_date,to_date)),'docstatus': ('!=', '2')}, ['*'])
    for att in attendance:
        print([att.name])
        # if att.shift and att.in_time and att.out_time:
        #     in_time = att.in_time
        #     out_time = att.out_time
        #     if att.on_duty_application != "":
        #         if att.in_time and att.out_time:
        #             in_time = att.in_time
        #             out_time = att.out_time
        #     else:
        #         if att.session_from_time and att.session_to_time: 
        #             in_time = att.session_from_time
        #             out_time = att.session_to_time
        #     frappe.errprint(att.name)

import frappe
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,
    nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime,format_date)           

#will send a mail of last three days pending Leave Application Repot for all HR Users
@frappe.whitelist()
def leave_approver_hr():
    day = add_days(frappe.utils.today(), -3)
    leave_application = frappe.db.sql("""
        SELECT * FROM `tabLeave Application`
        WHERE posting_date <= '%s' AND workflow_state not in ('Draft', 'Cancelled', 'Approved', 'Rejected') 
        ORDER BY employee
    """ % (day), as_dict=True)
    
    if leave_application:
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
        for la in leave_application:
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
            """.format(la.employee, la.employee_name, la.department, la.leave_type, 
                       format_date(la.from_date) or ' ', format_date(la.to_date) or ' ', la.workflow_state)
        
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
            subject='Leave Application Report',
            message="""Dear Sir,<br><br>
                        Kindly find the attached employee's pending Leave Application List:<br>{0}
                     """.format(data)
        )

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

#will send a mail of last three days pending On Duty Application Repot for all level Apporvers
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





#will send a mail of last three days pending Permission Repot to all HR Users
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

#will send a mail of last three days pending Overtime Request Repot to all level approvers
@frappe.whitelist()
def overtime_approvers():
    day = add_days(frappe.utils.today(), -3)
    
    def send_email_report(approver_field, approver_level, workflow_state):
        user_list = frappe.db.sql(f"""
            SELECT {approver_field} 
            FROM `tabOvertime Request` 
            WHERE {approver_field} IS NOT NULL 
            GROUP BY {approver_field}
        """, as_dict=True)
        
        for user in user_list:
            approver_email = user.get(approver_field)
            if not approver_email:
                continue
            
            ot_apps = frappe.db.sql(f"""
                SELECT *
                FROM `tabOvertime Request`
                WHERE {approver_field} = %s AND posting_date <= %s AND workflow_state = %s
            """, (approver_email, day, workflow_state), as_dict=True)
            
            # Send message if no Permissions are found
            # if not permission_apps:
            # 	print("hi")
            # 	continue
            
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
            
            for ot in ot_apps:
                data += f"""
                    <tr style="border: 1px solid black;">
                        <td style="padding: 4px; border: 1px solid black;">{ot.employee}</td>
                        <td style="padding: 4px; border: 1px solid black;">{ot.employee_name}</td>
                        <td style="padding: 4px; border: 1px solid black;">{ot.department}</td>
                        <td style="padding: 4px; border: 1px solid black; text-align: center;">{format_date(ot.posting_date) or ''}</td>
                        <td style="padding: 4px; border: 1px solid black; text-align: center;">{format_date(ot.ot_date) or ' '}</td>
                        <td style="padding: 4px; border: 1px solid black; text-align: center;">{ot.from_time}</td>
                        <td style="padding: 4px; border: 1px solid black; text-align: center;">{ot.to_time}</td>
                        <td style="padding: 4px; border: 1px solid black; text-align: center;">{ot.total_hours}</td>
                        <td style="padding: 4px; border: 1px solid black; text-align: center;">{ot.workflow_state}</td>
                    </tr>
                """
            
            data += "</table>"
            if ot_apps:
                frappe.sendmail(
                    recipients=[approver_email],
                    # recipients=['amar.p@groupteampro.com', 'jeniba.a@groupteampro.com'], 
                    subject=f'Overtime Request Application - Pending for Level {approver_level} Approver',
                    message=f"""Dear Sir,<br><br>
                    Kindly find the attached employee's pending Overtime Request Application List :<br>{data}"""
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
# method to update the attendance during update, when on duty application is present
def update_od(doc,method):
    if frappe.db.exists("On Duty Application",{"od_date":doc.attendance_date,'employee':doc.employee,'workflow_state':'Approved'}):
        # if doc.docstatus==1:
        # 	frappe.db.set_value("Attendance", doc.name, "docstatus", 0)
        od_doc=frappe.get_doc("On Duty Application",{"od_date":doc.attendance_date,'employee':doc.employee,'workflow_state':'Approved'})
        frappe.db.set_value("Attendance", doc.name, "on_duty_application", od_doc.name)
        p_wh=0
        if doc.working_hours>0:
            p_wh=doc.working_hours
        if od_doc.session=='Full Day':
            frappe.db.set_value("Attendance", doc.name, "status", "Present")
        else:
            if od_doc.shift=='C':
                tot=p_wh+3.5
                if tot>=7:
                    frappe.db.set_value("Attendance", doc.name, "status", "Present")
                else:
                    frappe.db.set_value("Attendance", doc.name, "status", "Half Day") 
            else:
                tot=p_wh+4
                if tot>=8:
                    frappe.db.set_value("Attendance", doc.name, "status", "Present")
                else:
                    frappe.db.set_value("Attendance", doc.name, "status", "Half Day")
        # doc.submit()
                    
def draft_od():
    od=frappe.db.get_all("On Duty Application",{"docstatus":1,'Workflow_state':'Approved'},['*'])
    for i in od:
        frappe.db.set_value("On Duty Application",i.name,'docstatus',0)
        frappe.db.set_value("On Duty Application",i.name,'Workflow_state',"Draft")
    # checkin = frappe.db.sql("""update `tabLeave Application` set docstatus=0 where name="HR-LAP-2024-00672" """,as_dict = True)
        
import frappe
from frappe.utils import getdate
#returns the total allocated leave of an employee from the start date and for the leave type to display it in Print Format
@frappe.whitelist()
def get_total_leaves_allocated(start_date, employee, leave_type):
    year = getdate(start_date).year    
    total_leaves = frappe.db.sql("""
        SELECT SUM(total_leaves_allocated) AS total_allocated
        FROM `tabLeave Allocation`
        WHERE docstatus = 1 
        AND employee = %s 
        AND leave_type = %s
        AND YEAR(from_date) = %s 
        AND YEAR(to_date) = %s
    """, (employee, leave_type, year, year), as_dict=True)    
    return total_leaves[0].get('total_allocated', 0) if total_leaves else 0

import frappe
from frappe import db
#returns the total approved leaves of an employee from the start date and for the leave type to display it in Print Format
@frappe.whitelist()
def get_approved_leave_days(start_date, employee, leave_type):
    start_date_obj = frappe.utils.getdate(start_date)
    start_month = start_date_obj.month
    start_year = start_date_obj.year
    leave_days = db.sql("""
        SELECT SUM(total_leave_days) 
        FROM `tabLeave Application` 
        WHERE docstatus = 1 
        AND workflow_state = 'Approved' 
        AND employee = %s 
        AND leave_type = %s
        AND MONTH(from_date) = %s 
        AND YEAR(from_date) = %s 
        AND MONTH(to_date) = %s 
        AND YEAR(to_date) = %s
    """, (employee, leave_type, start_month, start_year, start_month, start_year), as_dict=True)

    return leave_days[0].get('SUM(total_leave_days)') or 0


#returns the total leave balance of an employee from the start date and for the leave type to display it in Print Format
@frappe.whitelist()
def get_balance_leaves(start_date, employee, leave_type):
    balance=0
    opening=get_total_leaves_allocated(start_date, employee, leave_type)
    availed=get_approved_leave_days(start_date, employee, leave_type)
    balance=opening-availed
    if balance<0:
        balance=0
    return balance

#returns the holiday count of that period for the employee 
@frappe.whitelist()
def count_holidays(employee,start_date,end_date):
    # Fetch the holiday list from the employee document
    # employee='20080113'
    # start_date='2024-10-01'
    # end_date='2024-10-30'
    employee_doc = frappe.get_doc("Employee", employee)
    holiday_list = employee_doc.holiday_list

    start_date = getdate(start_date)
    end_date = getdate(end_date)

    holidays = frappe.get_all('Holiday',
        filters={
            'parent': holiday_list,
            'holiday_date': ['between', (start_date, end_date)],
            'weekly_off': 0  
        },
        fields=['holiday_date']
    )

    return len(holidays)

#automatically create week off for the staff on submission of Attendance if they worked for 24 hours
def create_weekoff(doc,method):
    if doc.employee_type == "Staff" and doc.in_time and doc.out_time:
        frappe.errprint("Test1")
        shift=''
        if doc.shift:
            if doc.shift=="A":
                shift='C'
                shiftdate=add_days(doc.attendance_date,1)
            elif doc.shift=="B":
                shift='A'
                shiftdate=add_days(doc.attendance_date,1)
            else:
                shift='B'
                shiftdate=add_days(doc.attendance_date,2)
            shiftdate = datetime.strptime(shiftdate, '%Y-%m-%d').date()
            shift_end=frappe.db.get_value("Shift Type",{'name':shift},['end_time'])
            shift_etime = datetime.strptime(str(shift_end), '%H:%M:%S').time()
            shift_start_datetime = datetime.combine(shiftdate, shift_etime)
            doc_out_time = datetime.strptime(doc.out_time, '%Y-%m-%d %H:%M:%S')
            if doc.working_hours >= 24 and  doc_out_time >= shift_start_datetime:
                hh=check_holiday(shiftdate,doc.employee)
                if not hh:
                    if not frappe.db.exists("Shift Assignment", {'employee': doc.employee, 'start_date': shiftdate, 'end_date': shiftdate, 'docstatus': ['!=',2]}):
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

# #automatically create week off for the staff on every day at 09:40 from  Attendance if they worked for 24 hours
# @frappe.whitelist()
# def create_off():
#     from_date = add_days(today(),-1)
#     to_date = today()
#     attendance=frappe.db.get_all("Attendance",{"attendance_date":("Between",(from_date,to_date)),"docstatus":['!=',2]},['*'])
#     for doc in attendance:
#         if doc.employee_type == "Staff" and doc.in_time and doc.out_time:
#             print('1')
#             shift=''
#             if doc.shift:
#                 print('2')
#                 if doc.shift=="A":
#                     shift='C'
#                     shiftdate=add_days(doc.attendance_date,1)
#                 elif doc.shift=="B":
#                     shift='A'
#                     shiftdate=add_days(doc.attendance_date,1)
#                 else:
#                     shift='B'
#                     shiftdate=add_days(doc.attendance_date,2)
#                 shift_end=frappe.db.get_value("Shift Type",{'name':shift},['end_time'])
#                 shift_etime = datetime.strptime(str(shift_end), '%H:%M:%S').time()
#                 shift_start_datetime = datetime.combine(shiftdate, shift_etime)
#                 if doc.working_hours >= 24 and  doc.out_time >= shift_start_datetime:
#                     print('3')
#                     hh=check_holiday(shiftdate,doc.employee)
#                     if not hh:
#                         print('4')
#                         if not frappe.db.exists("Shift Assignment", {'employee': doc.employee, 'start_date': shiftdate, 'end_date': shiftdate, 'docstatus': ['!=',2]}):
#                             print('5')
#                             sa = frappe.new_doc('Shift Assignment')
#                             sa.employee = doc.employee
#                             sa.shift_type = "WW"
#                             sa.start_date = shiftdate
#                             sa.end_date = shiftdate
#                             sa.reason = 'Week Off automatically created for 24 hours working'
#                             sa.save(ignore_permissions=True)
#                             sa.submit()
#                             frappe.db.commit()
#                         else:
#                             if frappe.db.exists("Shift Assignment", {'employee': doc.employee, 'start_date': shiftdate, 'end_date': shiftdate, 'docstatus': 1}):
#                                 print('6')
#                                 sa_exist=frappe.get_doc("Shift Assignment", {'employee': doc.employee, 'start_date': shiftdate, 'end_date': shiftdate, 'docstatus': 1})
#                                 sa_exist.cancel() 
#                                 frappe.db.commit()
#                                 sa = frappe.new_doc('Shift Assignment')
#                                 sa.employee = doc.employee
#                                 sa.shift_type = "WW"
#                                 sa.start_date = shiftdate
#                                 sa.end_date = shiftdate
#                                 sa.reason = 'Week Off automatically created for 24 hours working'
#                                 sa.save(ignore_permissions=True)
#                                 sa.submit()
#                                 frappe.db.commit()


# @frappe.whitelist()
# def create_hooks_att3():
#     job = frappe.db.exists('Scheduled Job Type', 'create_woff')
#     if not job:
#         att = frappe.new_doc("Scheduled Job Type")
#         att.update({
#             "method": 'dongwoo.custom.create_off',
#             "frequency": 'Cron',
#             "cron_format": "0 9 * * *"
#         })
#         att.save(ignore_permissions=True)


from datetime import datetime, timedelta

#calculate the time
@frappe.whitelist()
def calculate_flexible_time(fdate, tdate, perm):
    start = datetime.strptime(str(fdate), '%H:%M:%S').time()
    end = datetime.strptime(str(tdate), '%H:%M:%S').time()
    if isinstance(perm, datetime):
        perm_date = perm.date()
    else:
        perm_date = datetime.strptime(str(perm), '%Y-%m-%d').date()
    start_datetime = datetime.combine(perm_date, start)
    end_datetime = datetime.combine(perm_date, end)
    diff = time_diff_in_hours(end_datetime, start_datetime)
    frappe.errprint(diff)
    if diff>0:
        diff=round(diff,2)
    else:
        diff=0
    return diff

@frappe.whitelist()
def update_sa():
    count=0
    sa=frappe.db.get_all("Shift Assignment",{"start_date":('Between',("2024-11-01",'2024-12-31')),'docstatus':1},['*'])
    for i in sa:
        print(i.employee)
        emp=frappe.db.get_value("Employee",{'name':i.employee},['employee_type'])
        print(emp)
        if emp:
            print(i.employee)
            frappe.db.set_value("Shift Assignment",i.name,'employee_type',emp)

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
def create_special_allow(fdate, tdate):
    special_all = 0
    attendance = frappe.get_all(
        "Attendance", {'employee_type': 'Staff','working_hours': ('>=', 20), 'attendance_date': ('between', (fdate, tdate))},
        ['attendance_date', 'out_time', 'employee']
    )
    
    if attendance:  
        for att in attendance:
            emp_name = att.employee
            frappe.errprint(f"Processing employee: {emp_name} on {att.attendance_date}")
            start_date = fdate
            end_date = add_days(tdate, 1)
            holiday_dates = get_holiday_dates_for_employee(att.employee, fdate, end_date)
            if not holiday_dates:
                holiday_dates = []

            query = """SELECT cast(start_date as char) FROM `tabShift Assignment` WHERE employee='%s' AND shift_type = 'WW' AND reason = '' AND start_date BETWEEN '%s' AND '%s'"""  % (att.employee, start_date, end_date)
            ww = frappe.db.sql(query, as_list=True)
            ww_list = list(chain(*ww))
            holiday_dates.extend(ww_list)
            day_before_holidays = []
            for holiday in holiday_dates:
                day_before_holidays.append(add_days(holiday, -1)) 
             
            day_of_week = att.attendance_date.weekday()
            if cstr(att.attendance_date) in holiday_dates and cstr(att.attendance_date) not in day_before_holidays:
                special_all = 2500
            elif cstr(att.attendance_date) in day_before_holidays and cstr(att.attendance_date) not in holiday_dates:
                special_all = 3000
            elif cstr(att.attendance_date) in day_before_holidays and cstr(att.attendance_date) in holiday_dates:
                special_all = 3000
            else:
                frappe.errprint(att.employee)
                frappe.errprint(day_of_week)
                if day_of_week in [0, 1, 2, 3, 4]:
                    special_all = 1000
                elif day_of_week == 5:
                    special_all = 3000 
                elif day_of_week == 6:
                    special_all = 2500
            if special_all>0:
                if frappe.db.exists("Special Allowance", {'working_date': att.attendance_date, 'employee': att.employee, 'docstatus': ['!=', 2]}):
                    # count += 1
                    allow = frappe.get_doc("Special Allowance", {'working_date': att.attendance_date, 'employee': att.employee, 'docstatus': ['!=', 2]})
                    allow.employee = emp_name
                    allow.working_date = att.attendance_date
                    allow.amount = special_all
                    frappe.db.commit()
                    allow.save(ignore_permissions=True)
                else:
                    allow = frappe.new_doc('Special Allowance')
                    # frappe.errprint(f"Creating Special Allowance for {emp_name}")
                    allow.employee = emp_name
                    allow.working_date = att.attendance_date
                    allow.amount = special_all
                    allow.save(ignore_permissions=True)
                    frappe.db.commit()

@frappe.whitelist()
def create_special_allow_emp(fdate, tdate,emp):
    special_all = 0
    attendance = frappe.get_all(
        "Attendance", {'employee_type': 'Staff','working_hours': ('>=', 20),'employee':emp, 'attendance_date': ('between', (fdate, tdate))},
        ['attendance_date', 'out_time', 'employee']
    )
    
    if attendance:  
        for att in attendance:
            emp_name = att.employee
            frappe.errprint(f"Processing employee: {emp_name} on {att.attendance_date}")
            start_date = fdate
            end_date = add_days(tdate, 1)
            holiday_dates = get_holiday_dates_for_employee(att.employee, fdate, end_date)
            if not holiday_dates:
                holiday_dates = []

            query = """SELECT cast(start_date as char) FROM `tabShift Assignment` WHERE employee='%s' AND shift_type = 'WW' AND reason = '' AND start_date BETWEEN '%s' AND '%s'"""  % (att.employee, start_date, end_date)
            ww = frappe.db.sql(query, as_list=True)
            ww_list = list(chain(*ww))
            holiday_dates.extend(ww_list)
            day_before_holidays = []
            for holiday in holiday_dates:
                day_before_holidays.append(add_days(holiday, -1)) 
             
            day_of_week = att.attendance_date.weekday()
            if cstr(att.attendance_date) in holiday_dates and cstr(att.attendance_date) not in day_before_holidays:
                special_all = 2500
            elif cstr(att.attendance_date) in day_before_holidays and cstr(att.attendance_date) not in holiday_dates:
                special_all = 3000
            elif cstr(att.attendance_date) in day_before_holidays and cstr(att.attendance_date) in holiday_dates:
                special_all = 3000
            else:
                frappe.errprint(att.employee)
                frappe.errprint(day_of_week)
                if day_of_week in [0, 1, 2, 3, 4]:
                    special_all = 1000
                elif day_of_week == 5:
                    special_all = 3000 
                elif day_of_week == 6:
                    special_all = 2500
            if special_all>0:
                if frappe.db.exists("Special Allowance", {'working_date': att.attendance_date, 'employee': att.employee, 'docstatus': ['!=', 2]}):
                    # count += 1
                    allow = frappe.get_doc("Special Allowance", {'working_date': att.attendance_date, 'employee': att.employee, 'docstatus': ['!=', 2]})
                    allow.employee = emp_name
                    allow.working_date = att.attendance_date
                    allow.amount = special_all
                    frappe.db.commit()
                    allow.save(ignore_permissions=True)
                else:
                    allow = frappe.new_doc('Special Allowance')
                    # frappe.errprint(f"Creating Special Allowance for {emp_name}")
                    allow.employee = emp_name
                    allow.working_date = att.attendance_date
                    allow.amount = special_all
                    allow.save(ignore_permissions=True)
                    frappe.db.commit()



@frappe.whitelist()
def create_special_allow_employee_type(fdate, tdate,employee_type):
    special_all = 0
    attendance = frappe.get_all(
        "Attendance", {'employee_type': 'Staff','working_hours': ('>=', 20), 'attendance_date': ('between', (fdate, tdate))},
        ['attendance_date', 'out_time', 'employee']
    )
    
    if attendance:  
        for att in attendance:
            emp_name = att.employee
            frappe.errprint(f"Processing employee: {emp_name} on {att.attendance_date}")
            start_date = fdate
            end_date = add_days(tdate, 1)
            holiday_dates = get_holiday_dates_for_employee(att.employee, fdate, end_date)
            if not holiday_dates:
                holiday_dates = []

            query = """SELECT cast(start_date as char) FROM `tabShift Assignment` WHERE employee='%s' AND shift_type = 'WW' AND reason = '' AND start_date BETWEEN '%s' AND '%s'"""  % (att.employee, start_date, end_date)
            ww = frappe.db.sql(query, as_list=True)
            ww_list = list(chain(*ww))
            holiday_dates.extend(ww_list)
            day_before_holidays = []
            for holiday in holiday_dates:
                day_before_holidays.append(add_days(holiday, -1)) 
             
            day_of_week = att.attendance_date.weekday()
            if cstr(att.attendance_date) in holiday_dates and cstr(att.attendance_date) not in day_before_holidays:
                special_all = 2500
            elif cstr(att.attendance_date) in day_before_holidays and cstr(att.attendance_date) not in holiday_dates:
                special_all = 3000
            elif cstr(att.attendance_date) in day_before_holidays and cstr(att.attendance_date) in holiday_dates:
                special_all = 3000
            else:
                if day_of_week in [0, 1, 2, 3, 4]:
                    special_all = 1000
                elif day_of_week == 5:
                    special_all = 3000 
                elif day_of_week == 6:
                    special_all = 2500
            if special_all>0:
                if frappe.db.exists("Special Allowance", {'working_date': att.attendance_date, 'employee': att.employee, 'docstatus': ['!=', 2]}):
                    # count += 1
                    allow = frappe.get_doc("Special Allowance", {'working_date': att.attendance_date, 'employee': att.employee, 'docstatus': ['!=', 2]})
                    allow.employee = emp_name
                    allow.working_date = att.attendance_date
                    allow.amount = special_all
                    frappe.db.commit()
                    allow.save(ignore_permissions=True)
                else:
                    allow = frappe.new_doc('Special Allowance')
                    # frappe.errprint(f"Creating Special Allowance for {emp_name}")
                    allow.employee = emp_name
                    allow.working_date = att.attendance_date
                    allow.amount = special_all
                    allow.save(ignore_permissions=True)
                    frappe.db.commit()


@frappe.whitelist()
def calculate_od_time(ftime, ttime):
    diff = time_diff_in_hours(ttime, ftime)
    frappe.errprint(diff)
    if diff>0:
        diff=diff
    else:
        diff=0
    return diff

@frappe.whitelist()
def count_att():
    count=0
    att=frappe.db.get_all("Attendance",{'in_time':['!=',''],'out_time':['!=',''],'working_hours':0,'docstatus':['!=',2],'attendance_date':('between',('2024-12-01','2025-01-21'))},['in_time','out_time','name'])
    for a in att:
        if a.in_time<a.out_time:
            print(a.name)
            count+=1
    return count


from frappe import _
from frappe.utils.pdf import get_pdf
import frappe

@frappe.whitelist()
def candidate_excel_format():
    # Fetch candidates from "Appointment Letter"
    candidates = frappe.get_all(
        "Appointment Letter",
        filters={"name": "HR-APP-LETTER-00001"},
        fields=["*"],
    )

    if not candidates:
        frappe.throw(_("No candidates found for the provided Appointment Letter."))

    # Generate PDF
    pdf_filename = "Appointment_Letter.pdf"
    pdf_content = make_pdf_candidate(candidates)

    # Trigger email
    candidate_status_mail_test(pdf_filename, pdf_content, candidates)


def candidate_status_mail_test(pdf_filename, pdf_content, candidates):
    frappe.errprint("Hii")
    email_body = generate_email_body(candidates)

    subject = "Appointment Order"
    message = f"""
    Dear Sir/Madam,<br><br>
    Kindly find the attached Appointment Letter for your reference:<br><br>
    {email_body if email_body else ''}<br><br>
    Thanks & Regards,<br>
    TEAM ERP<br>
    <i>This email has been automatically generated. Please do not reply.</i>
    """

    frappe.sendmail(
        recipients=["pavithra.s@groupteampro.com"],
        subject=subject,
        message=message,
        attachments=[
            {"fname": pdf_filename, "fcontent": pdf_content}
        ]
    )


def generate_email_body(candidates):
    frappe.errprint("Hello")
    data = """
    <table style="width: 100%; border: 1px solid #ddd; border-collapse: collapse;">
        <thead>
            <tr>
                <th colspan="2" style="text-align: center; font-size: 18px; padding: 8px;">Appointment Order</th>
            </tr>
        </thead>
        <tbody>
    """

    for candidate in candidates:
        applicant = frappe.get_doc("Job Applicant", candidate.job_applicant)
        data += f"""
        <tr>
            <td colspan="2" style="padding: 8px; font-size: 18px; text-align:right">Date: {candidate.appointment_date}</td>
        </tr>
        <tr>
            <td colspan="2" style="padding: 8px; font-size: 18px;">Mr. {applicant.applicant_name}</td>
        </tr>
        <tr>
            <td colspan="2" style="padding: 8px; font-size: 18px;">{applicant.present__address_}</td>
        </tr>
        <tr>
            <td colspan="2" style="padding: 8px; font-size: 18px;">{applicant.address_line2}</td>
        </tr>
        <tr>
            <td colspan="2" style="padding: 8px; font-size: 18px;">{applicant.city2}, {applicant.district2}</td>
        </tr>
        <tr>
            <td colspan="2" style="padding: 8px; font-size: 18px;">Pincode: {applicant.pincode2}</td>
        </tr>
        <tr>
            <td colspan="2" style="padding: 8px; font-size: 18px;">Dear Mr. {applicant.applicant_name},</td>
        </tr>
        <tr>
            <td colspan="2" style="padding: 8px; font-size: 18px;">
                We have pleasure in appointing you as {" "} with effect from {candidate.appointment_date}, subject to the following terms and conditions:
            </td>
        </tr>
        """
        template = frappe.get_doc("Appointment Letter Template", candidate.appointment_letter_template)
        data += f"""
        <tr>
            <td colspan="2" style="padding: 8px; font-size: 18px;">1)Your C T C details are enclosed in the Annexure.</td>
            <td colspan="2" style="padding: 8px; font-size: 18px;">2)You will be on probation for 6 months. On satisfactory completion of your probationary period you may be confirmed in our services. If your performance is not upto the mark during the probation period, your services will be terminated.</td>
            <td colspan="2" style="padding: 8px; font-size: 18px;">3)The period of probation may be extended at the discretion of the company for further period of 3 months, depending on your performance.</td>
            <td colspan="2" style="padding: 8px; font-size: 18px;">4)On successful completion of the probation, your confirmation will be conveyed to you in writing. In the absence of any communication to this effect, it will be presumed that your probation has been extended for further period of 3 months at the option of management.</td>
            <td colspan="2" style="padding: 8px; font-size: 18px;">5)During the confirmation period, your service will be terminable at the discretion of the company on giving sixty days of notice, or on payment of 60 days salary in lieu of such notice. If you desire to leave the services of the company, you will have to serve 60 days’ notice period.</td>
            <td colspan="2" style="padding: 8px; font-size: 18px;">6)Your initial posting will be in our Factory Site, located in Mappedu, Thiruvallur District. But you may be required to serve in any part of India / Abroad as and when required by the company. You are also liable to be transferred from one department to another department of the organization and one job to another job. In that case, you will be governed by the working hours and other service conditions applicable to that department / locality.</td>
            <td colspan="2" style="padding: 8px; font-size: 18px;">7)During your services, you may be deputed to our parent company at Korea, at that time you should obey the rules of the Korea Nation and you will be governed by the working hours & service conditions applicable to that Company.</td>
            <td colspan="2" style="padding: 8px; font-size: 18px;">8)The grant of annual increment and your advancement in category will depend upon your performance and merit, during the review period, as judged by the management.</td>
            <td colspan="2" style="padding: 8px; font-size: 18px;">9)You should maintain the business secrets of the organization and shall not disclose any information about the organization to the outsider.</td>
            <td colspan="2" style="padding: 8px; font-size: 18px;">10)You will, at all times during your employment with us, devote your whole time and attention to the company’s work and shall not engage yourself directly or indirectly in any other work.</td>
            <td colspan="2" style="padding: 8px; font-size: 18px;">11)The age for Superannuation is 58 years. However purely at the discretion of the Management your services may be extended for further periods. But you have no claim for extension of services.</td>
            <td colspan="2" style="padding: 8px; font-size: 18px;">12)The remuneration and other terms of your engagement shall not be disclosed to other members of the staff of this company and to any other person with the exception of close relatives.</td>
            <td colspan="2" style="padding: 8px; font-size: 18px;">13)You will be governed by the General Conduct Rules / standing order of the company that are in force / altered / or amended from time to time.</td>
            <td colspan="2" style="padding: 8px; font-size: 18px;">14)You are liable to keep safe and in order any of the property provided to you for discharging your official duties. The cost of the property will be recovered from you if any damages</td>
            <td colspan="2" style="padding: 8px; font-size: 18px;">15)Any declaration given or furnished by you proves to be false at any time or if you are found to have willfully suppressed any material information, you will be liable to be removed from the services of the company and such other action as the company may deem necessary.</td>
            <td colspan="2" style="padding: 8px; font-size: 18px;">16)You should intimate in writing any changes in your family status and also any changes in your communication address.</td>
            <td colspan="2" style="padding: 8px; font-size: 18px;">17)Any change in Category is purely at the discretion of the Management.</td>
            <td colspan="2" style="padding: 8px; font-size: 18px;">18)You are required to sign the declaration presented below and return the copy to us.</td>
            <td colspan="2" style="padding: 8px; font-size: 18px;">for DongWoo Surfacetech (India) Pvt. Ltd.,</td>
        </tr>
        """

    data += "</tbody></table>"
    return data


def make_pdf_candidate(candidates):
    pdf_data = """
    <table style="width: 100%; border: 1px solid #ddd; border-collapse: collapse;">
        <thead>
            <tr>
                <th colspan="2" style="text-align: center; font-size: 18px; padding: 8px;">Appointment Order</th>
            </tr>
        </thead>
        <tbody>
    """

    for candidate in candidates:
        applicant = frappe.get_doc("Job Applicant", candidate.job_applicant)
        pdf_data += f"""
        <tr>
            <td colspan="2" style="padding: 8px; font-size: 18px;text-align:right">Date: {candidate.appointment_date}</td>
        </tr>
        <tr>
            <td colspan="2" style="padding: 8px; font-size: 18px;">Mr. {applicant.applicant_name}</td>
        </tr>
        <tr>
            <td colspan="2" style="padding: 8px; font-size: 18px;">{applicant.present__address_}</td>
        </tr>
        <tr>
            <td colspan="2" style="padding: 8px; font-size: 18px;">{applicant.address_line2}</td>
        </tr>
        <tr>
            <td colspan="2" style="padding: 8px; font-size: 18px;">{applicant.city2}, {applicant.district2}</td>
        </tr>
        <tr>
            <td colspan="2" style="padding: 8px; font-size: 18px;">Pincode: {applicant.pincode2}</td>
        </tr>
        <tr>
            <td colspan="2" style="padding: 8px; font-size: 18px;">Dear Mr. {applicant.applicant_name},</td>
        </tr>
        <tr>
            <td colspan="2" style="padding: 8px; font-size: 18px;">
                We have pleasure in appointing you as {" "} with effect from {candidate.appointment_date}, subject to the following terms and conditions:
            </td>
        </tr>
        """
        template = frappe.get_doc("Appointment Letter Template", candidate.appointment_letter_template)
        pdf_data += f"""
        <tr>
            <td colspan="2" style="padding: 8px; font-size: 18px;">1)Your C T C details are enclosed in the Annexure.</td>
            <td colspan="2" style="padding: 8px; font-size: 18px;">2)You will be on probation for 6 months. On satisfactory completion of your probationary period you may be confirmed in our services. If your performance is not upto the mark during the probation period, your services will be terminated.</td>
            <td colspan="2" style="padding: 8px; font-size: 18px;">3)The period of probation may be extended at the discretion of the company for further period of 3 months, depending on your performance.</td>
            <td colspan="2" style="padding: 8px; font-size: 18px;">4)On successful completion of the probation, your confirmation will be conveyed to you in writing. In the absence of any communication to this effect, it will be presumed that your probation has been extended for further period of 3 months at the option of management.</td>
            <td colspan="2" style="padding: 8px; font-size: 18px;">5)During the confirmation period, your service will be terminable at the discretion of the company on giving sixty days of notice, or on payment of 60 days salary in lieu of such notice. If you desire to leave the services of the company, you will have to serve 60 days’ notice period.</td>
            <td colspan="2" style="padding: 8px; font-size: 18px;">6)Your initial posting will be in our Factory Site, located in Mappedu, Thiruvallur District. But you may be required to serve in any part of India / Abroad as and when required by the company. You are also liable to be transferred from one department to another department of the organization and one job to another job. In that case, you will be governed by the working hours and other service conditions applicable to that department / locality.</td>
            <td colspan="2" style="padding: 8px; font-size: 18px;">7)During your services, you may be deputed to our parent company at Korea, at that time you should obey the rules of the Korea Nation and you will be governed by the working hours & service conditions applicable to that Company.</td>
            <td colspan="2" style="padding: 8px; font-size: 18px;">8)The grant of annual increment and your advancement in category will depend upon your performance and merit, during the review period, as judged by the management.</td>
            <td colspan="2" style="padding: 8px; font-size: 18px;">9)You should maintain the business secrets of the organization and shall not disclose any information about the organization to the outsider.</td>
            <td colspan="2" style="padding: 8px; font-size: 18px;">10)You will, at all times during your employment with us, devote your whole time and attention to the company’s work and shall not engage yourself directly or indirectly in any other work.</td>
            <td colspan="2" style="padding: 8px; font-size: 18px;">11)The age for Superannuation is 58 years. However purely at the discretion of the Management your services may be extended for further periods. But you have no claim for extension of services.</td>
            <td colspan="2" style="padding: 8px; font-size: 18px;">12)The remuneration and other terms of your engagement shall not be disclosed to other members of the staff of this company and to any other person with the exception of close relatives.</td>
            <td colspan="2" style="padding: 8px; font-size: 18px;">13)You will be governed by the General Conduct Rules / standing order of the company that are in force / altered / or amended from time to time.</td>
            <td colspan="2" style="padding: 8px; font-size: 18px;">14)You are liable to keep safe and in order any of the property provided to you for discharging your official duties. The cost of the property will be recovered from you if any damages</td>
            <td colspan="2" style="padding: 8px; font-size: 18px;">15)Any declaration given or furnished by you proves to be false at any time or if you are found to have willfully suppressed any material information, you will be liable to be removed from the services of the company and such other action as the company may deem necessary.</td>
            <td colspan="2" style="padding: 8px; font-size: 18px;">16)You should intimate in writing any changes in your family status and also any changes in your communication address.</td>
            <td colspan="2" style="padding: 8px; font-size: 18px;">17)Any change in Category is purely at the discretion of the Management.</td>
            <td colspan="2" style="padding: 8px; font-size: 18px;">18)You are required to sign the declaration presented below and return the copy to us.</td>
            <td colspan="2" style="padding: 8px; font-size: 18px;">for DongWoo Surfacetech (India) Pvt. Ltd.,</td>
        </tr>
        """

    pdf_data += "</tbody></table>"

    # Generate PDF
    return get_pdf(pdf_data)

# @frappe.whitelist()
# def job_offer_email(name):
#     frappe.sendmail(
#         recipients=['jeniba.a@groupteampro.com','pavithra.s@groupteampro.com'],
#         cc='',
#         subject="Job Offer",
#         message="""<p><b>Dear Sir/Mam ,</b></p>
#             Please find attached the Job offer from  DongWoo Surfacetech (India) Pvt Ltd.<br>
#             """,
           
#         attachments=[frappe.attach_print("Job Offer",name,file_name="OfferLetter", print_format="Offer Letter")]
#     )

@frappe.whitelist()
def change_user_name():
    name = frappe.db.get_value("User",{"name":"jeniba.a@groupteampro.com","email":"test@gmail.com"},["name"])
    frappe.rename_doc("User",name,"test@groupteampro.com", force=1)

# @frappe.whitelist()
# def appointment_email(name):
#     frappe.sendmail(
#         recipients=['jeniba.a@groupteampro.com','pavithra.s@groupteampro.com'],
#         cc='',
#         subject="Job Offer",
#         message="""<p><b>Dear Sir/Mam ,</b></p>
#             Please find attached the Appointment letter from  DongWoo Surfacetech (India) Pvt Ltd.<br>
#             """,
           
#         attachments=[frappe.attach_print("Job Applicant",name,file_name="AppointmentLetter", print_format="Appointment letter Print")]
#     )

@frappe.whitelist()
def test_check():
    attendance = frappe.get_all("Attendance", {"docstatus": 1, "attendance_date": "2025-01-02", "employee": ["not in", ("1234", "2345")]}, ["name", "out_time", "employee", "attendance_date"])
    for att in attendance:
        if att.out_time:
            if not frappe.db.exists("Employee Checkin", {"time":att.out_time}):
                print([att.name, att.employee, att.attendance_date])

@frappe.whitelist()
def att_count():
    att=frappe.db.get_all("Attendance",{'docstatus':['!=',2],'attendance_date':('between',('2024-11-01','2024-11-30')),'in_time':['!=',''],'out_time':['!=',''],'shift':'C'},['in_time','out_time','name'])
    count=0
    for a in att:
        if a.in_time>a.out_time:
            print(a.name)
            count+=1
    return count


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


@frappe.whitelist()
def get_att_count():
    att=frappe.db.get_all("Attendance",{'attendance_date':('between',('2025-05-01','2025-05-09')),'in_time':['!=',''],'out_time':['!=',''],'docstatus':['!=',2]},['in_time','out_time','name'])
    for a in att:
        if a.in_time > a.out_time:
            print(a.name)

# @frappe.whitelist(allow_guest=True)
# def get_leave_data(from_date, to_date, employee, year): 
#     from_date_ = datetime.strptime(from_date, "%Y-%m-%d").strftime('%d-%m-%Y')
#     to_date_ = datetime.strptime(to_date, "%Y-%m-%d").strftime('%d-%m-%Y')
#     emp_data_list = frappe.db.get_all('Employee',{'name':employee},['first_name','date_of_joining','department','designation','employee_type'])
#     emp_data = emp_data_list[0] 
#     allocated_leave_list = frappe.db.sql("""
#         select total_leaves_allocated,leave_type
#         from `tabLeave Allocation`
#         where docstatus != 2 and employee = %(employee)s
#             and (from_date between %(from_date)s and %(to_date)s
#                 or to_date between %(from_date)s and %(to_date)s
#                 or (from_date < %(from_date)s and to_date > %(to_date)s))
#         """, {
#             "from_date": from_date,
#             "to_date": to_date,
#             "employee":employee,
#         },
#     as_dict = True)
#     allocated_cl, allocated_sl, allocated_el =0,0,0
#     for allocated_leave in allocated_leave_list:
#         if allocated_leave['leave_type'] == 'Casual Leave (CL)':
#             allocated_cl = allocated_leave['total_leaves_allocated']
#         # else:
#         #     allocated_cl =0
#         if allocated_leave['leave_type'] == 'Sick Leave (SL)':
#             allocated_sl = allocated_leave['total_leaves_allocated']
#         # else:
#         #     allocated_sl =0
#         if allocated_leave['leave_type'] == 'Earned Leave (EL)':
#             allocated_el = allocated_leave['total_leaves_allocated']
#         # else:
#         #     allocated_el =0
#     leave_data = frappe.db.sql("""
#                 select leave_balance,from_date,to_date,total_leave_days,pre_defined_reason,leave_type,creation,modified
#                 from `tabLeave Application`
#                 where docstatus = 1 and workflow_state != 'Rejected' and employee = %(employee)s
#                     and (from_date between %(from_date)s and %(to_date)s
#                         or to_date between %(from_date)s and %(to_date)s
#                         or (from_date < %(from_date)s and to_date > %(to_date)s))
#                     order by creation 
#                 """, {
#                     "from_date": from_date,
#                     "to_date": to_date,
#                     "employee":employee
#                 },
#             as_dict = True)
#     rows = ""
#     index =0
#     cl_leave_balance = float(allocated_cl) if allocated_cl else 0.0
#     sl_leave_balance = float(allocated_sl) if allocated_sl else 0.0
#     el_leave_balance = float(allocated_el) if allocated_el else 0.0
#     cl_leave_type = ''
#     sl_leave_type =''
#     el_leave_type =''
#     for leave in leave_data:
#         index +=1
#         if leave['leave_type'] in ['Casual Leave (CL)','Sick Leave (SL)','Earned Leave (EL)']:
#             if leave['leave_type'] == 'Casual Leave (CL)':
#                 cl_leave_balance -= float(leave['total_leave_days'])
#                 cl_leave_type = '<span style="color: black; font-weight: bold;">✔</span>'
#                 sl_leave_type =''
#                 el_leave_type =''
#             elif leave['leave_type'] == 'Sick Leave (SL)':
#                 sl_leave_type = '<span style="color: black; font-weight: bold;">✔</span>'
#                 cl_leave_type = ''
#                 el_leave_type =''
#                 sl_leave_balance -= float(leave['total_leave_days'])
#             elif leave['leave_type'] == 'Earned Leave (EL)':
#                 el_leave_type = '<span style="color: black; font-weight: bold;">✔</span>'
#                 cl_leave_type = ''
#                 sl_leave_type =''
#                 el_leave_balance -= float(leave['total_leave_days'])
#             creation_date = leave['creation'].strftime('%d-%m-%Y')
#             modified_date = leave['modified'].strftime('%d-%m-%Y')
#             leave_start_date = leave['from_date'].strftime('%d-%m-%Y')
#             leave_end_date = leave['to_date'].strftime('%d-%m-%Y')
#             rows += f"""
#             <tr>
#                 <td style="border: 1px solid black;text-align: center;">{index}</td>
#                 <td style="border: 1px solid black;text-align: center;">{creation_date}</td>
#                 <td style="border: 1px solid black;text-align: center;">{modified_date}</td>
#                 <td style="border: 1px solid black;text-align: center;">{leave_start_date}</td>
#                 <td style="border: 1px solid black;text-align: center;">{leave_end_date}</td>
#                 <td style="border: 1px solid black;text-align: right;">{leave['total_leave_days']}</td>
#                 <td style="border: 1px solid black;text-align: center;">{cl_leave_type}</td>
#                 <td style="border: 1px solid black;text-align: center;">{sl_leave_type}</td>
#                 <td style="border: 1px solid black;text-align: center;">{el_leave_type}</td>
#                 <td style="border: 1px solid black;text-align: center;">{leave['pre_defined_reason']}</td>
#                 <td style="border: 1px solid black;text-align: right;">{cl_leave_balance}</td>
#                 <td style="border: 1px solid black;text-align: right;">{sl_leave_balance}</td>
#                 <td style="border: 1px solid black;text-align: right;">{el_leave_balance}</td>
#             </tr>
#             """
        
        
#     doj = emp_data['date_of_joining'].strftime('%d-%m-%Y')
#     data = f"""
    
#     <div style="overflow-x: auto; color: black;">
#             <table border="1" style="width: 100%; border-collapse: collapse; text-align: left;border: none;">
               
                
#             <tr>
#               <td rowspan="2" style="border: 1px solid black;text-align: center;"><strong>S.No.</strong></th>
#               <td rowspan ="2" style="border: 1px solid black;text-align: center;"><strong>APPLTN. DATE</strong></td>
#               <td rowspan="2" style="border: 1px solid black;text-align: center;"><strong>APPRVL DATE</strong></td>
#               <td colspan="2" style="border: 1px solid black;text-align: center;"><strong>LEAVE DAYS</strong></td>
#               <td rowspan="2" style="border: 1px solid black;text-align: center;"><strong>NO OF DAYS</strong></td>
#               <td colspan="3" style="border: 1px solid black;text-align: center;"><strong>TYPE OF LEAVE</strong></td>
#               <td rowspan="2" style="border: 1px solid black;text-align: center;"><strong>REASON FOR LEAVE</strong></td>
#               <td colspan="3" style="border: 1px solid black;text-align: center;"><strong>BALANCE LEAVE</strong></td>
#             </tr>
#             <tr>
#                 <td style="border: 1px solid black;text-align: center;"><strong>FROM</strong></td>
#                 <td style="border: 1px solid black;text-align: center;"><strong>TO</strong></td>
#                 <td style="border: 1px solid black;text-align: center;"><strong>CL</strong></td>
#                 <td style="border: 1px solid black;text-align: center;"><strong>SL</strong></td>
#                 <td style="border: 1px solid black;text-align: center;"><strong>EL</strong></td>
#                 <td style="border: 1px solid black;text-align: center;"><strong>CL</strong></td>
#                 <td style="border: 1px solid black;text-align: center;"><strong>SL</strong></td>
#                 <td style="border: 1px solid black;text-align: center;"><strong>EL</strong></td>
                
#             </tr>
#                 {rows}
#         </table>
#     </div>
#     """
#     return data


@frappe.whitelist()
def process_attendance_upload(doc_name):
        # frappe.errprint('234')
        # try:
        doc = frappe.get_doc("Attendance Upload", doc_name)

        if not doc.upload_attendance:
            frappe.throw(_("Please upload an attendance file."))

        filename, file_content = get_file(doc.upload_attendance)
        file_text = file_content.decode('utf-8') if isinstance(file_content, bytes) else file_content
        file_obj = io.StringIO(file_text)
        doc.create_attendance_from_csv(file_obj)

        
from dongwoo.mark_attendance import mark_att_with_employee
@frappe.whitelist()
def cancel_attendance_upload(doc_name):
    att=frappe.db.get_all("Attendance",{'attendance_upload':doc_name},['name'])
    for a in att:
        frappe.db.set_value("Attendance", a.name, "attendance_upload", "")
        doc = frappe.get_doc('Attendance', {'name':a.name})
        if doc.docstatus == 1:
            doc.cancel()
        mark_att_with_employee(doc.attendance_date,doc.attendance_date,doc.employee)
    s_ass=frappe.db.get_all("Shift Assignment",{'schedule':doc_name,'docstatus':['!=',2]},['name'])
    for s in s_ass:
        s_doc=frappe.get_doc('Shift Assignment',s.name)
        if s_doc.docstatus==1:
            s_doc.cancel()
        else:
            s_doc.delete()
    ot_doc=frappe.db.get_all("OT Type",{'upload_attendance':doc_name},['name'])
    for s in ot_doc:
        o_doc=frappe.get_doc('OT Type',s.name)
        o_doc.delete()

# @frappe.whitelist()
# def cl_monthly_leave_allocations():
#     print("Hi")
#     today = date.today()

#     # if today.day != 1:
#     #     return

#     first_day = today.replace(day=1)
#     last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1])
#     print(first_day)
#     print(last_day)

#     # employees = [{
#     #     "name": "4231001",
#     #     "employee_name": "DURAI P"
#     # }]
#     employees = frappe.db.sql("""
#         SELECT name, employee_name, date_of_joining, employee_type
#         FROM `tabEmployee`
#         WHERE status = 'Active'
#         AND employee_type IN ('NAPS', 'GET', 'D . Trainee')
#     """, as_dict=True)

#     for employee in employees:
      
#         exists = frappe.db.exists("Leave Allocation", {
#             "employee": employee["name"],
#             "leave_type": "Casual Leave (CL)",
#             "from_date": first_day,
#             "to_date": last_day,
#             "docstatus":["!=",2]
#         })
#         if not exists:
#             la = frappe.new_doc("Leave Allocation")
#             la.employee = employee["name"]
#             la.leave_type = "Casual Leave (CL)"
#             la.new_leaves_allocated = 1
#             la.from_date = first_day
#             la.to_date = last_day
#             la.save(ignore_permissions=True)
#             la.submit()
            

# @frappe.whitelist()
# def create_cl_leave():
#     job = frappe.db.exists('Scheduled Job Type', 'cl_monthly_leave_allocations')
#     if not job:
#         att = frappe.new_doc("Scheduled Job Type")
#         att.update({
#             "method": 'dongwoo.custom.cl_monthly_leave_allocations',
#             "frequency": 'Monthly',
#             "cron_format": "0 0 1 * *"
#         })
#         att.save(ignore_permissions=True)

# @frappe.whitelist()
# def create_job_fail():
#     job = frappe.db.exists('Scheduled Job Type', 'cron_failed')
#     if not job:
#         emc = frappe.new_doc("Scheduled Job Type")
#         emc.update({
#             "method": 'dongwoo.custom.cron_failed_method',
#             "frequency": 'Cron',
#             "cron_format": '*/5 * * * *'
#         })
#         emc.save(ignore_permissions=True)

# @frappe.whitelist()
# def cron_failed_method():
#     cutoff_time = datetime.now() - timedelta(minutes=5)
#     failed_jobs = frappe.get_all(
#         "Scheduled Job Log",
#         filters={
#             "status": "Failed",
#             "creation": [">=", cutoff_time]
#         },
#         fields=["scheduled_job_type"]
#     )
#     unique_job_types = set()
#     for job in failed_jobs:
#         unique_job_types.add(job['scheduled_job_type'])

#     for job_type in unique_job_types:
#         frappe.sendmail(
#             recipients = ["erp@groupteampro.com","jeniba.a@groupteampro.com"],
#             subject = 'Failed Cron List - DONGWOO',
#             message = 'Dear Sir / Mam <br> Kindly find the below failed Scheduled Job  %s'%(job_type)
#         )

# @frappe.whitelist()
# def miss_punch_mail1():
#     job = frappe.db.exists('Scheduled Job Type', 'Miss_punch_mail1')
#     if not job:
#         emc = frappe.new_doc("Scheduled Job Type")
#         emc.update({
#             "method": 'dongwoo.custom.send_miss_punch_report_mail1',
#             "frequency": 'Cron',
#             "cron_format": '0 10 * * *'
#         })
#         emc.save(ignore_permissions=True)


# import frappe
# from frappe.utils import nowdate, add_days, format_datetime

# @frappe.whitelist()
# def send_miss_punch_report_mail1():
#     yesterday = add_days(nowdate(), -1)

#     records = frappe.db.sql("""
#         SELECT 
#             emp.name AS employee_id,
#             emp.employee_name,
#             att.attendance_date,
#             att.in_time,
#             att.out_time,
#             att.status,
#             att.late_entry_time,
#             att.early_out_time
#         FROM `tabAttendance` att
#         JOIN `tabEmployee` emp ON att.employee = emp.name
#         WHERE att.attendance_date = %s
#         AND att.status != 'On Leave'
#         AND (
#             (att.in_time IS NOT NULL AND att.out_time IS NULL)
#             OR
#             (att.in_time IS NULL AND att.out_time IS NOT NULL)
#         )
#         ORDER BY emp.employee_name
#     """, (yesterday,), as_dict=1)

#     if not records:
#         return

#     message = f"""
#     <p>Dear Sir/Mam,</p>
#     <p>Kindly find the below attached <b>Miss Punch List</b> for yesterday.</p>
#     """

#     table = """
#         <table border="1" cellspacing="0" cellpadding="5" style="border-collapse:collapse; width:120%;">
#             <tr style="background-color:#00008b; color:white; text-align:center;">
#                 <th style="text-align:center; width:5%;">S.No</th>
#                 <th style="text-align:center; width:10%;">Employee</th>
#                 <th style="text-align:center; width:15%;">Employee Name</th>
#                 <th style="text-align:center; width:15%;">Attendance Date</th>
#                 <th style="text-align:center; width:20%;">In Time</th>
#                 <th style="text-align:center; width:20%;">Out Time</th>
#                 <th style="text-align:center; width:10%;">Status</th>
#                 <th style="text-align:center; width:10%;">Late Entry</th>
#                 <th style="text-align:center; width:10%;">Early Exit</th>
#             </tr>
#     """

#     for i, r in enumerate(records, start=1):
#         table += f"""
#             <tr>
#                 <td style="text-align:center; width:5%;">{i}</td>
#                 <td style="text-align:left; width:10%;">{r.employee_id}</td>
#                 <td style="text-align:left; width:20%;">{r.employee_name}</td>
#                 <td style="text-align:left; width:10%;">{formatdate(r.attendance_date, "dd-MM-yyyy")}</td>
#                 <td style="text-align:left; width:15%;">{format_datetime(r.in_time, "dd-MM-yyyy HH:mm") if r.in_time else ''}</td>
#                 <td style="text-align:left; width:15%;">{format_datetime(r.out_time, "dd-MM-yyyy HH:mm") if r.out_time else ''}</td>
#                 <td style="text-align:left; width:10%;">{r.status}</td>
#                 <td style="text-align:left; width:7%;">{r.late_entry or ''}</td>
#                 <td style="text-align:left; width:8%;">{r.early_exit or ''}</td>
#             </tr>
#         """
#     table += "</table>"
#     message += table
#     message += "<p>Regards,<br>HR Department</p>"
#     frappe.sendmail(
#         recipients=["jeniba.a@groupteampro.com","info@dwsi.co.in","vishnu@dwsi.co.in","vishal@dwsi.co.in"],
#         subject=f"Miss Punch Report - {formatdate(yesterday)}",
#         message=message
#     )


import frappe
from frappe.utils import today

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
