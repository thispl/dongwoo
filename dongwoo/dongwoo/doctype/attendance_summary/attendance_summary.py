# # Copyright (c) 2021, TEAMPRO and contributors
# # For license information, please see license.txt

# import frappe
# from frappe.model.document import Document
# from frappe.utils import cstr, add_days, date_diff,format_datetime
# from datetime import date, timedelta, datetime, time

# class AttendanceSummary(Document):
#     pass

# @frappe.whitelist()
# def get_data_mobile(emp, from_date, to_date):
#     no_of_days = date_diff(add_days(to_date, 1), from_date)
#     dates = [add_days(from_date, i) for i in range(0, no_of_days)]

#     emp_details = frappe.db.get_value('Employee',emp,['employee_name','department'])
#     roles=frappe.get_roles(frappe.session.user)
#     if 'HOD' in roles:
#         data = "<table class='table table-bordered=1'>"
#         data += "<tr style='font-size:5px;padding:1px'><td style = 'border: 2px solid black;background-color:#ADD8E6;padding:1px'><b><center>ID</center></b></td><td style = 'border: 2px solid black;background-color:#ADD8E6;padding:1px'colspan=1><b><center>%s</center></b></td><td style = 'border: 2px solid black;background-color:#ADD8E6;padding:1px'><b><center>Name</center></b></td><td style = 'border: 2px solid black;background-color:#ADD8E6;padding:1px' colspan=2><b><center>%s</center></b></td><td style = 'border: 2px solid black;background-color:#ADD8E6;padding:1px'><b><center>Dept</center></b></td><td style = 'border: 2px solid black;background-color:#ADD8E6;padding:1px' colspan=1><b><center>%s</center></b></td></tr>"%(emp,emp_details[0],emp_details[1])
#         data += "<tr style='font-size:5px;padding:1px'><td style = 'border: 2px solid black;padding:1px;background-color:#ADD8E6'colspan=6><b><center>Attendance</center></b></td><td style ='border: 2px solid black;padding:1px;background-color:#ADD8E6 colspan=3><b><center>Overtime</center></b></td><tr>"
#         data += "<tr style='font-size:5px;padding:1px'><td style = 'border: 2px solid black;border-right: 1px solid black;background-color:#ADD8E6;padding:1px'><b><center>Date</center></b></td><td style = 'border: 1px solid black;border-bottom: 2px solid black;background-color:#ADD8E6;padding:1px'><b><center>Day</center></b></td><td style = 'border: 1px solid black;border-bottom: 2px solid black;background-color:#ADD8E6;padding:1px'><b><center>Working</center></b></td><td style = 'border: 1px solid black;border-bottom: 2px solid black;background-color:#ADD8E6;padding:1px'><b><center>In Time</center></b></td><td style = 'border: 1px solid black;border-bottom: 2px solid black;background-color:#ADD8E6;padding:1px'><b><center>Out Time</center></b></td><td style = 'border: 2px solid black;border-left: 1px;background-color:#ADD8E6;padding:1px'><b><center>Status</center></b></td><td style = 'border: 2px solid black;border-left: 1px;background-color:#ADD8E6;padding:1px'><b><center>Total Hrs</center</b></td></tr>"
    
#         total_ot = timedelta(0,0,0)
#         for date in dates:
#             dt = datetime.strptime(date,'%Y-%m-%d')
#             d = dt.strftime('%d-%b')
#             day = datetime.date(dt).strftime('%a')
#             holiday  = check_holiday(emp,date)
#             in_time = frappe.db.get_value('Attendance' ,{'employee':emp,"attendance_date":date},'in_time') or ''
#             if in_time:
#                 in_time = (format_datetime(in_time)).replace(' ','<br>')
#             out_time = frappe.db.get_value('Attendance' ,{'employee':emp,"attendance_date":date},'out_time') or ''
#             if out_time:
#                 out_time = (format_datetime(out_time)).replace(' ','<br>')
#             status_format = get_status(emp,date)
#             if frappe.db.exists('Overtime Request',{'employee':emp,'ot_date':date,'workflow_state':'Approved'}):
#                 ot = frappe.db.get_value('Overtime Request',{'employee':emp,'ot_date':date,'workflow_state':'Approved'},'ot_hours')
#                 total_ot = total_ot + ot
#             start_time =frappe.db.get_value("Overtime Request",{'employee':emp,'ot_date':date,'workflow_state':'Approved'},'from_time') or  ''
#             if start_time:
#                 start_time = datetime.strptime(str(start_time),'%H:%M:%S')
#                 start_time = datetime.strftime(start_time,'%H:%M')
#             end_time = frappe.db.get_value("Overtime Request",{'employee':emp,'ot_date':date,'workflow_state':'Approved'},'to_time') or  ''   
#             if end_time:
#                 end_time = datetime.strptime(str(end_time),'%H:%M:%S')
#                 end_time = datetime.strftime(end_time,'%H:%M')
#             total_hours = frappe.db.get_value("Overtime Request",{'employee':emp,'ot_date':date,'workflow_state':'Approved'},'ot_hours') or  ''
#             if total_hours:
#                 total_hours = datetime.strptime(str(total_hours),'%H:%M:%S')
#                 total_hours = datetime.strftime(total_hours,'%H:%M')
#             if status_format in ('AA','12','13','21','23','31','32','1L2','1L3','2L1','2L3','3L1','3L2','PP1L','PP2L','1M','2M','3M','MM','M1','M2','M3','MPP2','LA','LL','LOP','0.5LL','0.5LA'):
#                 status_clr = 'ff262d'
#             else:
#                 status_clr = 'fdfefe'
#             data += "<tr style='font-size:5px;padding:1px'><td style = 'border: 1px solid black;border-left: 2px solid black;padding:1px' nowrap>%s</td><td style = 'border: 1px solid black;padding:1px'><center>%s</center></td><td style = 'border: 1px solid black;padding:1px'><center>%s</center></td><td style = 'border: 1px solid black;padding:1px' nowrap><center>%s</center></td><td style = 'border: 1px solid black;padding:1px' nowrap><center>%s</center></td><td style = 'border: 1px solid black;padding:1px;background-color:#%s'><center>%s</center></td><td style = 'border: 1px solid black;border-left: 2px solid black;padding:1px'><center>%s</center></td><td style = 'border: 1px solid black;padding:1px'><center>%s</center></td><td style = 'border: 1px solid black;border-right: 2px solid black;padding:1px'><center>%s</center></td></tr>"%(d,day,holiday or 'W',in_time or '',out_time or '',status_clr,status_format,start_time,end_time,total_hours)
#         day = total_ot.days * 24
#         hours = day + total_ot.seconds // 3600
#         minutes = (total_ot.seconds//60)%60
#         ot = str(hours) + ' hr<br>' + str(minutes) + ' min'
#         data += "<tr style='font-size:5px;padding:1px'><td colspan=6 style = 'border: 2px solid black;background-color:#ADD8E6;padding:1px'></td><td colspan=2 style = 'border: 2px solid black;background-color:#ADD8E6;padding:1px'><center><b>TOTAL</b></center></td><td style = 'border: 2px solid black;background-color:#ADD8E6;padding:1px' nowrap><b><center>%s<center></b></td></tr>"%(ot)
#         data += "</table>"
#         return data
#     else:
#         data = "<table class='table table-bordered=1'>"
#         data += "<tr style='font-size:5px;padding:1px'><td style = 'border: 2px solid black;background-color:#ADD8E6;padding:1px'colspan=1><b><center>%s</center></b></td><td style = 'border: 2px solid black;background-color:#ADD8E6;padding:1px' colspan=2><b><center>%s</center></b></td><td style = 'border: 2px solid black;background-color:#ADD8E6;padding:1px'><b><center>Dept</center></b></td><td style = 'border: 2px solid black;background-color:#ADD8E6;padding:1px' colspan=1><b><center>%s</center></b></td></tr>"%(emp,emp_details[0],emp_details[1])
#         data += "<tr style='font-size:5px;padding:1px'><td style = 'border: 2px solid black;padding:1px;background-color:#ADD8E6'colspan=4><b><center>Attendance</center></b></td><td style ='border: 2px solid black;padding:1px;background-color:#ADD8E6 colspan=3><b><center>Overtime</center></b></td><tr>"
#         data += "<tr style='font-size:5px;padding:1px'><td style = 'border: 2px solid black;border-right: 1px solid black;background-color:#ADD8E6;padding:1px'><b><center>Date</center></b></td><td style = 'border: 1px solid black;border-bottom: 2px solid black;background-color:#ADD8E6;padding:1px'><b><center>Day</center></b></td><td style = 'border: 1px solid black;border-bottom: 2px solid black;background-color:#ADD8E6;padding:1px'><b><center>Working</center></b></td><td style = 'border: 2px solid black;border-left: 1px;background-color:#ADD8E6;padding:1px'><b><center>Status</center></b></td><td style = 'border: 2px solid black;border-left: 1px;background-color:#ADD8E6;padding:1px'><b><center>Total Hrs</center</b></td></tr>"
    
