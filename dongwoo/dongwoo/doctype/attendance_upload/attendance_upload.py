# Copyright (c) 2025, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import date, datetime, timedelta
import openpyxl
from frappe.utils.csvutils import UnicodeWriter, read_csv_content
from six import BytesIO
from frappe.utils import cint,today,flt,date_diff,add_days,add_months,date_diff,getdate,formatdate,cint,cstr
from frappe.utils.file_manager import get_file
import csv
import io
from frappe import _
from frappe.utils import getdate, get_site_path
from dongwoo.mark_attendance import mark_att_with_employee
from dongwoo.custom import process_attendance_upload,cancel_attendance_upload
from frappe.utils.background_jobs import enqueue
class AttendanceUpload(Document):
    
    def on_cancel(self):
        frappe.msgprint('Cancelling related records. Kindly check after few minutes.')
        doc_name=self.name
        enqueue(cancel_attendance_upload, queue='default', timeout=6000, event='create_attendance',doc_name=doc_name)
        

    def on_submit(self):
        frappe.msgprint('Attendance and Shift assignment are updating in background. Kindly check after few minutes.')
        doc_name=self.name
        enqueue(process_attendance_upload, queue='default', timeout=6000, event='create_attendance',doc_name=doc_name)

    def create_attendance_from_csv(self, file_obj):
        reader = csv.reader(file_obj)
        rows = list(reader)

        if len(rows) < 3:
            frappe.throw(_("The uploaded CSV doesn't have enough rows."))

        dates = get_dates(self.from_date, self.to_date)
        num_days = len(dates)
        for row in rows[2:]:  
            employee_id = row[1].strip() if len(row) > 1 else ""
            emptype = frappe.db.get_value("Employee", employee_id, 'employee_type')
            if not employee_id:
                continue

            col_idx = 3
            status_values = row[col_idx: col_idx + num_days]
            col_idx += num_days
            ot_values = row[col_idx: col_idx + num_days]
            col_idx += num_days
            shift_values = row[col_idx: col_idx + num_days]
            col_idx += num_days
            # for date in dates:
            for i, date in enumerate(dates):
                # if col_idx + 2 >= len(row): 
                #     break

                # status = row[col_idx].strip()
                # overtime = row[col_idx + 1].strip()
                # shift = row[col_idx + 2].strip()
                # col_idx += 3 

                # if not status:
                #     status = 'A'
                status = (status_values[i] or "A").strip()       
                overtime = (ot_values[i] or "0").strip()         
                shift = (shift_values[i] or "").strip() 

                doj=frappe.db.get_value('Employee',{'name':employee_id},['date_of_joining']) 
                relieving=frappe.db.get_value('Employee',{'name':employee_id},['relieving_date'])
                if relieving:
                    if getdate(relieving) <= getdate(date):
                        eligible="Yes"
                    else:
                        eligible="No"
                else:
                    eligible="Yes"
                if getdate(date) >= getdate(doj) and eligible=="Yes":
                    attendance_name = frappe.db.get_value("Attendance", {
                        "employee": employee_id,
                        "attendance_date": date,
                        "docstatus": ["!=", 2]
                    }, "name")

                    if not attendance_name:
                        doc = frappe.new_doc("Attendance")
                        doc.employee = employee_id
                        doc.attendance_date = date
                    else:
                        doc = frappe.get_doc("Attendance", attendance_name)

                    status_given = status.upper()
                    if status_given == "P":
                        doc.status = "Present"
                    elif status_given == "HD":
                        doc.status = "Half Day"
                    else:
                        doc.status = "Absent"
                    
                    if shift and frappe.db.exists('Shift Type', {'name': shift}):
                        doc.shift = shift
                    doc.attendance_upload = self.name
                    doc.overtime_hours = float(overtime) if overtime else 0.0
                    if not attendance_name:
                        doc.insert(ignore_permissions=True)
                        if doc.status == 'Present':
                            doc.submit()
                        frappe.db.commit()
                    else:
                        doc.save(ignore_permissions=True)
                        if doc.status == 'Present' and doc.docstatus == 0:
                            doc.submit()
                    if shift and frappe.db.exists('Shift Type', {'name': shift}):
                        # doc.shift = shift
                        if shift == 'WW':
                            overlapping_assignments = frappe.get_all('Shift Assignment',
                                filters={
                                    'employee': employee_id,
                                    'docstatus': ['!=', 2],
                                    'start_date': date,
                                    # 'end_date': ['>=', date]
                                },
                                fields=['name', 'docstatus']
                            )
                            if overlapping_assignments:
                                for assignment in overlapping_assignments:
                                    sa = frappe.get_doc('Shift Assignment', assignment.name)
                                    if sa.docstatus == 1:
                                        if sa.shift_type!='WW':
                                            sa.cancel()
                                            frappe.db.commit()
                                            shift_assign = frappe.new_doc('Shift Assignment')
                                            shift_assign.employee = employee_id
                                            shift_assign.shift_type = 'WW'
                                            shift_assign.schedule = self.name
                                            shift_assign.start_date = date
                                            shift_assign.end_date = date
                                            shift_assign.save(ignore_permissions=True)
                                            shift_assign.submit()

                                    else:
                                        shift_assign = frappe.new_doc('Shift Assignment')
                                        shift_assign.employee = employee_id
                                        shift_assign.shift_type = 'WW'
                                        shift_assign.schedule = self.name
                                        shift_assign.start_date = date
                                        shift_assign.end_date = date
                                        shift_assign.save(ignore_permissions=True)
                                        shift_assign.submit()

                            else:
                                shift_assign = frappe.new_doc('Shift Assignment')
                                shift_assign.employee = employee_id
                                shift_assign.shift_type = 'WW'
                                shift_assign.schedule = self.name
                                shift_assign.start_date = date
                                shift_assign.end_date = date
                                shift_assign.save(ignore_permissions=True)
                                shift_assign.submit()
                    
        
            dwsi_ot = flt(row[-1])  
            contractor_ot = flt(row[-2]) 
            if emptype=='Contract Employee':
                if dwsi_ot > 0 or contractor_ot > 0:
                    if not frappe.db.exists("OT Type", {"employee": employee_id, "from_date": self.from_date, "to_date": self.to_date}):
                        ot_doc = frappe.new_doc("OT Type")
                        ot_doc.employee=employee_id
                        ot_doc.dwsi_ot=dwsi_ot
                        ot_doc.contractor_ot=contractor_ot
                        ot_doc.from_date = self.from_date
                        ot_doc.to_date = self.to_date
                        ot_doc.upload_attendance= self.name
                        ot_doc.insert(ignore_permissions=True)
                        frappe.db.commit()
                    else:
                        ot_doc = frappe.get_doc("OT Type", {"employee": employee_id, "from_date": self.from_date, "to_date": self.to_date})
                        ot_doc.dwsi_ot = dwsi_ot
                        ot_doc.contractor_ot = contractor_ot
                        ot_doc.upload_attendance= self.name
                        ot_doc.save(ignore_permissions=True)
                        frappe.db.commit()

                    


    


