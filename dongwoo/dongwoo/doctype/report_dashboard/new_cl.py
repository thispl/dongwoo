import frappe
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime, timedelta
import calendar
import io
from datetime import date
from openpyxl.utils import column_index_from_string

@frappe.whitelist()
def download(start_date, end_date, contractor):

    wb = Workbook()
    ws = wb.active
    ws.title = "Salary Statement"

    # ---------------- Date ----------------
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    month_name = calendar.month_name[start_dt.month].upper()
    year = start_dt.year
    month = start_dt.month

    # ---------------- Styles ----------------
    center = Alignment(horizontal="center", vertical="center", wrap_text=True)

    thin = Side(style="thin")
    border_all = Border(left=thin, right=thin, top=thin, bottom=thin)

    # ---- Colors ----
    blue_fill   = PatternFill("solid", fgColor="ADD8E6")
    pink_fill   = PatternFill("solid", fgColor="FFC0CB")
    red_fill    = PatternFill("solid", fgColor="FF7F7F")
    cement_fill = PatternFill("solid", fgColor="D9D9D9")
    green_fill  = PatternFill("solid", fgColor="90EE90")
    green_fill_new = PatternFill(start_color="92D050",end_color="92D050",fill_type="solid")
    light_orange_fill = PatternFill(start_color="F4B084",end_color="F4B084",fill_type="solid")
    yellow_fill = PatternFill("solid", fgColor="FFFF00")

    dark_orange = PatternFill("solid", fgColor="FF8C00")
    violet      = PatternFill("solid", fgColor="D8BFD8")
    dark_green  = PatternFill("solid", fgColor="006400")

    title_font = Font(bold=True, underline="single")
    bold_font = Font(bold=True)

    # ---------------- Helpers ----------------
    def apply_border(cell_range):
        for row in ws[cell_range]:
            for cell in row:
                cell.border = border_all

    def merge_and_set(cell_range, value, fill=None):
        ws.merge_cells(cell_range)
        c = ws[cell_range.split(":")[0]]
        c.value = value
        c.alignment = center
        if fill:
            c.fill = fill
        apply_border(cell_range)

    def set_cell(row, col, value, fill=None):
        cell = ws.cell(row=row, column=col, value=value)
        cell.alignment = center
        if fill:
            cell.fill = fill
        cell.border = border_all

    def build_step_sum(col_letter, start_row, end_row, step=4):
        cells = []
        r = start_row
        while r <= end_row:
            cells.append(f"{col_letter}{r}")
            r += step
        return f"=SUM({','.join(cells)})" if cells else "=0"

    def merge_emp_4_rows(ws, row_start, col_start, col_end, border):
        """
        Merge each column vertically for 4 rows (one employee block)
        """
        for col in range(col_start, col_end + 1):
            ws.merge_cells(
                start_row=row_start,
                start_column=col,
                end_row=row_start + 3,
                end_column=col
            )

            for r in range(row_start, row_start + 4):
                c = ws.cell(row=r, column=col)
                c.alignment = center
                c.border = border

    def get_actual_shift_code(att):
        if not att.shift:
            return ""

        base_shift = SHIFT_MAP_CHAR.get(att.shift, "")

        if att.status == "Present":
            return base_shift

        if att.status == "Half Day":
            return f"H{base_shift}"   # HA / HB / HC

        return ""


    ws.column_dimensions["C"].width = 10
    ws.column_dimensions["D"].width = 10
    ws.column_dimensions["E"].width =20
    ws.column_dimensions["F"].width = 15
    ws.column_dimensions["G"].width = 15
    ws.column_dimensions["H"].width = 10
    ws.column_dimensions["I"].width = 15
    ws.column_dimensions["BH"].width = 15
    ws.column_dimensions["BI"].width = 15
    ws.column_dimensions["BJ"].width = 15
    ws.column_dimensions["BM"].width = 15
    ws.column_dimensions["BO"].width = 15
    ws.column_dimensions["BQ"].width = 15
    ws.column_dimensions["BT"].width = 15
    ws.column_dimensions["CM"].width = 15
    ws.column_dimensions["CN"].width = 15


    # ---------------- Main Title ----------------
    ws.merge_cells("B2:F2")
    ws["B2"] = f"{contractor} SALARY STATEMENT"
    ws["B2"].font = title_font
    ws["B2"].alignment = center
    apply_border("B2:F2")

    ws.merge_cells("B4:F4")
    ws["B4"] = f"FOR THE MONTH OF {month_name} - {year}"
    ws["B4"].font = bold_font
    ws["B4"].alignment = center
    apply_border("B4:F4")

    # ---------------- Color Indicators (I Column) ----------------
    color_cells = {
        "I2": blue_fill,
        "I3": pink_fill,
        "I4": red_fill,
        "I5": cement_fill,
    }

    for cell, fill in color_cells.items():
        ws[cell].fill = fill
        ws[cell].border = border_all

    # ---------------- J–L Section ----------------
    jl_data = {
        "J2:L2": "COMP OFF",
        "J3:L3": "WEEKLY OFF",
        "J4:L4": f"{contractor} SCOPE OT",
        "J5:L5": "DWSI SCOPE OT",
    }

    for rng, text in jl_data.items():
        ws.merge_cells(rng)
        ws[rng.split(":")[0]] = text
        ws[rng.split(":")[0]].alignment = center
        apply_border(rng)

    # ---------------- M–N Section ----------------
    ws.merge_cells("M1:N1")
    ws["M1"] = "Schedule"
    ws["M1"].fill = green_fill
    ws["M1"].alignment = center
    apply_border("M1:N1")

    mn_data = {
        "M2:N2": "Worked",
        "M3:N3": "Continue",
        "M4:N4": "NAL",
        "M5:N5": "AL",
    }

    for rng, text in mn_data.items():
        ws.merge_cells(rng)
        c = ws[rng.split(":")[0]]
        c.value = text
        c.alignment = center
        if text in ["NAL", "AL"]:
            c.fill = yellow_fill
        apply_border(rng)

    # ---------------- O–T Section ----------------
    ot_data = {
        "O1:T1": ("1: A Shift, 2: B Shift, 3: C Shift, 4: W off", green_fill),
        "O2:T2": ("A: A Shift, B: B Shift, C: C Shift, H: W off", None),
        "O3:T3": ('16-"A" & "B" Shift, 14 - "C" Shift', None),
        "O4:T4": ("xA & xB & xC : Non Approved Leave & Shift", yellow_fill),
        "O5:T5": ("oA & oB & oC : Approved Leave & Shift", yellow_fill),
    }

    for rng, (text, fill) in ot_data.items():
        ws.merge_cells(rng)
        c = ws[rng.split(":")[0]]
        c.value = text
        c.alignment = center
        if fill:
            c.fill = fill
        apply_border(rng)

    # ---------------- Fixed Headers ----------------
    fixed_headers = [
        "S.NO","DEPT","NEW EMP ID","NAME","DOJ","DOB","CATEGORY"
    ]

    col = 2 
    for head in fixed_headers:
        letter = get_column_letter(col)
        merge_and_set(f"{letter}7:{letter}8", head)
        col += 1

    # ---------------- Work Type Column ----------------
    work_col = col

    merge_and_set(
        f"{get_column_letter(work_col)}7:{get_column_letter(work_col)}8",
        "TYPE"
    )

    col += 1
    company_holidays = set(
        h.holiday_date for h in frappe.get_all(
            "Holiday",
            filters={
                "holiday_date": ["between", [start_date, end_date]]
            },
            fields=["holiday_date"]
        )
    )


    # ---------------- Dynamic Days ----------------
    total_days = calendar.monthrange(year, start_dt.month)[1]

    date_start_col = col

    for day in range(1, total_days + 1):
        date_obj = datetime(year, start_dt.month, day)
        curr_date = date_obj.date()

        day_name = date_obj.strftime("%a").upper()

        # ---- Decide Fill ----
        if curr_date in company_holidays:
            fill = blue_fill
        elif day_name == "SUN":
            fill = yellow_fill
        else:
            fill = None

        # Row 7 – Date Number
        set_cell(7, col, day, fill)

        # Row 8 – Day Name
        set_cell(8, col, day_name, fill)

        # Column width = 6
        ws.column_dimensions[get_column_letter(col)].width = 6

        col += 1


    # ---------------- Schedule ----------------
    start = col
    merge_and_set(
        f"{get_column_letter(start)}7:{get_column_letter(start+5)}7",
        "SCHEDULE"
    )

    for i, txt in enumerate(["A","B","C","WRK","H","TOTAL"]):
        fill = violet if txt not in ["A","B","C","WRK","TOTAL"] else None
        set_cell(8, start + i, txt, fill)
    col += 6

    # ---------------- Actual Attendance ----------------
    actual_start_col = col
    start = col
    merge_and_set(
        f"{get_column_letter(start)}7:{get_column_letter(start+6)}7",
        "ACTUAL ATTENDED"
    )

    actual_cols = ["A","B","C","WRK","NH/FH","W OFF","TOTAL"]
    for i, txt in enumerate(actual_cols):
        fill = green_fill_new if txt not in ["W OFF","TOTAL"] else None
        set_cell(8, start + i, txt, fill)
    col += 7

    # ---------------- Leave ----------------
    start = col
    merge_and_set(
        f"{get_column_letter(start)}7:{get_column_letter(start+2)}7",
        "LEAVE"
    )

    leave_cols = [("NAL",yellow_fill),("AL",yellow_fill),("HALF DAY",green_fill)]
    for i,(txt,fill) in enumerate(leave_cols):
        set_cell(8, start + i, txt, fill)
    col += 3

    contractor_doc = frappe.get_doc("Contractor", contractor)
    service_charge = contractor_doc.service_charges or 0
    con_name = contractor_doc.name or ""
    service_charge_label = f"SERVICE CHARGE {service_charge}%"
    con_ot = f"{con_name} OT%"
    con_ot_amount = f"{con_name} OT AMOUNT%"

    # ---------------- Final Headers ----------------
    final_headers = [
        ("TOTAL",None),
        ("CONT (A)",None),
        ("TOTAL OT HOURS",dark_orange),
        ("EXISTING GROSS 03-2025",yellow_fill),
        ("INCREASE",None),
        ("REVISED GROSS 04-2025",cement_fill),
        ("OT RATE",None),
        ("SHOE",None),
        ("UNIFORM",None),
        ("TOTAL",None),
        ("TOTAL MAN DAYS",None),
        ("TOTAL WAGE",None),
        ("PF RESTRICTED WAGE PER DAY",blue_fill),
        ("PF WAGE",blue_fill),
        ("ACTUAL PF 13%",None),
        ("BASIC+DA",violet),
        ("HRA",violet),
        ("WASHING ALLOWANCE",violet),
        ("FIXED GROSS FOR ESI CALC.",violet),
        ("ESI WAGE",violet),
        ("ESI OT WAGE",violet),
        ("ESI @ 3.25%",violet),
        ("OT HOURS",None),
        ("TOTAL OT AMOUNT",None),
        ("ATTEN. BONUS",None),
        ("FEST. ALLOW.",None),
        ("GRAND TOTAL",None),
        (service_charge_label, None),
        ("DWSI OT",green_fill),
        (con_ot,red_fill),
        ("DWSI OT AMOUNT",green_fill),
        (con_ot_amount,red_fill),
        ("FESTIVAL 1 DAY SALARY",dark_green),
        ("FESTIVAL SERVICE CHARGES",blue_fill),
        ("SERVICE CHARGE DEDUCTION",dark_green),
        ("SERVICE CHARGE DEDUCTION",blue_fill),
    ]

    final_header_start_col = col
    for text, fill in final_headers:
        letter = get_column_letter(col)
        merge_and_set(f"{letter}7:{letter}8", text, fill)
        col += 1
    final_header_end_col = col - 1

        # ================= Employee Data Section =================

    # 1. Get Salary Slips (Draft + Submitted)
    salary_slips = frappe.get_all(
        "Salary Slip",
        filters={
            "start_date": ["between", [start_date, end_date]],
            "docstatus": ["in", [0, 1]]
        },
        fields=["employee"]
    )

    if not salary_slips:
        frappe.throw("No Salary Slips found for the selected month")
    emp_list = list(set([s.employee for s in salary_slips]))

    # 2. Fetch Employee Details
    employees = frappe.get_all(
        "Employee",
        filters={"name": ["in", emp_list]},
        fields=[
            "name",
            "employee_name",
            "department",
            "date_of_joining",
            "date_of_birth",
            "designation"
        ]
    )

    # 3. Attach Department Order
    for emp in employees:
        emp["dept_order"] = frappe.get_value(
            "Department",
            emp.department,
            "order_for_contractor"
        ) or 999

    # 4. Sort → Department Order, then DOJ
    employees.sort(
        key=lambda x: (x.department, x.date_of_joining or datetime.max)
    )

    # ================= Write Employee Rows =================

    start_row = 9
    sno = 1
    current_dept = None
    thin_border = Border(left=thin, right=thin, top=thin, bottom=thin)
    dept_start_row = None
    subtotal_rows = []

    for emp in employees:

        if current_dept is None:
            current_dept = emp.department
            dept_start_row = start_row

        elif current_dept != emp.department:
            dept_end_row = start_row - 1
            subtotal_row = start_row
            summary_start_col = day_loop_end_col + 1
            for col in range(date_start_col, day_loop_end_col + 1):
                cell = ws.cell(subtotal_row, col)
                cell.border = thin_border
                cell.fill = yellow_fill
                cell.alignment = center
            for col in range(summary_start_col, final_header_end_col + 1):
                col_letter = get_column_letter(col)
                cell = ws.cell(subtotal_row, col)
                cell.value = f"=SUM({col_letter}{dept_start_row}:{col_letter}{dept_end_row})"
                cell.number_format = '#,##0'
                cell.fill = yellow_fill
                cell.alignment = center
                cell.border = thin_border
            subtotal_rows.append(subtotal_row)
            ws.merge_cells(
                start_row=subtotal_row,
                start_column=2,
                end_row=subtotal_row,
                end_column=date_start_col - 1
            )

            cell = ws.cell(subtotal_row, 2, "SUBTOTAL")
            cell.fill = yellow_fill
            cell.alignment = center
            cell.border = thin_border

            start_row += 1   
            current_dept = emp.department
            dept_start_row = start_row

        row_start = start_row
        
        row_end = start_row + 3  # 4 rows per employee

        # -------- Fixed Columns (S.NO → CATEGORY) --------
        fixed_data = [
            sno,
            emp.department,
            emp.name,
            emp.employee_name,
            emp.date_of_joining.strftime("%d-%m-%Y") if emp.date_of_joining else "",
            emp.date_of_birth.strftime("%d-%m-%Y") if emp.date_of_birth else "",
            emp.designation
        ]

        col_no = 2  # B column

        for value in fixed_data:
            ws.merge_cells(
                start_row=row_start,
                start_column=col_no,
                end_row=row_end,
                end_column=col_no
            )
            ws.cell(row=row_start, column=col_no, value=value).alignment = center
            apply_border(
                f"{get_column_letter(col_no)}{row_start}:{get_column_letter(col_no)}{row_end}"
            )
            col_no += 1

        cat_col = col_no  # CATEGORY next blank column

       
        # -------- Schedule / Actual / Continue / Work Spot --------
        labels = ["Schedule", "Actual", "Continue", "Work Spot"]

        for i, lbl in enumerate(labels):
            cell = ws.cell(
            row=row_start + i,
            column=work_col,
            value=lbl
        )
            cell.alignment = center
            cell.border = border_all
        
        workspot_row = row_start + 3

        col_no = date_start_col
        for day in range(1, total_days + 1):
            c = ws.cell(row=workspot_row, column=col_no)
            c.border = border_all
            c.alignment = center
            col_no += 1
        

        holiday_list = frappe.get_value(
            "Employee",
            emp.name,
            "holiday_list"
        )
        holiday_dates = set()

        if holiday_list:
            holidays = frappe.get_all(
                "Holiday",
                filters={
                    "parent": holiday_list,
                    "holiday_date": ["between", [start_date, end_date]]
                },
                fields=[
                    "holiday_date",
                    "national_holiday",
                    "festival_holiday"
                ]

            )

            holiday_dates = {h.holiday_date for h in holidays}

            holiday_map = {}

            for h in holidays:
                holiday_map[h.holiday_date] = {
                    "NH": h.national_holiday,
                    "FH": h.festival_holiday
                }

        attendance_list = frappe.get_all(
            "Attendance",
            filters={
                "employee": emp.name,
                "attendance_date": ["between", [start_date, end_date]],
                "docstatus": 1
            },
            fields=[
                "attendance_date",
                "shift",
                "status",
                "overtime_hours"
            ]
        )
        attendance_by_date = {}
        for att in attendance_list:
            attendance_by_date[att.attendance_date] = att

        leave_apps = frappe.get_all(
            "Leave Application",
            filters={
                "employee": emp.name,
                "from_date": ["<=", end_date],
                "to_date": [">=", start_date],
                "docstatus": 1,
                "status": "Approved"
            },
            fields=["from_date", "to_date"]
        )

        leave_dates = set()

        for la in leave_apps:
            d = la.from_date
            while d <= la.to_date:
                leave_dates.add(d)
                d += timedelta(days=1)

        def has_leave_on(date):
            return date in leave_dates


        SHIFT_MAP_CHAR = {
            "A": "A",
            "B": "B",
            "C": "C"
        }

        # -------- Schedule (Shift Assignment) --------
        SHIFT_MAP = {
            "A": 1,
            "B": 2,
            "C": 3,
            "WW": 4,
        }

        shift_assignments = frappe.get_all(
            "Shift Assignment",
            filters={
                "employee": emp.name,
                "start_date": ["between", [start_date, end_date]],
                "docstatus": 1
            },
            fields=["start_date", "shift_type"]
        )

        shift_by_date = {
            sa.start_date: sa.shift_type
            for sa in shift_assignments
        }

        schedule_row = row_start
        col_no = date_start_col

        for day in range(1, total_days + 1):
            curr_date = datetime(year, start_dt.month, day).date()

            shift = shift_by_date.get(curr_date)
            value = SHIFT_MAP.get(shift, "") if shift else ""

            # -------- Schedule value (row 1 of 4) --------
            sched_cell = ws.cell(
                row=row_start,
                column=col_no,
                value=value
            )

            sched_cell.alignment = center
            sched_cell.border = border_all

            # -------- COLOR LOGIC --------
            if curr_date in holiday_dates:
                for r in range(row_start, row_start + 4):
                    c = ws.cell(row=r, column=col_no)
                    c.fill = blue_fill
                    c.border = border_all
                    c.alignment = center
            else:
                sched_cell.fill = green_fill

            col_no += 1

        actual_row = row_start + 1
        continue_row = row_start + 2

        col_no = date_start_col

        half_day_count = 0.0
        al_count = 0.0
        nal_count = 0.0

        for day in range(1, total_days + 1):
            curr_date = datetime(year, start_dt.month, day).date()
            col = date_start_col + day - 1
            
            
            shift = shift_by_date.get(curr_date)
            att = attendance_by_date.get(curr_date)
            # ---------- ACTUAL ----------
            actual_value = ""
            actual_fill = None
            ot_hours = 0
            schedule_val = SHIFT_MAP.get(shift)
            if att:
                ot_hours = float(att.get("overtime_hours") or 0)
            # -------- HOLIDAY CHECK (TOP PRIORITY) --------
            if curr_date in holiday_map and ot_hours > 0:
                h = holiday_map[curr_date]

                if h.get("NH"):
                    actual_value = "NH"
                    actual_fill = light_orange_fill

                elif h.get("FH"):
                    actual_value = "FH"
                    actual_fill = light_orange_fill

            elif curr_date in holiday_map:
                if att:
                    shift_value = get_actual_shift_code(att)
                    if shift_value:
                        actual_value = shift_value

            # -------- WEEKLY OFF (Schedule = 4) --------
            elif schedule_val == 4:
                actual_value = "H"
                actual_fill = violet

            # -------- NORMAL PRESENT --------
            elif att:
                shift_value = get_actual_shift_code(att)  

                if shift_value:
                    actual_value = shift_value
            
            cell = ws.cell(
                row=actual_row,
                column=col_no,
                value=actual_value
            )
            cell.alignment = center
            cell.border = border_all
            if curr_date not in holiday_dates and actual_fill:
                cell.fill = actual_fill
            
            val = actual_value          
            if val in ("HA", "HB", "HC"):
                half_day_count += 0.5

                if has_leave_on(curr_date):
                    al_count += 0.5
                else:
                    nal_count += 0.5

            # ---------- CONTINUE (OT Hours) ----------
            ot_value = att.overtime_hours if att and att.overtime_hours else ""

            cell = ws.cell(
                row=continue_row,
                column=col_no,
                value=ot_value
            )
            cell.alignment = center
            cell.border = border_all
            if ot_value:
                cell.fill = red_fill

            col_no += 1

        day_loop_end_col = date_start_col + total_days - 1
        # ===== Schedule Summary (Excel Formula) =====

        start_letter = get_column_letter(date_start_col)
        end_letter   = get_column_letter(date_start_col + total_days - 1)

        summary_col = date_start_col + total_days
        r = schedule_row  

        # A
        ws.cell(r, summary_col).value = \
            f'=COUNTIF({start_letter}{r}:{end_letter}{r},1)'

        # B
        ws.cell(r, summary_col+1).value = \
            f'=COUNTIF({start_letter}{r}:{end_letter}{r},2)'
        # C
        ws.cell(r, summary_col+2).value = \
            f'=COUNTIF({start_letter}{r}:{end_letter}{r},3)'
        # WRK = A+B+C
        ws.cell(r, summary_col+3).value = \
            f'={get_column_letter(summary_col)}{r}+' \
            f'{get_column_letter(summary_col+1)}{r}+' \
            f'{get_column_letter(summary_col+2)}{r}'

        # H
        ws.cell(r, summary_col+4).value = \
            f'=COUNTIF({start_letter}{r}:{end_letter}{r},4)'

        # TOTAL = WRK + H
        ws.cell(r, summary_col+5).value = \
            f'={get_column_letter(summary_col+4)}{r}+' \
            f'{get_column_letter(summary_col+3)}{r}'

        # ===== Merge summary columns for 4 rows =====

        merge_start_row = start_row
        merge_end_row   = start_row + 3
        summary_start_col = date_start_col + total_days
        summary_end_col   = summary_start_col + 5   # A,B,C,WRK,H,TOTAL
        for col in range(summary_start_col, summary_end_col + 1):

            ws.merge_cells(
                start_row=merge_start_row,
                start_column=col,
                end_row=merge_end_row,
                end_column=col
            )

            top_cell = ws.cell(row=merge_start_row, column=col)
            top_cell.alignment = center
            for r in range(merge_start_row, merge_end_row + 1):
                ws.cell(row=r, column=col).border = border_all

        # ===== Actual Summary (Excel Formula) =====

        formula_row = row_start         
        data_row    = row_start + 1      

        start_letter = get_column_letter(date_start_col)
        end_letter   = get_column_letter(date_start_col + total_days - 1)

        summary_col = date_start_col + total_days + 6

        # A
        ws.cell(formula_row, summary_col).value = \
            f'=COUNTIF({start_letter}{data_row}:{end_letter}{data_row},"A")'

        # B
        ws.cell(formula_row, summary_col+1).value = \
            f'=COUNTIF({start_letter}{data_row}:{end_letter}{data_row},"B")'

        # C
        ws.cell(formula_row, summary_col+2).value = \
            f'=COUNTIF({start_letter}{data_row}:{end_letter}{data_row},"C")'

        # WRK = A+B+C
        ws.cell(formula_row, summary_col+3).value = \
            f'={get_column_letter(summary_col)}{formula_row}+' \
            f'{get_column_letter(summary_col+1)}{formula_row}+' \
            f'{get_column_letter(summary_col+2)}{formula_row}'

        # NH / FH
        ws.cell(formula_row, summary_col+4).value = (
            f'=COUNTIF({start_letter}{data_row}:{end_letter}{data_row},"NH")'
            f'+COUNTIF({start_letter}{data_row}:{end_letter}{data_row},"FH")'
        )

        # W OFF
        ws.cell(formula_row, summary_col+5).value = \
            f'=COUNTIF({start_letter}{data_row}:{end_letter}{data_row},"H")'

        # TOTAL
        ws.cell(formula_row, summary_col+6).value = \
            f'={get_column_letter(summary_col+3)}{formula_row}+' \
            f'{get_column_letter(summary_col+4)}{formula_row}+' \
            f'{get_column_letter(summary_col+5)}{formula_row}'

        merge_start_row = row_start
        merge_end_row   = row_start + 3

        for col in range(actual_start_col, actual_start_col + 7):
            ws.merge_cells(
                start_row=merge_start_row,
                start_column=col,
                end_row=merge_end_row,
                end_column=col
            )

            top_cell = ws.cell(row=merge_start_row, column=col)
            top_cell.alignment = center

            for r in range(merge_start_row, merge_end_row + 1):
                ws.cell(row=r, column=col).border = border_all

        # ===== Leave Data Merge =====

        leave_start_col = start   # NAL starts here
        leave_end_col   = start + 2

        merge_start_row = row_start
        merge_end_row   = row_start + 3

        ws.cell(row_start, leave_start_col).value     = nal_count      # NAL
        ws.cell(row_start, leave_start_col + 1).value = al_count       # AL
        ws.cell(row_start, leave_start_col + 2).value = half_day_count # HALF DAY

        for c in range(leave_start_col, leave_start_col + 3):
            ws.cell(row_start, c).alignment = center

        for c in range(leave_start_col, leave_end_col + 1):
            ws.merge_cells(
                start_row=merge_start_row,
                start_column=c,
                end_row=merge_end_row,
                end_column=c
            )

            top = ws.cell(row=merge_start_row, column=c)
            top.alignment = center

            for r in range(merge_start_row, merge_end_row + 1):
                ws.cell(row=r, column=c).border = border_all

        # TOTAL Calculation after Leave Clm
        final_total_col = leave_start_col + 3   # after HALF DAY

        ws.cell(row_start, final_total_col).value = \
            f'={get_column_letter(summary_col+6)}{row_start}+' \
            f'{get_column_letter(leave_start_col)}{row_start}+' \
            f'{get_column_letter(leave_start_col+1)}{row_start}+' \
            f'{get_column_letter(leave_start_col+2)}{row_start}'

        # CONT (A) Clmc Calculation
        start_letter = get_column_letter(date_start_col)
        end_letter   = get_column_letter(date_start_col + total_days - 1)  

        cont_col = final_total_col + 1

        ws.cell(row_start, cont_col).value = (
            f'=COUNTIF({start_letter}{continue_row}:{end_letter}{continue_row},16)'
            f'+COUNTIF({start_letter}{continue_row}:{end_letter}{continue_row},14)'
            f'+COUNTIF({start_letter}{continue_row}:{end_letter}{continue_row},6)'
            f'+COUNTIF({start_letter}{continue_row}:{end_letter}{continue_row},8)'
        )

        total_ot_col = cont_col + 1
        ws.cell(row_start, total_ot_col).value = \
            f'=SUM({start_letter}{continue_row}:{end_letter}{continue_row})'

        existing_gross = frappe.get_value("Employee", emp.name, "existing_gross") or 0
        ws.cell(row_start, total_ot_col+1).value = existing_gross
        increase = frappe.get_value("Employee", emp.name, "increase_amount") or 0
        ws.cell(row_start, total_ot_col+2).value = increase
        increase_col = total_ot_col + 2   
        cell = ws.cell(row=row_start, column=increase_col)
        cell.number_format = '0.00'
        revised_gross = frappe.get_value("Employee", emp.name, "revised_gross") or 0
        ws.cell(row_start, total_ot_col+3).value = revised_gross
        revised_col = total_ot_col + 3
        ws.cell(row_start, revised_col).value = revised_gross
        ws.cell(row_start, revised_col).number_format = '#,##0.00'


        ot_rate_col = revised_col + 1
        ws.cell(row_start, ot_rate_col).value = \
            f'=ROUND({get_column_letter(revised_col)}{row_start}/8,2)'
        ws.cell(row_start, ot_rate_col).number_format = '0.00'


        
        shoe_amount = contractor_doc.shoe_amount or 0
        uniform_amount = contractor_doc.shoe_amount or 0
        ws.cell(row_start, ot_rate_col+1).value = shoe_amount
        ws.cell(row_start, ot_rate_col+2).value = uniform_amount

        total_col = ot_rate_col + 3
        ws.cell(row_start, total_col).value = \
            f'={get_column_letter(ot_rate_col+1)}{row_start}+' \
            f'{get_column_letter(total_ot_col+3)}{row_start}'

        man_days_col = total_col + 1
        ws.cell(row_start, man_days_col).value = \
            f'={get_column_letter(leave_start_col+2)}{row_start}+' \
            f'{get_column_letter(summary_col+3)}{row_start}'

        total_wage_col = man_days_col + 1
        ws.cell(row_start, total_wage_col).value = \
            f'={get_column_letter(total_col)}{row_start}*' \
            f'{get_column_letter(man_days_col)}{row_start}'
        cell = ws.cell(row=row_start, column=total_wage_col)
        cell.number_format = '#,##0'

        pf_res_col = total_wage_col + 1
        revised_col_letter = get_column_letter(total_ot_col+3)
        actual_weekoff_col = summary_col + 5
        actual_attended_col = final_total_col

        actual_attended_col_letter = get_column_letter(actual_attended_col)
        actual_weekoff_col_letter = get_column_letter(actual_weekoff_col)
        ws.cell(row_start, pf_res_col).value = (
            f'=MIN({revised_col_letter}{row_start},'
            f'ROUND(15000/({actual_attended_col_letter}{row_start}-'
            f'{actual_weekoff_col_letter}{row_start}),0))'
        )

        pf_wage_col = pf_res_col + 1
        ws.cell(row_start, pf_wage_col).value = (
            f'=MIN({get_column_letter(man_days_col)}{row_start}*'
            f'{get_column_letter(pf_res_col)}{row_start},15000)'
        )
        cell = ws.cell(row=row_start, column=pf_wage_col)
        cell.number_format = '#,##0'

        actual_pf_col = pf_wage_col + 1
        ws.cell(row_start, actual_pf_col).value = \
            f'=ROUND({get_column_letter(pf_wage_col)}{row_start}*13%,0)'
        cell = ws.cell(row=row_start, column=actual_pf_col)
        cell.number_format = '#,##0'

        minimum_wages = contractor_doc.minimum_wages or 0
        basic_da_col = actual_pf_col + 1
        ws.cell(row_start, basic_da_col).value = (
            f'=MIN({get_column_letter(revised_col)}{row_start},{minimum_wages})'
        )
        hrs_col = basic_da_col + 1
        ws.cell(row_start, hrs_col).value = \
            f'=ROUND(({get_column_letter(revised_col)}{row_start}-{get_column_letter(basic_da_col)}{row_start})/2,2)'
        ws.cell(row_start, hrs_col).number_format = '0.00'

        washing_col = hrs_col + 1
        ws.cell(row_start, washing_col).value = \
            f'=ROUND(({get_column_letter(revised_col)}{row_start}-{get_column_letter(basic_da_col)}{row_start})/2,2)'
        ws.cell(row_start, washing_col).number_format = '0.00'

        fixed_gross_col = washing_col + 1
        actual_weekoff_col = summary_col + 5
        actual_attended_col = summary_col + 6
        revised_col_letter = get_column_letter(revised_col)
        actual_attended_letter = get_column_letter(actual_attended_col)
        actual_weekoff_letter = get_column_letter(actual_weekoff_col)
        ws.cell(row_start, fixed_gross_col).value = (
            f'=ROUND({revised_col_letter}{row_start}*'
            f'({actual_attended_letter}{row_start}-'
            f'{actual_weekoff_letter}{row_start}),0)'
        )
        ws.cell(row_start, fixed_gross_col).number_format = '#,##0'
        
        esi_wage_col = fixed_gross_col + 1
        ws.cell(row_start, esi_wage_col).value = f'''=
        IF({get_column_letter(fixed_gross_col)}{row_start}<21000,
        ({get_column_letter(basic_da_col)}{row_start}+
        {get_column_letter(hrs_col)}{row_start})*
        {get_column_letter(man_days_col)}{row_start},
        0)'''
        ws.cell(row_start, esi_wage_col).number_format = '#,##0'

        esi_ot_col = esi_wage_col + 1
        ws.cell(row_start, esi_ot_col).value = f'''=
        IF({get_column_letter(fixed_gross_col)}{row_start}<21000,
        (({get_column_letter(basic_da_col)}{row_start}+
        {get_column_letter(hrs_col)}{row_start})/8)*
        {get_column_letter(total_ot_col)}{row_start},
        0)'''
        ws.cell(row_start, esi_ot_col).number_format = '#,##0'

        esi_percent_col = esi_ot_col + 1
        ot_hours_col = esi_percent_col + 1
        total_ot_amt_col = ot_hours_col + 1

        att_bonus_col = total_ot_amt_col + 1
        ws.cell(row_start, att_bonus_col).value = f'''=
        IF({get_column_letter(actual_attended_col)}{row_start}=31,500,
        IF({get_column_letter(actual_attended_col)}{row_start}=30,300,0))'''
        ws.cell(row_start, att_bonus_col).number_format = '#,##0'

        ws.cell(row_start, esi_percent_col).value = f'''=
        IF({get_column_letter(fixed_gross_col)}{row_start}<21000,
        ROUND(({get_column_letter(esi_wage_col)}{row_start}+
        {get_column_letter(esi_ot_col)}{row_start}+
        {get_column_letter(att_bonus_col)}{row_start})*3.25%,0),
        0)'''
        ws.cell(row_start, esi_percent_col).number_format = '#,##0'

        
        ws.cell(row_start, ot_hours_col).value = \
            f'={get_column_letter(total_ot_col)}{row_start}'
        ws.cell(row_start, washing_col).number_format = '0.00'
        
        ws.cell(row_start, total_ot_amt_col).value = \
            f'=ROUND(({get_column_letter(revised_col)}{row_start}/8)*{get_column_letter(ot_hours_col)}{row_start},2)'
        ws.cell(row_start, total_ot_amt_col).number_format = '#,##0'


        fest_allow_col = att_bonus_col + 1
        formula_row = row_start         
        data_row    = row_start + 1      

        start_letter = get_column_letter(date_start_col)
        end_letter   = get_column_letter(date_start_col + total_days - 1)

        ws.cell(formula_row, fest_allow_col).value = (
            f'=COUNTIF({start_letter}{data_row}:{end_letter}{data_row},"NH")*150+'
            f'COUNTIF({start_letter}{data_row}:{end_letter}{data_row},"FH")*250'
        )


        grand_total_col = fest_allow_col + 1
        ws.cell(row_start, grand_total_col).value = \
            f'=ROUND({get_column_letter(total_wage_col)}{row_start}+' \
            f'{get_column_letter(actual_pf_col)}{row_start}+' \
            f'{get_column_letter(total_ot_amt_col)}{row_start}+' \
            f'{get_column_letter(att_bonus_col)}{row_start}+' \
            f'{get_column_letter(fest_allow_col)}{row_start},0)'
        ws.cell(row_start, grand_total_col).number_format = '#,##0'

        
        service_charge_col = grand_total_col + 1
        ws.cell(row_start, service_charge_col).value = \
            f'=ROUND(({get_column_letter(revised_col)}{row_start}*' \
            f'{get_column_letter(man_days_col)}{row_start})*' \
            f'{service_charge}/100,0)'
        ws.cell(row_start, service_charge_col).number_format = '#,##0'


        emp_name = emp.get("name")
        ot_doc = frappe.get_all(
            "OT Type",
            filters={
                "employee": emp_name,
                "from_date": ["<=", end_date],
                "to_date": [">=", start_date]
            },fields=["dwsi_ot", "contractor_ot"],limit=1)

        dwsi_ot = ot_doc[0].dwsi_ot if ot_doc else 0
        se_ot = ot_doc[0].contractor_ot if ot_doc else 0
        dwsi_ot_col = service_charge_col + 1
        se_ot_col = dwsi_ot_col + 1
        ws.cell(row_start, dwsi_ot_col).value = dwsi_ot
        ws.cell(row_start, se_ot_col).value = se_ot
        dwsi_ot_amt_col = se_ot_col + 1
        con_ot_amt_col = dwsi_ot_amt_col + 1

        ws.cell(row_start, dwsi_ot_amt_col).value = \
            f'=ROUND({get_column_letter(ot_rate_col)}{row_start}*{get_column_letter(dwsi_ot_col)}{row_start},0)'
        ws.cell(row_start, dwsi_ot_amt_col).number_format = '#,##0'
        ws.cell(row_start, con_ot_amt_col).value = \
            f'=ROUND({get_column_letter(ot_rate_col)}{row_start}*{get_column_letter(se_ot_col)}{row_start},0)'
        ws.cell(row_start, con_ot_amt_col).number_format = '#,##0'

        fes_salary = con_ot_amt_col + 1
        revised_col_letter = get_column_letter(revised_col)
        festival_allow_letter = get_column_letter(fest_allow_col)
        ws.cell(formula_row, fes_salary).value = (
            f'=ROUND({revised_col_letter}{formula_row}*'
            f'(COUNTIF({start_letter}{data_row}:{end_letter}{data_row},"NH")+'
            f'COUNTIF({start_letter}{data_row}:{end_letter}{data_row},"FH")),0)'
        )

        fes_service_charge_col = fes_salary + 1
        fes_salary_letter = get_column_letter(fes_salary)
        ws.cell(formula_row, fes_service_charge_col).value = (
            f'=ROUND({fes_salary_letter}{formula_row}*{service_charge}/100,0)'
        )
        ws.cell(formula_row, fes_service_charge_col).number_format = '#,##0'

        ded_service_charge_col = fes_service_charge_col + 1
        holiday_shift_count = 0
        start_col = column_index_from_string("J")
        for day in range(1, total_days + 1):
            current_date = date(year, month, day)
            if current_date in company_holidays:
                shift_value = ws.cell(data_row, start_col + day - 1).value
                if shift_value in ["A", "B", "C"]:
                    holiday_shift_count += 1
        revised = ws.cell(formula_row, revised_col).value or 0
        try:
            revised_value = float(revised)
        except (TypeError, ValueError):
            revised_value = 0
        fes_salary1 = ws.cell(formula_row, fes_salary).value or 0
        try:
            fes_salary_value = float(fes_salary1)
        except (TypeError, ValueError):
            fes_salary_value = 0
        if fes_salary_value > 0:
            deduction_value = 0
        else:
            deduction_value = holiday_shift_count * revised_value
        cell = ws.cell(formula_row, ded_service_charge_col)
        cell.value = deduction_value
        cell.number_format = '#,##0'


        ded_service_charge_col_val = ded_service_charge_col + 1
        fes_salary_letter = get_column_letter(ded_service_charge_col)
        ws.cell(formula_row, ded_service_charge_col_val).value = (
            f'=ROUND({fes_salary_letter}{formula_row}*{service_charge}/100,0)'
        )
        ws.cell(formula_row, ded_service_charge_col_val).number_format = '#,##0'

        # ===== FINAL HEADERS : 4 ROW MERGE PER EMPLOYEE =====
        merge_emp_4_rows(
            ws,
            row_start,
            final_header_start_col,
            final_header_end_col,
            border_all
        )

        # -------- Move to next employee --------
        sno += 1
        start_row += 4
    
    # ===== LAST DEPARTMENT SUBTOTAL =====
    if current_dept:

        dept_end_row = start_row - 1
        subtotal_row = start_row
        
        for col in range(date_start_col, day_loop_end_col + 1):
            cell = ws.cell(subtotal_row, col)
            cell.border = thin_border
            cell.fill = yellow_fill
            cell.alignment = center

        summary_start_col = day_loop_end_col + 1
        for col in range(summary_start_col, final_header_end_col + 1):
            col_letter = get_column_letter(col)

            cell = ws.cell(subtotal_row, col)
            cell.value = f"=SUM({col_letter}{dept_start_row}:{col_letter}{dept_end_row})"
            cell.number_format = '#,##0'
            cell.fill = yellow_fill
            cell.alignment = center
            cell.border = thin_border
        subtotal_rows.append(subtotal_row)

        start_row += 1

        ws.merge_cells(
            start_row=subtotal_row,
            start_column=2,
            end_row=subtotal_row,
            end_column=date_start_col - 1
        )
        for col in range(2, date_start_col):
            cell = ws.cell(subtotal_row, col)
            cell.fill = yellow_fill
            cell.border = thin_border
            cell.alignment = center
        cell = ws.cell(subtotal_row, 2, "SUBTOTAL")
        cell.fill = yellow_fill
        cell.alignment = center
        cell.border = thin_border
        
    grand_total_row = start_row
    ws.merge_cells(
        start_row=grand_total_row,
        start_column=2,
        end_row=grand_total_row,
        end_column=cat_col
    )
    for col in range(2, cat_col + 1):
        cell = ws.cell(grand_total_row, col)
        cell.fill = green_fill
        cell.alignment = center
        cell.border = border_all
    c = ws.cell(row=grand_total_row, column=2, value="GRAND TOTAL")
    

    for col in range(date_start_col, day_loop_end_col + 1):
        cell = ws.cell(grand_total_row, col)
        cell.border = thin_border
        cell.fill = green_fill
        cell.alignment = center

    summary_start_col = day_loop_end_col + 1
    for col in range(summary_start_col, final_header_end_col + 1):
        col_letter = get_column_letter(col)
        sum_formula = "+".join(
            [f"{col_letter}{r}" for r in subtotal_rows]
        )
        ws.cell(grand_total_row, col).value = f"={sum_formula}"
        ws.cell(grand_total_row, col).number_format = '#,##0'
        ws.cell(grand_total_row, col).fill = green_fill
        ws.cell(grand_total_row, col).alignment = center
        ws.cell(grand_total_row, col).border = border_all

    
    # ---------------- Response ----------------
    xlsx = io.BytesIO()
    wb.save(xlsx)
    xlsx.seek(0)

    frappe.response.filename = f"{contractor}_Salary_Statement.xlsx"
    frappe.response.filecontent = xlsx.read()
    frappe.response.type = "binary"