#         total_ot = timedelta(0,0,0)
#         for date in dates:
#             dt = datetime.strptime(date,'%Y-%m-%d')
#             d = dt.strftime('%d-%b')
#             day = datetime.date(dt).strftime('%a')
#             holiday  = check_holiday(emp,date)
#             in_time = frappe.db.get_value('Attendance' ,{'employee':emp,"attendance_date":date},'in_time') or ''
#             if in_time:
#                 in_time = (format_datetime(in_time)).replace(' ','<br>')
#             out_time = frappe.db.get_value('Attendance' ,{'employee':emp,"attendance_date":date},'out_time') or ''
#             if out_time:
#                 out_time = (format_datetime(out_time)).replace(' ','<br>')
#             status_format = get_status(emp,date)
#             if frappe.db.exists('Overtime Request',{'employee':emp,'ot_date':date,'workflow_state':'Approved'}):
#                 ot = frappe.db.get_value('Overtime Request',{'employee':emp,'ot_date':date,'workflow_state':'Approved'},'ot_hours')
#                 total_ot = total_ot + ot
#             start_time =frappe.db.get_value("Overtime Request",{'employee':emp,'ot_date':date,'workflow_state':'Approved'},'from_time') or  ''
#             if start_time:
#                 start_time = datetime.strptime(str(start_time),'%H:%M:%S')
#                 start_time = datetime.strftime(start_time,'%H:%M')
#             end_time = frappe.db.get_value("Overtime Request",{'employee':emp,'ot_date':date,'workflow_state':'Approved'},'to_time') or  ''   
#             if end_time:
#                 end_time = datetime.strptime(str(end_time),'%H:%M:%S')
#                 end_time = datetime.strftime(end_time,'%H:%M')
#             total_hours = frappe.db.get_value("Overtime Request",{'employee':emp,'ot_date':date,'workflow_state':'Approved'},'ot_hours') or  ''
#             if total_hours:
#                 total_hours = datetime.strptime(str(total_hours),'%H:%M:%S')
#                 total_hours = datetime.strftime(total_hours,'%H:%M')
#             if status_format in ('AA','12','13','21','23','31','32','1L2','1L3','2L1','2L3','3L1','3L2','PP1L','PP2L','1M','2M','3M','MM','M1','M2','M3','MPP2','LA','LL','LOP','0.5LL','0.5LA'):
#                 status_clr = 'ff262d'
#             else:
#                 status_clr = 'fdfefe'
#             data += "<tr style='font-size:5px;padding:1px'><td style = 'border: 1px solid black;border-left: 2px solid black;padding:1px' nowrap>%s</td><td style = 'border: 1px solid black;padding:1px' nowrap><center>%s</center></td><td style = 'border: 1px solid black;padding:1px' nowrap><center>%s</center></td><td style = 'border: 1px solid black;padding:1px;background-color:#%s'><center>%s</center></td><td style = 'border: 1px solid black;border-left: 2px solid black;padding:1px'><center>%s</center></td><td style = 'border: 1px solid black;padding:1px'><center>%s</center></td><td style = 'border: 1px solid black;border-right: 2px solid black;padding:1px'><center>%s</center></td></tr>"%(d,day,holiday or 'W',status_clr,status_format,start_time,end_time,total_hours)
#         day = total_ot.days * 24
#         hours = day + total_ot.seconds // 3600
#         minutes = (total_ot.seconds//60)%60
#         ot = str(hours) + ' hr<br>' + str(minutes) + ' min'
#         data += "<tr style='font-size:5px;padding:1px'><td colspan=4 style = 'border: 2px solid black;background-color:#ADD8E6;padding:1px'></td><td colspan=2 style = 'border: 2px solid black;background-color:#ADD8E6;padding:1px'><center><b>TOTAL</b></center></td><td style = 'border: 2px solid black;background-color:#ADD8E6;padding:1px' nowrap><b><center>%s<center></b></td></tr>"%(ot)
#         data += "</table>"
#         return data

# @frappe.whitelist()
# def get_data_system(emp, from_date, to_date):
#     no_of_days = date_diff(add_days(to_date, 1), from_date)
#     dates = [add_days(from_date, i) for i in range(0, no_of_days)]

