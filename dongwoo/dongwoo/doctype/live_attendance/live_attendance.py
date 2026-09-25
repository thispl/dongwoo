# Copyright (c) 2025, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowtime, get_time
from datetime import datetime, time
from frappe.utils import nowdate
from datetime import datetime, timedelta
from frappe.utils import add_days,format_date
from frappe.utils import today

class LiveAttendance(Document):
    pass


# @frappe.whitelist(allow_guest=True)
# def get_att_data(date):
#     today_date = nowdate()
#     now = datetime.now()
#     date_now = now.strftime("%d/%m/%Y")
#     now_time = now.time()
#     def to_time(t):
#         return (datetime.min + t).time() if isinstance(t, timedelta) else t
#     now_time = datetime.now().time()

#     date_dt = datetime.strptime(date, "%Y-%m-%d")
#     date_dt = date_dt.replace(hour=0, minute=0, second=0, microsecond=0)

#     today_dt = datetime.strptime(today(), "%Y-%m-%d").replace(hour=8, minute=30, second=0, microsecond=0)
#     prev_day =add_days(today(),-1)
#     prev_day_dt = datetime.strptime(prev_day, "%Y-%m-%d").replace(hour=0, minute=0, second=0, microsecond=0)

#     shifts = frappe.get_all(
#         'Shift Type',
#         filters={
#             'name': ['!=', 'WW']
#         },
#         fields=['name', 'start_time', 'end_time']
#     )

#     matched_shift = ""
#     frappe.errprint(date)

#     for shift in shifts:
#         start = to_time(shift.start_time)
#         end = to_time(shift.end_time)

#         if start and end:
#             if start < end:
#                 if start <= now_time <= end:
#                     matched_shift = shift.name
#                     break
#             else:
#                 # Overnight shift (e.g., 17:00 to 01:30)
#                 if now_time >= start or now_time <= end:
#                     matched_shift = shift.name
#                     # Overnight range check (e.g., 01:30 to 08:30)
#                     if time(1, 30) <= now_time <= time(8, 30):
#                         date = add_days(date, -1)
#                     break
#     category_list = frappe.db.get_all('Employee Type', ['name'], order_by='`order`')

#     row_data = {
#         "in": {},
#         "out": {},
#         "balance": {}
#     }

#     in_total = out_total = total_balance = 0

#     for category in category_list:
#         category_name = category['name']

#         category_in = frappe.db.count("Attendance", {
#             "in_time": ['!=', ''],
#             "attendance_date": date.strftime("%Y-%m-%d") if isinstance(date, datetime) else date,
#             "employee_type": category_name,
#             "docstatus": ['!=', 2]
#         })

#         category_out = frappe.db.count("Attendance", {
#             "in_time": ['is', 'set'],
#             "out_time": ['!=', ''],
#             "attendance_date": date.strftime("%Y-%m-%d") if isinstance(date, datetime) else date,
#             "employee_type": category_name,
#             "docstatus": ['!=', 2]
#         })

#         balance = category_in - category_out

#         row_data["in"][category_name] = category_in
#         row_data["out"][category_name] = category_out
#         row_data["balance"][category_name] = balance

#         in_total += category_in
#         out_total += category_out
#         total_balance += balance

#     categories = [c["name"] for c in category_list]
#     shift = matched_shift or ""
#     total_cols = len(categories) + 1  
#     remaining_width = 80  
#     col_width = round(remaining_width / (total_cols), 2)  
#     desc_col_width = 20
#     if isinstance(date, str):
#         date_d = datetime.strptime(date, "%Y-%m-%d").date()
#     elif isinstance(date, datetime):
#         date_d = date.date()
#     else:
#         date_d = date
#     if prev_day_dt <= date_dt <= today_dt:
#         date = date_d
#         header = f"On Going Shift: {shift} - {format_date(date)}"
        
#     else:
#         date = date_d
#         header = f"Attendance Date - {format_date(date)}"
        

#     html = f"""
#     <table class="table table-bordered text-center" style="table-layout: fixed; width: 100%;">
#         <thead class="thead-dark">
#             <tr style="border: 1px solid black; color:white;">
#                 <th colspan="4" style="border: 1px solid black; background-color: #fb0102; font-size: 20px;">
#                     {header}
#                 </th>
#             </tr>
#             <tr style="border: 1px solid black; color:white;">
#                 <th style="border: 1px solid black; background-color: #040473; width: 25%;">Category</th>
#                 <th style="border: 1px solid black; background-color: #0f1568; width: 25%;">Checkin (Present)</th>
#                 <th style="border: 1px solid black; background-color: #0f1568; width: 25%;">Checkout</th>
#                 <th style="border: 1px solid black; background-color: #0f1568; width: 25%;">Balance</th>
#             </tr>
#         </thead>
#         <tbody>
#     """

#     # Loop each category to build rows
#     for cat in categories:
#         html += f"""
#             <tr style="border: 1px solid black; color: black;">
#                 <td style="border: 1px solid black;">{cat}</td>
#                 <td style="border: 1px solid black;">{row_data['in'].get(cat, 0)}</td>
#                 <td style="border: 1px solid black;">{row_data['out'].get(cat, 0)}</td>
#                 <td style="border: 1px solid black;">{row_data['balance'].get(cat, 0)}</td>
#             </tr>
#         """

