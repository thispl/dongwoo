import frappe
from datetime import datetime
import traceback
@frappe.whitelist(allow_guest=True)
def mark_checkin(**args):
    if frappe.db.exists('Employee',{'biometric_pin':args['employee'],'status':'Active'}):
        employee = frappe.db.get_value('Employee',{'biometric_pin':args['employee'],'status':'Active'},['name'])
        if employee:
            try:
                if args['device_id'] == 'IN 1' or args['device_id'] == 'IN 2':
                    if not frappe.db.exists('Employee Checkin',{'employee':employee,'time':args['time']}):
                        ec = frappe.new_doc('Employee Checkin')
                        ec.employee = employee
                        ec.time = args['time']
                        ec.device_id = args['device_id']
                        ec.log_type = 'IN'
                        ec.save(ignore_permissions=True)
                        frappe.db.commit()
                        return "Checkin Marked"
                    else:
                        return "Checkin Marked"
                elif args['device_id'] == 'OUT 1' or args['device_id'] == 'OUT 2':
                    if not frappe.db.exists('Employee Checkin',{'employee':employee,'time':args['time']}):
                        ec = frappe.new_doc('Employee Checkin')
                        ec.employee = employee
                        ec.time = args['time']
                        ec.device_id = args['device_id']
                        ec.log_type = 'OUT'
                        ec.save(ignore_permissions=True)
                        frappe.db.commit()
                        return "Checkin Marked" 
                    else:
                        return "Checkin Marked" 
                else:
                    return "Checkin Markeds"
        
            except:
                frappe.log_error(title="checkin error1",message=args)
    else:
        try:
            if args['device_id'] == 'IN 1' or args['device_id'] == 'IN 2':
                if not frappe.db.exists('Unregistered Employee Checkin',{'biometric_pin':args['employee'],'biometric_time':args['time']}):
                    ec = frappe.new_doc('Unregistered Employee Checkin')
                    ec.biometric_pin = args['employee']
                    ec.biometric_time = args['time']
                    ec.locationdevice_id = args['device_id']
                    ec.log_type = 'IN'
                    ec.save(ignore_permissions=True)
                    frappe.db.commit()
                    return "Checkin Unmarked"
                else:
                    return "Checkin Unmarked"
            elif args['device_id'] == 'OUT 1' or args['device_id'] == 'OUT 2':
                if not frappe.db.exists('Unregistered Employee Checkin',{'biometric_pin':args['employee'],'biometric_time':args['time']}):
                    ec = frappe.new_doc('Unregistered Employee Checkin')
                    ec.biometric_pin = args['employee']
                    ec.biometric_time = args['time']
                    ec.locationdevice_id = args['device_id']
                    ec.log_type = 'OUT'
                    ec.save(ignore_permissions=True)
                    frappe.db.commit()
                    return "Checkin Unmarked"
                else:
                    return "Checkin Unmarked"
            else:
                return "Checkin Unmarked"
    
        except:
            frappe.log_error(title="checkin error",message=args)

import traceback
from datetime import datetime

@frappe.whitelist(allow_guest=True)
def mark_checkin_canteen(**args):
    if frappe.db.exists('Employee', {'biometric_pin': args['employee'],'status':'Active'}):
        employee = frappe.db.get_value('Employee',{'biometric_pin':args['employee'],'status':'Active'},['name'])
        if employee:
            try:
                if args['device_id'] == 'C1' or args['device_id'] == 'C2':
                    if not frappe.db.exists('Canteen Checkin', {'employee': employee, 'time': args['time']}):
                        ec = frappe.new_doc('Canteen Checkin')
                        ec.employee = employee
                        ec.time = args['time']
                        time_str = args['time'] 
                        
                        try:
                            time_obj = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            time_obj = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S.%f')
                        
                        att_time = time_obj.time()  
                        att_date = time_obj.date()  
                        ec.date = att_date

                        meal_types = ['Breakfast', 'Lunch', 'Dinner', 'Supper']
                        meal_times = {}
                        for meal in meal_types:
                            bff = frappe.db.get_value("Meal Type", {'name': meal}, ['from_time'])
                            bft = frappe.db.get_value("Meal Type", {'name': meal}, ['to_time'])
                            meal_times[meal] = {'from_time': bff, 'to_time': bft}
                        
                        def parse_time(time_str):
                            try:
                                return datetime.strptime(str(time_str), '%H:%M:%S.%f').time()
                            except ValueError:
                                return datetime.strptime(str(time_str), '%H:%M:%S').time()
                        meal_time_objs = {}
                        for meal, times in meal_times.items():
                            meal_time_objs[meal] = {
                                'from_time': parse_time(times['from_time']),
                                'to_time': parse_time(times['to_time'])
                            }

                        ec.meal_type = ""
                        for meal, times in meal_time_objs.items():
                            if times['from_time'] <= att_time <= times['to_time']:
                                ec.meal_type = meal
                                break  

                        ec.device_id = args['device_id']
                        ec.save(ignore_permissions=True)
                        frappe.db.commit()
                        return "Checkin Marked"

            except Exception as e:
                error_message = f"Error occurred: {str(e)}"
                stack_trace = traceback.format_exc()
                frappe.log_error(title="Canteen Checkin Error", message=f"{error_message}\nStack Trace:\n{stack_trace}")
    else:
        try:
            if args['device_id'] == 'C1' or args['device_id'] == 'C2':
                if not frappe.db.exists('Unregistered Employee Checkin', {'biometric_pin': args['employee'], 'biometric_time': args['time']}):
                    ec = frappe.new_doc('Unregistered Employee Checkin')
                    ec.biometric_pin = args['employee']
                    ec.biometric_time = args['time']
                    time_str = args['time']  

                    try:
                        time_obj = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        time_obj = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S.%f')
                    
                    att_time = time_obj.time() 
                    att_date = time_obj.date()  
                    ec.date = att_date

                    meal_types = ['Breakfast', 'Lunch', 'Dinner', 'Supper']
                    meal_times = {}
                    for meal in meal_types:
                        bff = frappe.db.get_value("Meal Type", {'name': meal}, ['from_time'])
                        bft = frappe.db.get_value("Meal Type", {'name': meal}, ['to_time'])
                        meal_times[meal] = {'from_time': bff, 'to_time': bft}
                    
                    def parse_time(time_str):
                        try:
                            return datetime.strptime(str(time_str), '%H:%M:%S.%f').time()
                        except ValueError:
                            return datetime.strptime(str(time_str), '%H:%M:%S').time()

                    meal_time_objs = {}
                    for meal, times in meal_times.items():
                        meal_time_objs[meal] = {
                            'from_time': parse_time(times['from_time']),
                            'to_time': parse_time(times['to_time'])
                        }
                    ec.meal_type = ""
                    for meal, times in meal_time_objs.items():
                        if times['from_time'] <= att_time <= times['to_time']:
                            ec.meal_type = meal
                            break  

                    ec.locationdevice_id = args['device_id']
                    ec.save(ignore_permissions=True)
                    frappe.db.commit()
                    return "Checkin Unmarked"
        except Exception as e:
            error_message = f"Error occurred: {str(e)}"
            stack_trace = traceback.format_exc()
            frappe.log_error(title="Unregistered Checkin Error", message=f"{error_message}\nStack Trace:\n{stack_trace}")