#     emp_details = frappe.db.get_value('Employee',emp,['employee_name','department'])
#     users = frappe.get_all("User", {"name":frappe.session.user,"role": "HOD","enabled":1},["name"])
#     # roles = frappe.get_roles(frappe.session.user)
#     if users:
#         frappe.errprint("Test1")
#         data = "<table class='table table-bordered=1'>"
#         data += "<tr><td style = 'border: 1px solid black;background-color:#ADD8E6'><b>ID</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;'colspan=1><b>%s</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;'><b>Name</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;' colspan=2><b>%s</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;'><b>Dept</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;' colspan=1><b>%s</b></td></tr>"%(emp,emp_details[0],emp_details[1])
#         data += "<tr><td style = 'border: 1px solid black;'colspan=7><b><center>Attendance</center></b></td>"
#         data += "<tr><td style = 'border: 1px solid black;background-color:#ADD8E6'><b>Date</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;'><b>Day</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;'><b>Working</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;'><b>In Time</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;'><b>Out Time</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;'><b>Status</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;'><b>OT Hrs</b></td></tr>"   
#         ot_tot=0
#         for date in dates:
#             status_format = get_status(emp,date)
#             dt = datetime.strptime(date,'%Y-%m-%d')
#             d = dt.strftime('%d-%b')
#             day = datetime.date(dt).strftime('%a')
#             holiday  = check_holiday(emp,date)
#             in_time = frappe.db.get_value('Attendance' ,{'employee':emp,"attendance_date":date},'in_time') or ''
#             out_time = frappe.db.get_value('Attendance' ,{'employee':emp,"attendance_date":date},'out_time') or ''
#             ot_hrs = frappe.db.get_value('Attendance' ,{'employee':emp,"attendance_date":date},'overtime_hours') or 0
#             ot_hrs=float(ot_hrs)
#             ot_tot+=ot_hrs
#             data += "<tr><td style = 'border: 1px solid black;'>%s</td><td style = 'border: 1px solid black;'>%s</td><td style = 'border: 1px solid black;'>%s</td><td style = 'border: 1px solid black;'>%s</td><td style = 'border: 1px solid black;'>%s</td><td style = 'border: 1px solid black;'>%s</td><td style = 'border: 1px solid black;'>%s</td></tr>"%(d,day,holiday or 'W',format_datetime(in_time) or '',format_datetime(out_time) or '',status_format,ot_hrs)
#         ot=str(ot_tot)+' Hrs'
#         data += "<tr><td colspan=4 style = 'border: 1px solid black;background-color:#ADD8E6;'></td><td colspan=2 style = 'border: 1px solid black;background-color:#ADD8E6;'><center><b>TOTAL</b></center></td><td style = 'border: 1px solid black;background-color:#ADD8E6'><b>%s</b></td></tr>"%(ot)
#         data += "<tr><td colspan=3>P - Present<br>A - Absent<br>OL - On Leave</td><td colspan=2>HD - Half Day<br>WFH - Work From Home<br>CO - Compensatory Off</td><td colspan=2>SL - Sick Leave<br>CL - Casual Leave<br>EL - Earned Leave</td></tr>"
#         data += "</table>"
#     else:
#         frappe.errprint("Test")
#         data = "<table class='table table-bordered=1'>"
#         data += "<tr><td style = 'border: 1px solid black;background-color:#ADD8E6;'colspan=1><b>%s</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;' colspan=2><b>%s</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;'><b>Dept</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;' colspan=1><b>%s</b></td></tr>"%(emp,emp_details[0],emp_details[1])
#         data += "<tr><td style = 'border: 1px solid black;'colspan=5><b><center>Attendance</center></b></td>"
#         data += "<tr><td style = 'border: 1px solid black;background-color:#ADD8E6'><b>Date</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;'><b>Day</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;'><b>Working</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;'><b>Status</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;'><b>OT Hrs</b></td></tr>"   
#         ot_tot=0
#         for date in dates:
#             status_format = get_status(emp,date)
#             dt = datetime.strptime(date,'%Y-%m-%d')
#             d = dt.strftime('%d-%b')
#             day = datetime.date(dt).strftime('%a')
#             holiday  = check_holiday(emp,date)
#             in_time = frappe.db.get_value('Attendance' ,{'employee':emp,"attendance_date":date},'in_time') or ''
#             out_time = frappe.db.get_value('Attendance' ,{'employee':emp,"attendance_date":date},'out_time') or ''
#             ot_hrs = frappe.db.get_value('Attendance' ,{'employee':emp,"attendance_date":date},'overtime_hours') or 0
#             ot_hrs=float(ot_hrs)
#             ot_tot+=ot_hrs
#             data += "<tr><td style = 'border: 1px solid black;'>%s</td><td style = 'border: 1px solid black;'>%s</td><td style = 'border: 1px solid black;'>%s</td><td style = 'border: 1px solid black;'>%s</td><td style = 'border: 1px solid black;'>%s</td></tr>"%(d,day,holiday or 'W',status_format,ot_hrs)
#         ot=str(ot_tot)+' Hrs'
#         data += "<tr><td colspan=2 style = 'border: 1px solid black;background-color:#ADD8E6;'></td><td colspan=2 style = 'border: 1px solid black;background-color:#ADD8E6;'><center><b>TOTAL</b></center></td><td style = 'border: 1px solid black;background-color:#ADD8E6'><b>%s</b></td></tr>"%(ot)
#         data += "<tr><td colspan=2>P - Present<br>A - Absent<br>OL - On Leave</td><td colspan=2>HD - Half Day<br>WFH - Work From Home<br>CO - Compensatory Off</td><td colspan=1>SL - Sick Leave<br>CL - Casual Leave<br>EL - Earned Leave</td></tr>"
#         data += "</table>"

#     return data

# def check_holiday(emp,date):
#     holiday_list = frappe.db.get_value('Employee',{'name':emp},'holiday_list')
#     holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List`
#     left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(holiday_list,date),as_dict=True)
#     doj= frappe.db.get_value("Employee",{'name':emp},"date_of_joining")
#     status = ''
#     if frappe.db.exists('Shift Assignment',{'start_date':date,'employee':emp,'shift_type':'WW','docstatus':1}):
#         return "WW"
#     elif holiday :
#         if doj < holiday[0].holiday_date:
#             if holiday[0].weekly_off == 1:
#                 return "WW"     
#             else:
#                 return "HH"

# def get_status(emp,date):
#     status = ''
#     if frappe.db.exists('Attendance',{'employee':emp,'attendance_date':date,'docstatus':['!=','2']}):
#         shift = frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':date,'docstatus':['!=','2']},['status','employee_type','shift'])
#         holiday = check_holiday(emp,date)
#         if holiday:
#             if shift[2]:
#                 shift = shift[2] + holiday
#             else:
#              shift = holiday
#         else:
#             shift = shift[0]
#         # frappe.errprint([date,shift])
#         if shift[1] == "WC":
#             status = wc_status_map.get(shift, "")
#         else:
#             status = bc_status_map.get(shift, "")
#     return status

