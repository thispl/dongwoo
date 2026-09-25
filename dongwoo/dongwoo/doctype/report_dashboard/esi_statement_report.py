import frappe
import datetime
import math
from frappe.utils import cstr, add_days, date_diff, getdate, format_date
from frappe import _, bold
from frappe.utils.csvutils import UnicodeWriter, read_csv_content
from frappe.utils.file_manager import get_file
from frappe.model.document import Document
from frappe.utils.background_jobs import enqueue
from datetime import date, timedelta, datetime
import openpyxl
from openpyxl import Workbook
import openpyxl
import xlrd
import re
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import GradientFill, PatternFill
from six import BytesIO, string_types
from openpyxl.styles.numbers import FORMAT_PERCENTAGE
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,format_date,
    nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime)



@frappe.whitelist()
def download():
    filename = 'ESI Statement'
    test = build_xlsx_response(filename)


@frappe.whitelist()
def make_xlsx(data, sheet_name=None, wb=None, column_widths=None):
    args = frappe.local.form_dict
    column_widths = column_widths or []
    if wb is None:
        wb = openpyxl.Workbook()
    ws = wb.create_sheet(sheet_name, 0)

    start_date=getdate(args.start_date)
    attmonth=start_date.strftime('%B')
    att_year = start_date.year
    previous_dept=None
    count=0
    sub_days_paid=0
    grand_days_paid=0
    sub_stipend=0
    grand_stipend=0
    sub_ot=0
    grand_ot=0
    sub_att_bonus=0
    grand_att_bonus=0
    sub_shift=0
    grand_shift=0
    sub_esi=0
    grand_esi=0
    sub_day_present=0
    grand_day_present=0
    sub_esi_wage=0
    grand_esi_wage=0
    sub_75=0
    grand_75=0
    sub_25=0
    grand_25=0
    sub_total=0
    grand_total=0

    employee_details = frappe.db.sql("""
    SELECT e.bank_ac_no AS 'AC No', e.employee, e.first_name AS 'Employee Name', s.employee_name AS 'Salary Slip Ename', e.mop, e.employee_type AS 'Employee Type',
        e.designation AS 'Designation', e.employee_type AS 'Etype', e.department AS 'Department', e.uan_number AS "UAN NO", e.esi_number AS "Esi", e.date_of_joining AS 'Date of Joining',
        s.payment_days AS 'Payment Days', s.leave_without_pay AS 'LOP',s.absent_days AS 'ABS', s.total_working_days AS 'Days in Month',
        e.basic AS 'Basic Pay', e.house_rent_allowance AS 'HRA', e.medical_allowance AS 'Medical Allowance', e.conveyance_allowance AS 'Conveyance',
        e.education_allowance AS 'Education Allowance', e.leave_and_travel_allowance AS 'LTA', e.dress_allowance AS 'Dress Allowance', e.gross_pay AS 'Fixed Gross', 
        s.name AS 'Name', s.total_deduction AS 'Total Deduction'
    FROM `tabEmployee` e
    INNER JOIN `tabSalary Slip` s ON e.name = s.employee
    INNER JOIN `tabDepartment` d ON e.department = d.name
    INNER JOIN `tabDesignation` de ON de.name = e.designation
    WHERE e.name = s.employee and s.start_date <= %s AND s.end_date >= %s
    ORDER BY d.order_value, e.employee_type, de.order, e.date_of_joining
""", (args.start_date, args.end_date), as_dict=True)

    header1 = ['ESI STATEMENT'+ ' - '+str(attmonth).upper() + ' '+ str(att_year)]
    ws.append(header1)    
    header2 = ['S.No','DEPT','EMP NO','NAMES','ESI IP NO','DATE OF JOINING','No.of Days Paid ','STIPEND CALCULATION','','','','','','WORKINGS FOR PAYMENT','','','','']
    ws.append(header2)   
    header3 = ['','','','','','','','Stipend','OT','Attendance Bonus','Shift Allow',' ESI @.75%','','No.of Days Present','ESI Wage','0.75%','3.25%','Total']
    ws.append(header3)   
    for row in employee_details:
        if row['Etype']=='D . Trainee':
            count+= 1
            stipen_paid = frappe.db.get_value("Salary Detail", {"parent": row['Name'] , "salary_component": "Stipend"},"amount") or 0.0
            ot_paid=frappe.get_value("Salary Detail",{'parent':row['Name'] ,"salary_component":'Overtime'},"amount") or 0.0
            att_bonus_paid=frappe.get_value("Salary Detail",{'parent':row['Name'] ,"salary_component":'Attendance Bonus'},"amount") or 0.0
            shift_paid=frappe.get_value("Salary Detail",{'parent':row['Name'] ,"salary_component":"Shift Allowance"},"amount") or 0.0
        
        
            if stipen_paid<21000:
                esi_paid=math.ceil((stipen_paid+ot_paid+att_bonus_paid+shift_paid)*0.0075)
            else:
                esi_paid=0

            if stipen_paid<21000:
                present_25=((stipen_paid+ot_paid+att_bonus_paid+shift_paid)*0.0325)
                present_25=round(present_25)
            else:
                present_25=0
            wage_present=(stipen_paid+ot_paid+att_bonus_paid+shift_paid)
            total_tot=(esi_paid+present_25)     
        
            if previous_dept is None:
                    previous_dept=row['Department']
            else:
                if previous_dept!=row['Department']:
                    ws.append(['','SUBTOTAL', '','','','',sub_days_paid,sub_stipend,sub_ot,sub_att_bonus,
                            sub_shift,sub_esi,'',sub_day_present,sub_esi_wage,sub_75, sub_25,sub_total ])
                    previous_dept=row['Department']
                    sub_days_paid=0
                    sub_stipend=0
                    sub_ot=0
                    sub_att_bonus=0
                    sub_shift=0
                    sub_esi=0
                    sub_ot=0
                    sub_day_present=0
                    sub_esi_wage=0
                    sub_75=0
                    sub_25=0
                    sub_total=0
                
            sub_days_paid+=row['Payment Days']
            sub_stipend+=stipen_paid        
            sub_ot+=ot_paid
            sub_att_bonus+=att_bonus_paid
            sub_shift+=shift_paid
            sub_esi+=esi_paid
            sub_day_present+=row['Payment Days']
            sub_esi_wage+=wage_present
            sub_75+=esi_paid
            sub_25=present_25
            sub_total=total_tot


            grand_days_paid+=row['Payment Days']
            grand_stipend+=stipen_paid
            grand_ot+=ot_paid
            grand_att_bonus+=att_bonus_paid
            grand_shift+=shift_paid
            grand_esi+=esi_paid
            grand_day_present+=row['Payment Days']
            grand_esi_wage+=wage_present
            grand_75+=esi_paid
            grand_25+=present_25
            grand_total+=total_tot

            ws.append([
                        count,
                        row['Department'],
                        row['employee'], 
                        row['Employee Name'],
                        row['Esi'],
                        row['Date of Joining'],
                        row['Payment Days'],stipen_paid,ot_paid,att_bonus_paid,shift_paid,esi_paid,'',
                        row['Payment Days'],wage_present,esi_paid,present_25,total_tot

                    ])
    
    ws.append(['','SUBTOTAL', '','','','',sub_days_paid,sub_stipend,sub_ot,sub_att_bonus,
                    sub_shift,sub_esi,'',sub_day_present,sub_esi_wage,sub_75, sub_25,sub_total ])
        
    ws.append(['','GRANDTOTAL', '','','','',grand_days_paid, grand_stipend,grand_ot,grand_att_bonus,
        grand_shift, grand_esi, '',grand_day_present,grand_esi_wage,grand_75, grand_25, grand_total ])   
    
    for i in range(1,8):
        ws.merge_cells(start_row=2,start_column=i,end_row=3,end_column=i)

    ws.merge_cells(start_row=2,start_column=1,end_row=3,end_column=1)
    ws.merge_cells(start_row=2,start_column=2,end_row=3,end_column=2)
    ws.merge_cells(start_row=2,start_column=3,end_row=3,end_column=3)
    ws.merge_cells(start_row=2,start_column=4,end_row=3,end_column=4)
    ws.merge_cells(start_row=2,start_column=5,end_row=3,end_column=5)
    ws.merge_cells(start_row=2,start_column=6,end_row=3,end_column=6)

    ws.merge_cells(start_row=1,start_column=1,end_row=1,end_column=18)
    ws.merge_cells(start_row=2,start_column=8,end_row=2,end_column=11)
    ws.merge_cells(start_row=2,start_column=14,end_row=2,end_column=18)

    border = Border(left=Side(border_style='thin', color='000000'),
            right=Side(border_style='thin', color='000000'),
            top=Side(border_style='thin', color='000000'),
            bottom=Side(border_style='thin', color='000000'))
    for header in ws.iter_rows(min_row=1, max_row=ws.max_row,min_col=1, max_col=12):
        for cell in header:
            cell.border = border
    for header in ws.iter_rows(min_row=1, max_row=ws.max_row,min_col=14, max_col=18):
        for cell in header:
            cell.border = border

    for header in ws.iter_rows(min_row=2, max_row=3,min_col=1, max_col=12):
        for cell in header:
            cell.fill = PatternFill(fgColor='eefa0f', fill_type="solid")
            cell.border = border
    max_row = ws.max_row
    previous_department = None
    merge_start_row = None

    for row in range(1, max_row + 1):
        cell_value = ws.cell(row=row, column=2).value

        # Apply center alignment to the current cell
        ws.cell(row=row, column=2).alignment = Alignment(horizontal='center', vertical='center')
        
        if cell_value is None or cell_value.strip() == '':
            previous_department = None
            merge_start_row = None
        elif cell_value == previous_department:
            if merge_start_row is not None:
                end_row = row
                ws.merge_cells(start_row=merge_start_row, start_column=2, end_row=end_row, end_column=2)
        else:
            if merge_start_row is not None and previous_department is not None:
                end_row = row - 1
                ws.merge_cells(start_row=merge_start_row, start_column=2, end_row=end_row, end_column=2)
            
            previous_department = cell_value
            merge_start_row = row 
    for allow in ws.iter_rows(min_row=1, max_row=ws.max_row,min_col=13, max_col=13):
        for cell in allow:
            cell.fill = PatternFill(fgColor="f5f2eb", fill_type = "solid")      
    yellow = PatternFill(start_color='fff600',end_color='fff600',fill_type='solid')
    green = PatternFill(start_color='98c91c',end_color='98c91c',fill_type='solid')
    for rows in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=2, max_col=2):
        for cell in rows:
            if cell.value == 'SUBTOTAL':
                for cell in ws[cell.row]:
                    cell.fill = green
            if cell.value == 'GRANDTOTAL' or cell.value=='TOTAL FOR WORKERS' or cell.value=='TOTAL FOR TRAINEE' or cell.value=='TOTAL FOR STAFF':
                for cell in ws[cell.row]:
                    cell.fill = yellow
    for header1 in ws.iter_rows(min_row=2, max_row=3,min_col=14, max_col=18):
        for cell in header1:
            cell.fill = PatternFill(fgColor='eefa0f', fill_type="solid")
            cell.border = border
    

    ws.column_dimensions['F'].width = 20
    ws.column_dimensions['D'].width = 20
    ws.column_dimensions['I'].width = 20
    ws.column_dimensions['J'].width = 20
    ws.column_dimensions['K'].width = 20
    ws.column_dimensions['N'].width = 20

    ws.row_dimensions[3].height = 30

    align_center = Alignment(horizontal='center',vertical='center') 
    for align in ws.iter_rows(min_row=1, max_row=ws.max_row,min_col=1, max_col=18):
            for cell in align:
                cell.alignment = align_center
    for allow in ws.iter_rows(min_row=1, max_row=ws.max_row,min_col=13, max_col=13):
        for cell in allow:
            cell.fill = PatternFill(fgColor="f5f2eb", fill_type = "solid") 
    xlsx_file=BytesIO()
    wb.save(xlsx_file)
    return xlsx_file

@frappe.whitelist()
def build_xlsx_response(filename):
    xlsx_file = make_xlsx(filename)
    frappe.response['filename'] = filename + '.xlsx'
    frappe.response['filecontent'] = xlsx_file.getvalue()
    frappe.response['type'] = 'binary'



        





           