#     # Total row
#     html += f"""
#         <tr style="border: 1px solid black; font-weight: bold;">
#             <td style="border: 1px solid black;">Total</td>
#             <td style="border: 1px solid black;">{in_total}</td>
#             <td style="border: 1px solid black;">{out_total}</td>
#             <td style="border: 1px solid black;">{total_balance}</td>
#         </tr>
#     """

#     html += "</tbody></table>"
#     return html



# def to_time(t):
#     return (datetime.min + t).time() if isinstance(t, timedelta) else t

@frappe.whitelist(allow_guest=True)
def get_att_data(date):
    now = datetime.now()
    now_time = now.time()
    def to_time(t):
        return (datetime.min + t).time() if isinstance(t, timedelta) else t
    
    today_dt = datetime.strptime(today(), "%Y-%m-%d").replace(hour=8, minute=30, second=0)
    prev_day = add_days(today(), -1)
    prev_day_dt = datetime.strptime(prev_day, "%Y-%m-%d").replace(hour=0, minute=0)

    # Convert string date to datetime
    if isinstance(date, str):
        date_dt = datetime.strptime(date, "%Y-%m-%d")
    else:
        date_dt = date

    shifts = frappe.get_all(
        'Shift Type',
        filters={'name': ['!=', 'WW']},
        fields=['name', 'start_time', 'end_time'],
        order_by='name ASC'
    )

    matched_shift = ""
    for shift in shifts:
        start = to_time(shift.start_time)
        end = to_time(shift.end_time)
        if start < end:
            if start <= now_time <= end:
                matched_shift = shift.name
                break
        else:
            if now_time >= start or now_time <= end:
                matched_shift = shift.name
                if time(1, 30) <= now_time <= time(8, 30):
                    date = add_days(date, -1)
                break

    if isinstance(date, str):
        date_d = datetime.strptime(date, "%Y-%m-%d").date()
    elif isinstance(date, datetime):
        date_d = date.date()
    else:
        date_d = date

    # if prev_day_dt <= date_dt <= today_dt:
    #     header = f"On Going Shift: {matched_shift} - {format_date(date)}"
    # else:
    #     header = f"Attendance Date - {format_date(date)}"
    
    if prev_day_dt < date_dt <= today_dt:
        date = date_d
        header = f"On Going Shift: {matched_shift} - {format_date(date)}"
        
    else:
        date = date_d
        header = f"Attendance Date - {format_date(date)}"

    category_list = frappe.db.get_all('Employee Type', ['name'], order_by='`order`')
    categories = [c['name'] for c in category_list]

    # Initialize row_data[shift][in/out/balance][category]
    row_data = {}
    for shift in shifts:
        sname = shift.name
        row_data[sname] = {"in": {}, "out": {}, "balance": {}}
        for category in categories:
            category_in = frappe.db.count("Attendance", {
                "in_time": ['!=', ''],
                "attendance_date": date_d,
                "employee_type": category,
                "shift": sname,
                "docstatus": ['!=', 2]
            })

            category_out = frappe.db.count("Attendance", {
                "out_time": ['!=', ''],
                "attendance_date": date_d,
                "employee_type": category,
                "shift": sname,
                "docstatus": ['!=', 2]
            })

            balance = category_in - category_out
            row_data[sname]["in"][category] = category_in
            row_data[sname]["out"][category] = category_out
            row_data[sname]["balance"][category] = balance

    # Begin HTML Table
    html = f"""
    <h4 style='margin-bottom: 10px; font-weight: bold; text-align:center'>{header}</h4>
    <table class="table table-bordered text-center" style="width: 100%; border-collapse: collapse;">
        <thead>
            <tr>
                <th rowspan="2" style="border: 1px solid black; background-color: #040473; color: white;">Category</th>
    """
    for shift in shifts:
        html += f"""
                <th colspan="3" style="border: 1px solid black; background-color: #fb0102; color: white;">
                    Shift {shift.name}
                </th>
        """
    html += "</tr><tr>"

    for s in shifts:
        html += """
                <th style="border: 1px solid black; background-color: #0f1568; color: white;">Checkin</th>
                <th style="border: 1px solid black; background-color: #0f1568; color: white;">Checkout</th>
                <th style="border: 1px solid black; background-color: #0f1568; color: white;">Balance</th>
        """
    html += "</tr></thead><tbody>"

    # Rows for each category
    for category in categories:
        html += f"<tr><td style='border: 1px solid black;'>{category}</td>"
        for shift in shifts:
            sname = shift.name
            html += f"""
                <td style='border: 1px solid black;'>{row_data[sname]['in'].get(category, 0)}</td>
                <td style='border: 1px solid black;'>{row_data[sname]['out'].get(category, 0)}</td>
                <td style='border: 1px solid black;'>{row_data[sname]['balance'].get(category, 0)}</td>
            """
        html += "</tr>"

    # Total Row
    html += "<tr style='font-weight: bold;'><td style='border: 1px solid black;'>Total</td>"
    for shift in shifts:
        sname = shift.name
        total_in = sum(row_data[sname]["in"].values())
        total_out = sum(row_data[sname]["out"].values())
        total_bal = sum(row_data[sname]["balance"].values())
        html += f"""
            <td style='border: 1px solid black;'>{total_in}</td>
            <td style='border: 1px solid black;'>{total_out}</td>
            <td style='border: 1px solid black;'>{total_bal}</td>
        """
    html += "</tr></tbody></table>"

    return html