# bc_status_map = {
#     "Absent": "A",
#     "AA":"AA",
#     "Half Day": "HD",
#     "Holiday": "HH",
#     "WW": "WW",
#     "Weekly Off": "WW",
#     "1H": "1H",
#     "2H": "2H",
#     "3H": "3H",
#     "1W": "1W",
#     "2W": "2W",
#     "3W": "3W",
#     "PP1W": "PP1W",
#     "PP2W": "PP2W",
#     "1LH": "1LH",
#     "2LH": "2LH",
#     "3LH": "3LH",
#     "1LW": "1LW",
#     "2LW": "2LW",
#     "3LW": "3LW",
#     "PP1LW": "PP1LW",
#     "PP2LW": "PP2LW",
#     "MW": "MW",
#     "On Leave": "L",
#     "Present": "P",
#     "Work From Home": "WFH",
#     "MM": "AA",
#     "11": "11",
#     "22": "22",
#     "33": "33",
#     "PP1PP1": "P1P1",
#     "PP2PP2": "P2P2",
#     "1L1": "1L1",
#     "2L2": "2L2",
#     "3L3": "3L3",
#     "2L3": "AA",
#     "1L2": "AA",
#     "3L1": "AA",
#     "1LM": "1LM",
#     "2LM": "2LM",
#     "3LM": "3LM",
#     "PP2LM":"P2LM",
#     "PP1LPP1": "P1LP1",
#     "PP2LPP2": "P2LP2",
#     "1M": "1M",
#     "2M": "2M",
#     "3M": "3M",
#     "M1": "M1",
#     "M2": "M2",
#     "M3": "M3",
#     "PP1M": "P1M",
#     "PP2M": "P2M",
#     "MPP1": "MP1",
#     "MPP2": "MP2",
#     "11": "11",
#     "12": "12",
#     "13": "13",
#     "1PP1": "1P1",
#     "1PP2": "1P2",
#     "21": "21",
#     "22": "22",
#     "23": "23",
#     "2PP1": "2P1",
#     "2PP2": "2P2",
#     "31": "31",
#     "32": "32",
#     "33": "33",
#     "3PP1": "3P1",
#     "3PP2": "3P2",
#     "PP11": "P11",
#     "PP12": "P12",
#     "PP13": "P13",
#     "PP1PP1": "P1P1",
#     "PP1PP2": "P1P2",
#     "PP21": "P2P1",
#     "PP22": "P2P2",
#     "PP23": "P2P3",
#     "PP2PP1": "P2P1",
#     "PP2PP2": "P2P2",
#     "Earned Leave": "EL",
#     "Casual Leave": "CL",
#     "Sick Leave": "SL",
#     "OD": "OD",
#     "Compensatory Off": "CO",
#     "Leave Without Pay": "LL",
#     "0.5Earned Leave": "0.5EL",
#     "0.5Casual Leave": "0.5CL",
#     "0.5Sick Leave": "0.5SL",
#     "0.5Compensatory Off": "0.5CO",
#     "0.5Leave Without Pay": "0.5LL",
#     "LEarned Leave/2": "0.5SL",
#     "LCasual Leave/2": "0.5LCL",
#     "0.5Leave Without PayW": "1W",
#     "LSick Leave/2": "0.5LSL",
#     "LSpecial Leave/2": "0.5LSPL",
#     "LCompensatory Off/2": "0.5LCO",
#     "LLeave Without Pay/2": "0.5LLL",
#     "0.5Special Leave": "0.5SPL",
#     "Special Leave": "SPL",
#     "AAWW": "WW",
#     "AAHH": "HH",
#     "11WW": "11W",
#     "11HH": "11H",
#     "22WW": "22W",
#     "22HH": "22H",
#     "33WW": "33W",
#     "33HH": "33H",
#     "PP2PP2WW": "PP2PP2W",
#     "PP2PP2HH": "PP2PP2H",
#     "1WW": "1W",
#     "1HH": "1H",
#     "2WW": "2W",
#     "2HH": "2H",
#     "3WW": "3W",
#     "3HH": "3H",
#     "PP2WW": "PP2W",
#     "PP2HH": "PP2H",
#     "ODWW": "ODW"
#     }

# wc_status_map = {
#     "Absent": "A",
#     "AA": "AA",
#     "Half Day": "HD",
#     "Holiday": "HH",
#     "1H": "1H",
#     "2H": "2H",
#     "3H": "3H",
#     "1W": "1W",
#     "2W": "2W",
#     "3W": "3W",
#     "PP1W": "PP1W",
#     "PP2W": "PP2W",
#     "PP1H": "P1H",
#     "PP2H": "P2H",
#     "Weekly Off": "WW",
#     "On Leave": "L",
#     # "Present": "11",
#     "Work From Home": "WFH",
#     "OD": "OD",
#     "Earned Leave": "EL",
#     "Casual Leave": "CL",
#     "Sick Leave": "SL",
#     "Compensatory Off": "CO",
#     "Leave Without Pay": "LL",
#     "1": "11",
#     "2": "22",
#     "3": "33",
#     " ": "MM",
#     "PP1": "P1P1",
#     "PP2": "P2P2",
#     "1L": "1L1",
#     "2L": "2L2",
#     "3L": "3L3",
#     "PP1L": "P1LP1",
#     "PP2L": "P2LP2",
#     "1LH": "1LH",
#     "2LH": "2LH",
#     "3LH": "3LH",
#     "1LW": "1LW",
#     "2LW": "2LW",
#     "3LW": "3LW",
#     "PP1LW": "PP1LW",
#     "PP2LW": "PP2LW",
#     "1M": "1M",
#     "2M": "2M",
#     "3M": "3M",
#     "M1": "M1",
#     "M2": "M2",
#     "M3": "M3",
#     "PP1M": "P1M",
#     "PP2M": "P2M",
#     "MPP1": "MP1",
#     "MPP2": "MP2",
#     "0.5Earned Leave": "0.5EL",
#     "0.5Casual Leave": "0.5CL",
#     "0.5Sick Leave": "0.5SL",
#     "0.5Compensatory Off": "0.5CO",
#     "0.5Leave Without Pay": "0.5LL",
#     "0.5Leave Without PayW": "1W",
#     "LEarned Leave/2": "0.5SL",
#     "LCasual Leave/2": "0.5LCL",
#     "LSick Leave/2": "0.5LSL",
#     "LSpecial Leave/2": "0.5LSPL",
#     "LCompensatory Off/2": "0.5LCO",
#     "LLeave Without Pay/2": "0.5LLL",
#     "0.5Special Leave": "0.5SPL",
#     "Special Leave": "SPL",
#     "AAWW": "WW",
#     "AAHH": "HH",
#     "1WW": "1W",
#     "1HH": "1H",
#     "2WW": "2W",
#     "2HH": "2H",
#     "3WW": "3W",
#     "3HH": "3H",
#     "PP2WW": "PP2W",
#     "PP2HH": "PP2H",
#     "ODWW": "ODW"
#     }

# @frappe.whitelist()
# def get_employee():
#     emp_details = frappe.db.get_value('Employee',{'user_id':frappe.session.user},['employee','employee_name','department'])
#     return emp_details