@frappe.whitelist()
def get_template(from_date, to_date, department=None, designation=None, name=None):
    args = frappe.local.form_dict
    csv_file = make_csv(args)
    filename = "Attendance_Template"
    frappe.response['filename'] = filename + '.csv'
    frappe.response['filecontent'] = csv_file.getvalue()
    frappe.response['type'] = 'binary'

def make_csv(args):
    output = io.StringIO()
    writer = csv.writer(output)
    date_headers = get_dates(args['from_date'], args['to_date'])
    write_headers(writer, date_headers)
    employees = get_employees(args)
    sr_no = 1
    for emp in employees:
        row = [sr_no, emp.name , emp.employee_name]
        writer.writerow(row)
        sr_no += 1

    output.seek(0)
    return output

def get_dates(from_date, to_date):
    start_date = getdate(from_date)
    end_date = getdate(to_date)
    delta = end_date - start_date
    return [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(delta.days + 1)]

def write_headers(writer, date_headers):
    first_row = ['Sr No.', 'Employee','Employee Name']
    for _ in range(3): 
        for date in date_headers:
            first_row.extend([datetime.strptime(date, "%Y-%m-%d").strftime("%d-%b")])
    writer.writerow(first_row)
   
    
    second_row = ['', '','']
    # for _ in date_headers:
    #     second_row.extend(['Status', 'OT', 'Shift'])  
    # second_row.extend(['Cont OT', 'DWSI OT']) 
    # writer.writerow(second_row)
    for _ in date_headers:
        second_row.extend(['Status'])
    for _ in date_headers:
        second_row.extend(['OT'])   
    for _ in date_headers:
        second_row.extend(['Shift'])    
    second_row.extend(['Cont OT', 'DWSI OT']) 
    writer.writerow(second_row)
    # for _ in date_headers:s
    #     second_row.extend(['OT'])  
    # second_row.extend(['Cont OT', 'DWSI OT']) 
    # writer.writerow(second_row)

def get_employees(args):
    filters = {'status': 'Active'}
    dept=frappe.db.get_value("Attendance Upload",{'name':args.name},['department'])
    if dept=='All Departments':
        dept=''
    cat=frappe.db.get_value("Attendance Upload",{'name':args.name},['category'])
    cont=frappe.db.get_value("Attendance Upload",{'name':args.name},['contractor'])
    if cat and dept:
        if cat=='Contract Employee' and cont:
            employees = frappe.db.get_all('Employee', filters={'status':'Active','department':dept,'employee_type':cat,'contractor':cont}, fields=['name', 'employee_name'])
        else:
            employees = frappe.db.get_all('Employee', filters={'status':'Active','department':dept,'employee_type':cat}, fields=['name', 'employee_name'])
    elif cat and not dept:
        if cat=='Contract Employee' and cont:
            employees = frappe.db.get_all('Employee', filters={'status':'Active','employee_type':cat,'contractor':cont}, fields=['name', 'employee_name'])
        else:
            employees = frappe.db.get_all('Employee', filters={'status':'Active','employee_type':cat}, fields=['name', 'employee_name'])
    
    elif not cat and  dept:
        employees = frappe.db.get_all('Employee', filters={'status':'Active','department':dept}, fields=['name', 'employee_name'])
    else:
        employees = frappe.db.get_all('Employee', filters={'status':'Active'}, fields=['name', 'employee_name'])    
    return employees