# @frappe.whitelist()
# def get_employee_details(employee):
#     emp_details = frappe.db.get_value('Employee',{'name':employee},['employee_name','department'])
#     return emp_details

# @frappe.whitelist()
# def get_department_hods(user=None):
#     if not user:
#         user = frappe.session.user
#     department_list = frappe.db.get_values(
#         'Department',
#         filters={'hod': user},
#         fieldname=['name'],  
#         as_dict=False
#     )
#     return list(map(lambda x: x[0], department_list))  


# Copyright (c) 2021, TEAMPRO and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cstr, add_days, date_diff,format_datetime
from datetime import date, timedelta, datetime, time

class AttendanceSummary(Document):
    pass

@frappe.whitelist()
def get_data_mobile(emp, from_date, to_date):
    no_of_days = date_diff(add_days(to_date, 1), from_date)
    dates = [add_days(from_date, i) for i in range(0, no_of_days)]

    emp_details = frappe.db.get_value('Employee',emp,['employee_name','department'])
    roles=frappe.get_roles(frappe.session.user)
    if 'HOD' in roles:
        data = "<table class='table table-bordered=1'>"
        data += "<tr style='font-size:5px;padding:1px'><td style = 'border: 2px solid black;background-color:#ADD8E6;padding:1px'><b><center>ID</center></b></td><td style = 'border: 2px solid black;background-color:#ADD8E6;padding:1px'colspan=1><b><center>%s</center></b></td><td style = 'border: 2px solid black;background-color:#ADD8E6;padding:1px'><b><center>Name</center></b></td><td style = 'border: 2px solid black;background-color:#ADD8E6;padding:1px' colspan=2><b><center>%s</center></b></td><td style = 'border: 2px solid black;background-color:#ADD8E6;padding:1px'><b><center>Dept</center></b></td><td style = 'border: 2px solid black;background-color:#ADD8E6;padding:1px' colspan=1><b><center>%s</center></b></td></tr>"%(emp,emp_details[0],emp_details[1])
        data += "<tr style='font-size:5px;padding:1px'><td style = 'border: 2px solid black;padding:1px;background-color:#ADD8E6'colspan=6><b><center>Attendance</center></b></td><td style ='border: 2px solid black;padding:1px;background-color:#ADD8E6 colspan=3><b><center>Overtime</center></b></td><tr>"
        data += "<tr style='font-size:5px;padding:1px'><td style = 'border: 2px solid black;border-right: 1px solid black;background-color:#ADD8E6;padding:1px'><b><center>Date</center></b></td><td style = 'border: 1px solid black;border-bottom: 2px solid black;background-color:#ADD8E6;padding:1px'><b><center>Day</center></b></td><td style = 'border: 1px solid black;border-bottom: 2px solid black;background-color:#ADD8E6;padding:1px'><b><center>Working</center></b></td><td style = 'border: 1px solid black;border-bottom: 2px solid black;background-color:#ADD8E6;padding:1px'><b><center>In Time</center></b></td><td style = 'border: 1px solid black;border-bottom: 2px solid black;background-color:#ADD8E6;padding:1px'><b><center>Out Time</center></b></td><td style = 'border: 2px solid black;border-left: 1px;background-color:#ADD8E6;padding:1px'><b><center>Status</center></b></td><td style = 'border: 2px solid black;border-left: 1px;background-color:#ADD8E6;padding:1px'><b><center>Total Hrs</center</b></td></tr>"
    
        total_ot = timedelta(0,0,0)
        for date in dates:
            dt = datetime.strptime(date,'%Y-%m-%d')
            d = dt.strftime('%d-%b')
            day = datetime.date(dt).strftime('%a')
            holiday  = check_holiday(emp,date)
            in_time = frappe.db.get_value('Attendance' ,{'employee':emp,"attendance_date":date},'in_time') or ''
            if in_time:
                in_time = (format_datetime(in_time)).replace(' ','<br>')
            out_time = frappe.db.get_value('Attendance' ,{'employee':emp,"attendance_date":date},'out_time') or ''
            if out_time:
                out_time = (format_datetime(out_time)).replace(' ','<br>')
            status_format = get_status(emp,date)
            if frappe.db.exists('Overtime Request',{'employee':emp,'ot_date':date,'workflow_state':'Approved'}):
                ot = frappe.db.get_value('Overtime Request',{'employee':emp,'ot_date':date,'workflow_state':'Approved'},'ot_hours')
                total_ot = total_ot + ot
            start_time =frappe.db.get_value("Overtime Request",{'employee':emp,'ot_date':date,'workflow_state':'Approved'},'from_time') or  ''
            if start_time:
                start_time = datetime.strptime(str(start_time),'%H:%M:%S')
                start_time = datetime.strftime(start_time,'%H:%M')
            end_time = frappe.db.get_value("Overtime Request",{'employee':emp,'ot_date':date,'workflow_state':'Approved'},'to_time') or  ''   
            if end_time:
                end_time = datetime.strptime(str(end_time),'%H:%M:%S')
                end_time = datetime.strftime(end_time,'%H:%M')
            total_hours = frappe.db.get_value("Overtime Request",{'employee':emp,'ot_date':date,'workflow_state':'Approved'},'ot_hours') or  ''
            if total_hours:
                total_hours = datetime.strptime(str(total_hours),'%H:%M:%S')
                total_hours = datetime.strftime(total_hours,'%H:%M')
            if status_format in ('AA','12','13','21','23','31','32','1L2','1L3','2L1','2L3','3L1','3L2','PP1L','PP2L','1M','2M','3M','MM','M1','M2','M3','MPP2','LA','LL','LOP','0.5LL','0.5LA'):
                status_clr = 'ff262d'
            else:
                status_clr = 'fdfefe'
            data += "<tr style='font-size:5px;padding:1px'><td style = 'border: 1px solid black;border-left: 2px solid black;padding:1px' nowrap>%s</td><td style = 'border: 1px solid black;padding:1px'><center>%s</center></td><td style = 'border: 1px solid black;padding:1px'><center>%s</center></td><td style = 'border: 1px solid black;padding:1px' nowrap><center>%s</center></td><td style = 'border: 1px solid black;padding:1px' nowrap><center>%s</center></td><td style = 'border: 1px solid black;padding:1px;background-color:#%s'><center>%s</center></td><td style = 'border: 1px solid black;border-left: 2px solid black;padding:1px'><center>%s</center></td><td style = 'border: 1px solid black;padding:1px'><center>%s</center></td><td style = 'border: 1px solid black;border-right: 2px solid black;padding:1px'><center>%s</center></td></tr>"%(d,day,holiday or 'W',in_time or '',out_time or '',status_clr,status_format,start_time,end_time,total_hours)
        day = total_ot.days * 24
        hours = day + total_ot.seconds // 3600
        minutes = (total_ot.seconds//60)%60
        ot = str(hours) + ' hr<br>' + str(minutes) + ' min'
        data += "<tr style='font-size:5px;padding:1px'><td colspan=6 style = 'border: 2px solid black;background-color:#ADD8E6;padding:1px'></td><td colspan=2 style = 'border: 2px solid black;background-color:#ADD8E6;padding:1px'><center><b>TOTAL</b></center></td><td style = 'border: 2px solid black;background-color:#ADD8E6;padding:1px' nowrap><b><center>%s<center></b></td></tr>"%(ot)
        data += "</table>"
        return data
    else:
        data = "<table class='table table-bordered=1'>"
        data += "<tr style='font-size:5px;padding:1px'><td style = 'border: 2px solid black;background-color:#ADD8E6;padding:1px'colspan=1><b><center>%s</center></b></td><td style = 'border: 2px solid black;background-color:#ADD8E6;padding:1px' colspan=2><b><center>%s</center></b></td><td style = 'border: 2px solid black;background-color:#ADD8E6;padding:1px'><b><center>Dept</center></b></td><td style = 'border: 2px solid black;background-color:#ADD8E6;padding:1px' colspan=1><b><center>%s</center></b></td></tr>"%(emp,emp_details[0],emp_details[1])
        data += "<tr style='font-size:5px;padding:1px'><td style = 'border: 2px solid black;padding:1px;background-color:#ADD8E6'colspan=4><b><center>Attendance</center></b></td><td style ='border: 2px solid black;padding:1px;background-color:#ADD8E6 colspan=3><b><center>Overtime</center></b></td><tr>"
        data += "<tr style='font-size:5px;padding:1px'><td style = 'border: 2px solid black;border-right: 1px solid black;background-color:#ADD8E6;padding:1px'><b><center>Date</center></b></td><td style = 'border: 1px solid black;border-bottom: 2px solid black;background-color:#ADD8E6;padding:1px'><b><center>Day</center></b></td><td style = 'border: 1px solid black;border-bottom: 2px solid black;background-color:#ADD8E6;padding:1px'><b><center>Working</center></b></td><td style = 'border: 2px solid black;border-left: 1px;background-color:#ADD8E6;padding:1px'><b><center>Status</center></b></td><td style = 'border: 2px solid black;border-left: 1px;background-color:#ADD8E6;padding:1px'><b><center>Total Hrs</center</b></td></tr>"
    
        total_ot = timedelta(0,0,0)
        for date in dates:
            dt = datetime.strptime(date,'%Y-%m-%d')
            d = dt.strftime('%d-%b')
            day = datetime.date(dt).strftime('%a')
            holiday  = check_holiday(emp,date)
            in_time = frappe.db.get_value('Attendance' ,{'employee':emp,"attendance_date":date},'in_time') or ''
            if in_time:
                in_time = (format_datetime(in_time)).replace(' ','<br>')
            out_time = frappe.db.get_value('Attendance' ,{'employee':emp,"attendance_date":date},'out_time') or ''
            if out_time:
                out_time = (format_datetime(out_time)).replace(' ','<br>')
            status_format = get_status(emp,date)
            if frappe.db.exists('Overtime Request',{'employee':emp,'ot_date':date,'workflow_state':'Approved'}):
                ot = frappe.db.get_value('Overtime Request',{'employee':emp,'ot_date':date,'workflow_state':'Approved'},'ot_hours')
                total_ot = total_ot + ot
            start_time =frappe.db.get_value("Overtime Request",{'employee':emp,'ot_date':date,'workflow_state':'Approved'},'from_time') or  ''
            if start_time:
                start_time = datetime.strptime(str(start_time),'%H:%M:%S')
                start_time = datetime.strftime(start_time,'%H:%M')
            end_time = frappe.db.get_value("Overtime Request",{'employee':emp,'ot_date':date,'workflow_state':'Approved'},'to_time') or  ''   
            if end_time:
                end_time = datetime.strptime(str(end_time),'%H:%M:%S')
                end_time = datetime.strftime(end_time,'%H:%M')
            total_hours = frappe.db.get_value("Overtime Request",{'employee':emp,'ot_date':date,'workflow_state':'Approved'},'ot_hours') or  ''
            if total_hours:
                total_hours = datetime.strptime(str(total_hours),'%H:%M:%S')
                total_hours = datetime.strftime(total_hours,'%H:%M')
            if status_format in ('AA','12','13','21','23','31','32','1L2','1L3','2L1','2L3','3L1','3L2','PP1L','PP2L','1M','2M','3M','MM','M1','M2','M3','MPP2','LA','LL','LOP','0.5LL','0.5LA'):
                status_clr = 'ff262d'
            else:
                status_clr = 'fdfefe'
            data += "<tr style='font-size:5px;padding:1px'><td style = 'border: 1px solid black;border-left: 2px solid black;padding:1px' nowrap>%s</td><td style = 'border: 1px solid black;padding:1px' nowrap><center>%s</center></td><td style = 'border: 1px solid black;padding:1px' nowrap><center>%s</center></td><td style = 'border: 1px solid black;padding:1px;background-color:#%s'><center>%s</center></td><td style = 'border: 1px solid black;border-left: 2px solid black;padding:1px'><center>%s</center></td><td style = 'border: 1px solid black;padding:1px'><center>%s</center></td><td style = 'border: 1px solid black;border-right: 2px solid black;padding:1px'><center>%s</center></td></tr>"%(d,day,holiday or 'W',status_clr,status_format,start_time,end_time,total_hours)
        day = total_ot.days * 24
        hours = day + total_ot.seconds // 3600
        minutes = (total_ot.seconds//60)%60
        ot = str(hours) + ' hr<br>' + str(minutes) + ' min'
        data += "<tr style='font-size:5px;padding:1px'><td colspan=4 style = 'border: 2px solid black;background-color:#ADD8E6;padding:1px'></td><td colspan=2 style = 'border: 2px solid black;background-color:#ADD8E6;padding:1px'><center><b>TOTAL</b></center></td><td style = 'border: 2px solid black;background-color:#ADD8E6;padding:1px' nowrap><b><center>%s<center></b></td></tr>"%(ot)
        data += "</table>"
        return data

@frappe.whitelist()
def get_data_system(emp, from_date, to_date):
    no_of_days = date_diff(add_days(to_date, 1), from_date)
    dates = [add_days(from_date, i) for i in range(0, no_of_days)]

    emp_details = frappe.db.get_value('Employee',emp,['employee_name','department'])
    users = frappe.get_all("User", {"name":frappe.session.user,"role": "HOD","enabled":1},["name"])
    # roles = frappe.get_roles(frappe.session.user)
    if users:
        frappe.errprint("Test1")
        data = "<table class='table table-bordered=1'>"
        data += "<tr><td style = 'border: 1px solid black;background-color:#ADD8E6'><b>ID</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;'colspan=1><b>%s</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;'><b>Name</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;' colspan=2><b>%s</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;'><b>Dept</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;' colspan=1><b>%s</b></td></tr>"%(emp,emp_details[0],emp_details[1])
        data += "<tr><td style = 'border: 1px solid black;'colspan=7><b><center>Attendance</center></b></td>"
        data += "<tr><td style = 'border: 1px solid black;background-color:#ADD8E6'><b>Date</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;'><b>Day</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;'><b>Working</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;'><b>In Time</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;'><b>Out Time</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;'><b>Status</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;'><b>OT Hrs</b></td></tr>"   
        ot_tot=0
        for date in dates:
            status_format = get_status(emp,date)
            dt = datetime.strptime(date,'%Y-%m-%d')
            d = dt.strftime('%d-%b')
            day = datetime.date(dt).strftime('%a')
            holiday  = check_holiday(emp,date)
            in_time = frappe.db.get_value('Attendance' ,{'employee':emp,"attendance_date":date},'in_time') or ''
            out_time = frappe.db.get_value('Attendance' ,{'employee':emp,"attendance_date":date},'out_time') or ''
            ot_hrs = frappe.db.get_value('Attendance' ,{'employee':emp,"attendance_date":date},'overtime_hours') or 0
            ot_hrs=float(ot_hrs)
            ot_tot+=ot_hrs
            data += "<tr><td style = 'border: 1px solid black;'>%s</td><td style = 'border: 1px solid black;'>%s</td><td style = 'border: 1px solid black;'>%s</td><td style = 'border: 1px solid black;'>%s</td><td style = 'border: 1px solid black;'>%s</td><td style = 'border: 1px solid black;'>%s</td><td style = 'border: 1px solid black;'>%s</td></tr>"%(d,day,holiday or 'W',format_datetime(in_time) or '',format_datetime(out_time) or '',status_format,ot_hrs)
        ot=str(ot_tot)+' Hrs'
        data += "<tr><td colspan=4 style = 'border: 1px solid black;background-color:#ADD8E6;'></td><td colspan=2 style = 'border: 1px solid black;background-color:#ADD8E6;'><center><b>TOTAL</b></center></td><td style = 'border: 1px solid black;background-color:#ADD8E6'><b>%s</b></td></tr>"%(ot)
        data += "<tr><td colspan=3>P - Present<br>A - Absent<br>OL - On Leave</td><td colspan=2>HD - Half Day<br>WFH - Work From Home<br>CO - Compensatory Off</td><td colspan=2>SL - Sick Leave<br>CL - Casual Leave<br>EL - Earned Leave</td></tr>"
        data += "</table>"
    else:
        frappe.errprint("Test")
        data = "<table class='table table-bordered=1'>"
        data += "<tr><td style = 'border: 1px solid black;background-color:#ADD8E6;'><b>ID</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;'colspan=1><b>%s</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;'><b>Name</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;' colspan=2><b>%s</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;'><b>Dept</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;' colspan=1><b>%s</b></td></tr>"%(emp,emp_details[0],emp_details[1])
        data += "<tr><td style = 'border: 1px solid black;'colspan=7><b><center>Attendance</center></b></td>"
        data += "<tr><td style = 'border: 1px solid black;background-color:#ADD8E6'><b>Date</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;'><b>Day</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;'><b>Working</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;'><b>Status</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;'><b>In Time</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;'><b>Out Time</b></td><td style = 'border: 1px solid black;background-color:#ADD8E6;'><b>OT Hrs</b></td></tr>"   
        ot_tot=0
        for date in dates:
            status_format = get_status(emp,date)
            dt = datetime.strptime(date,'%Y-%m-%d')
            d = dt.strftime('%d-%b')
            day = datetime.date(dt).strftime('%a')
            holiday  = check_holiday(emp,date)
            in_time = frappe.db.get_value('Attendance' ,{'employee':emp,"attendance_date":date},'in_time') or ''
            out_time = frappe.db.get_value('Attendance' ,{'employee':emp,"attendance_date":date},'out_time') or ''
            ot_hrs = frappe.db.get_value('Attendance' ,{'employee':emp,"attendance_date":date},'overtime_hours') or 0
            ot_hrs=float(ot_hrs)
            ot_tot+=ot_hrs
            data += "<tr><td style = 'border: 1px solid black;'>%s</td><td style = 'border: 1px solid black;'>%s</td><td style = 'border: 1px solid black;'>%s</td><td style = 'border: 1px solid black;'>%s</td><td style = 'border: 1px solid black;'>%s</td><td style = 'border: 1px solid black;'>%s</td><td style = 'border: 1px solid black;'>%s</td></tr>"%(d,day,holiday or 'W',status_format,format_datetime(in_time) or '',format_datetime(out_time) or '',ot_hrs)
        ot=str(ot_tot)+' Hrs'
        data += "<tr><td colspan=4 style = 'border: 1px solid black;background-color:#ADD8E6;'></td><td colspan=2 style = 'border: 1px solid black;background-color:#ADD8E6;'><center><b>TOTAL</b></center></td><td style = 'border: 1px solid black;background-color:#ADD8E6'><b>%s</b></td></tr>"%(ot)
        data += "<tr><td colspan=3>P - Present<br>A - Absent<br>OL - On Leave</td><td colspan=2>HD - Half Day<br>WFH - Work From Home<br>CO - Compensatory Off</td><td colspan=2>SL - Sick Leave<br>CL - Casual Leave<br>EL - Earned Leave</td></tr>"
        data += "</table>"

    return data

def check_holiday(emp,date):
    holiday_list = frappe.db.get_value('Employee',{'name':emp},'holiday_list')
    holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List`
    left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(holiday_list,date),as_dict=True)
    doj= frappe.db.get_value("Employee",{'name':emp},"date_of_joining")
    status = ''
    if frappe.db.exists('Shift Assignment',{'start_date':date,'employee':emp,'shift_type':'WW','docstatus':1}):
        return "WW"
    elif holiday :
        if doj < holiday[0].holiday_date:
            if holiday[0].weekly_off == 1:
                return "WW"     
            else:
                return "HH"

def get_status(emp,date):
    status = ''
    if frappe.db.exists('Attendance',{'employee':emp,'attendance_date':date,'docstatus':['!=','2']}):
        shift = frappe.db.get_value('Attendance',{'employee':emp,'attendance_date':date,'docstatus':['!=','2']},['status','employee_type','shift'])
        holiday = check_holiday(emp,date)
        if holiday:
            if shift[2]:
                shift = shift[2] + holiday
            else:
             shift = holiday
        else:
            shift = shift[0]
        # frappe.errprint([date,shift])
        if shift[1] == "WC":
            status = wc_status_map.get(shift, "")
        else:
            status = bc_status_map.get(shift, "")
    return status

bc_status_map = {
    "Absent": "A",
    "AA":"AA",
    "Half Day": "HD",
    "Holiday": "HH",
    "WW": "WW",
    "Weekly Off": "WW",
    "1H": "1H",
    "2H": "2H",
    "3H": "3H",
    "1W": "1W",
    "2W": "2W",
    "3W": "3W",
    "PP1W": "PP1W",
    "PP2W": "PP2W",
    "1LH": "1LH",
    "2LH": "2LH",
    "3LH": "3LH",
    "1LW": "1LW",
    "2LW": "2LW",
    "3LW": "3LW",
    "PP1LW": "PP1LW",
    "PP2LW": "PP2LW",
    "MW": "MW",
    "On Leave": "L",
    "Present": "P",
    "Work From Home": "WFH",
    "MM": "AA",
    "11": "11",
    "22": "22",
    "33": "33",
    "PP1PP1": "P1P1",
    "PP2PP2": "P2P2",
    "1L1": "1L1",
    "2L2": "2L2",
    "3L3": "3L3",
    "2L3": "AA",
    "1L2": "AA",
    "3L1": "AA",
    "1LM": "1LM",
    "2LM": "2LM",
    "3LM": "3LM",
    "PP2LM":"P2LM",
    "PP1LPP1": "P1LP1",
    "PP2LPP2": "P2LP2",
    "1M": "1M",
    "2M": "2M",
    "3M": "3M",
    "M1": "M1",
    "M2": "M2",
    "M3": "M3",
    "PP1M": "P1M",
    "PP2M": "P2M",
    "MPP1": "MP1",
    "MPP2": "MP2",
    "11": "11",
    "12": "12",
    "13": "13",
    "1PP1": "1P1",
    "1PP2": "1P2",
    "21": "21",
    "22": "22",
    "23": "23",
    "2PP1": "2P1",
    "2PP2": "2P2",
    "31": "31",
    "32": "32",
    "33": "33",
    "3PP1": "3P1",
    "3PP2": "3P2",
    "PP11": "P11",
    "PP12": "P12",
    "PP13": "P13",
    "PP1PP1": "P1P1",
    "PP1PP2": "P1P2",
    "PP21": "P2P1",
    "PP22": "P2P2",
    "PP23": "P2P3",
    "PP2PP1": "P2P1",
    "PP2PP2": "P2P2",
    "Earned Leave": "EL",
    "Casual Leave": "CL",
    "Sick Leave": "SL",
    "OD": "OD",
    "Compensatory Off": "CO",
    "Leave Without Pay": "LL",
    "0.5Earned Leave": "0.5EL",
    "0.5Casual Leave": "0.5CL",
    "0.5Sick Leave": "0.5SL",
    "0.5Compensatory Off": "0.5CO",
    "0.5Leave Without Pay": "0.5LL",
    "LEarned Leave/2": "0.5SL",
    "LCasual Leave/2": "0.5LCL",
    "0.5Leave Without PayW": "1W",
    "LSick Leave/2": "0.5LSL",
    "LSpecial Leave/2": "0.5LSPL",
    "LCompensatory Off/2": "0.5LCO",
    "LLeave Without Pay/2": "0.5LLL",
    "0.5Special Leave": "0.5SPL",
    "Special Leave": "SPL",
    "AAWW": "WW",
    "AAHH": "HH",
    "11WW": "11W",
    "11HH": "11H",
    "22WW": "22W",
    "22HH": "22H",
    "33WW": "33W",
    "33HH": "33H",
    "PP2PP2WW": "PP2PP2W",
    "PP2PP2HH": "PP2PP2H",
    "1WW": "1W",
    "1HH": "1H",
    "2WW": "2W",
    "2HH": "2H",
    "3WW": "3W",
    "3HH": "3H",
    "PP2WW": "PP2W",
    "PP2HH": "PP2H",
    "ODWW": "ODW"
    }

wc_status_map = {
    "Absent": "A",
    "AA": "AA",
    "Half Day": "HD",
    "Holiday": "HH",
    "1H": "1H",
    "2H": "2H",
    "3H": "3H",
    "1W": "1W",
    "2W": "2W",
    "3W": "3W",
    "PP1W": "PP1W",
    "PP2W": "PP2W",
    "PP1H": "P1H",
    "PP2H": "P2H",
    "Weekly Off": "WW",
    "On Leave": "L",
    # "Present": "11",
    "Work From Home": "WFH",
    "OD": "OD",
    "Earned Leave": "EL",
    "Casual Leave": "CL",
    "Sick Leave": "SL",
    "Compensatory Off": "CO",
    "Leave Without Pay": "LL",
    "1": "11",
    "2": "22",
    "3": "33",
    " ": "MM",
    "PP1": "P1P1",
    "PP2": "P2P2",
    "1L": "1L1",
    "2L": "2L2",
    "3L": "3L3",
    "PP1L": "P1LP1",
    "PP2L": "P2LP2",
    "1LH": "1LH",
    "2LH": "2LH",
    "3LH": "3LH",
    "1LW": "1LW",
    "2LW": "2LW",
    "3LW": "3LW",
    "PP1LW": "PP1LW",
    "PP2LW": "PP2LW",
    "1M": "1M",
    "2M": "2M",
    "3M": "3M",
    "M1": "M1",
    "M2": "M2",
    "M3": "M3",
    "PP1M": "P1M",
    "PP2M": "P2M",
    "MPP1": "MP1",
    "MPP2": "MP2",
    "0.5Earned Leave": "0.5EL",
    "0.5Casual Leave": "0.5CL",
    "0.5Sick Leave": "0.5SL",
    "0.5Compensatory Off": "0.5CO",
    "0.5Leave Without Pay": "0.5LL",
    "0.5Leave Without PayW": "1W",
    "LEarned Leave/2": "0.5SL",
    "LCasual Leave/2": "0.5LCL",
    "LSick Leave/2": "0.5LSL",
    "LSpecial Leave/2": "0.5LSPL",
    "LCompensatory Off/2": "0.5LCO",
    "LLeave Without Pay/2": "0.5LLL",
    "0.5Special Leave": "0.5SPL",
    "Special Leave": "SPL",
    "AAWW": "WW",
    "AAHH": "HH",
    "1WW": "1W",
    "1HH": "1H",
    "2WW": "2W",
    "2HH": "2H",
    "3WW": "3W",
    "3HH": "3H",
    "PP2WW": "PP2W",
    "PP2HH": "PP2H",
    "ODWW": "ODW"
    }

@frappe.whitelist()
def get_employee():
    emp_details = frappe.db.get_value('Employee',{'user_id':frappe.session.user},['employee','employee_name','department'])
    return emp_details

@frappe.whitelist()
def get_employee_details(employee):
    emp_details = frappe.db.get_value('Employee',{'name':employee},['employee_name','department'])
    return emp_details

@frappe.whitelist()
def get_department_hods(user=None):
    if not user:
        user = frappe.session.user
    department_list = frappe.db.get_values(
        'Department',
        filters={'hod': user},
        fieldname=['name'],  
        as_dict=False
    )
    return list(map(lambda x: x[0], department_list))