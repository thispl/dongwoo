// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Attendance Settings', {
	refresh: function(frm) {
        frm.disable_save(); 
    },
	onload: function(frm) {
        frm.disable_save(); 
    },
	process_checkin(frm){
		frappe.call({
			"method": "dongwoo.attendance_custom.get_urc_to_ec",
			"args":{
				"from_date" : frm.doc.date,
			},
			freeze: true,
			freeze_message: 'Processing UnRegistered Employee Checkin to Employee Checkin....',
			callback(r){
				console.log(r.message)
				if(r.message == "ok"){
					frappe.msgprint("Checkin's are created in Successfully")
				}
			}
		})
	},
	process_sa(frm){
		if (frm.doc.employee && frm.doc.from_date && frm.doc.to_date){
			frappe.call({
				"method": "dongwoo.dongwoo.doctype.attendance_settings.attendance_settings.process_shift_allowance_with_emp",
				"args":{
					"from_date" : frm.doc.from_date,
					"to_date" : frm.doc.to_date,
					"emp": frm.doc.employee
				},
				freeze: true,
				freeze_message: 'Processing Shift Allowance....',
				callback(r){
					console.log(r.message)
					if(r.message == "ok"){
						frappe.msgprint("Shift Allowances are marked Successfully")
					}
				}
			})
		}
		else if (frm.doc.employee_type && frm.doc.from_date && frm.doc.to_date){
			frappe.call({
				"method": "dongwoo.dongwoo.doctype.attendance_settings.attendance_settings.process_shift_allowance_with_employee_type",
				"args":{
					"from_date" : frm.doc.from_date,
					"to_date" : frm.doc.to_date,
					"employee_type": frm.doc.employee_type
				},
				freeze: true,
				freeze_message: 'Processing Shift Allowance....',
				callback(r){
					console.log(r.message)
					if(r.message == "ok"){
						frappe.msgprint("Shift Allowances are marked Successfully")
					}
				}
			})
		}
		else{
			frappe.call({
				"method": "dongwoo.dongwoo.doctype.attendance_settings.attendance_settings.process_shift_allowance",
				"args":{
					"from_date" : frm.doc.from_date,
					"to_date" : frm.doc.to_date,
				},
				freeze: true,
				freeze_message: 'Processing Shift Allowance....',
				callback(r){
					console.log(r.message)
					if(r.message == "ok"){
						frappe.msgprint("Shift Allowances are marked Successfully")
					}
				}
			})
		}
		
	},
	process_sp_all(frm){
		if (frm.doc.employee && frm.doc.from_date && frm.doc.to_date){
			frappe.call({
				"method": "dongwoo.attendance_custom.create_special_allow_emp",
				"args":{
					"fdate" : frm.doc.from_date,
					"tdate" : frm.doc.to_date,
					"emp":frm.doc.employee
				},
				freeze: true,
				freeze_message: 'Processing Special Allowance....',
				callback(r){
					console.log(r.message)
					if(r.message == "ok"){
						frappe.msgprint("Special Allowances are created Successfully")
					}
				}
			})
		}
		else if (frm.doc.employee_type && frm.doc.from_date && frm.doc.to_date){
			frappe.call({
				"method": "dongwoo.attendance_custom.create_special_allow_employee_type",
				"args":{
					"fdate" : frm.doc.from_date,
					"tdate" : frm.doc.to_date,
					"employee_type":frm.doc.employee_type
				},
				freeze: true,
				freeze_message: 'Processing Special Allowance....',
				callback(r){
					console.log(r.message)
					if(r.message == "ok"){
						frappe.msgprint("Special Allowances are created Successfully")
					}
				}
			})
		}
		else{
			frappe.call({
				"method": "dongwoo.attendance_custom.create_special_allow",
				"args":{
					"fdate" : frm.doc.from_date,
					"tdate" : frm.doc.to_date,
					"emp":frm.doc.employee
				},
				freeze: true,
				freeze_message: 'Processing Special Allowance....',
				callback(r){
					console.log(r.message)
					if(r.message == "ok"){
						frappe.msgprint("Special Allowances are created Successfully")
					}
				}
			})
		}
	},
	process_att(frm){
		if (frm.doc.employee && frm.doc.from_date && frm.doc.to_date){
			// console.log("HI")
			frappe.call({
				"method": "dongwoo.mark_attendance.mark_att_with_employee",
				"args":{
					"fdate" : frm.doc.from_date,
					"tdate": frm.doc.to_date,
					"employee": frm.doc.employee 
				},
				freeze: true,
				freeze_message: 'Processing Attendance....',
				callback(r){
					// console.log(r.message)
					if(r.message == "ok"){
						frappe.msgprint("Attendance are created Successfully")
					}
				}
			})
		}
		else if (frm.doc.employee_type && frm.doc.from_date && frm.doc.to_date){
			console.log("HI 1")
			if (!frm.doc.contractor_name){
				console.log("HI 2")
				frappe.call({
					"method": "dongwoo.mark_attendance.update_att_with_employee_type",
					"args":{
						"fdate" : frm.doc.from_date,
						"tdate": frm.doc.to_date,
						"employee_type": frm.doc.employee_type 
					},
					freeze: true,
					freeze_message: 'Processing Attendance....',
					callback(r){
						// console.log(r.message)
						if(r.message == "ok"){
							frappe.msgprint("Attendance are created Successfully")
						}
					}
				})
			}
			else{
				console.log("HI 3")
				frappe.call({
					"method": "dongwoo.mark_attendance.update_att_with_con_name",
					"args":{
						"fdate" : frm.doc.from_date,
						"tdate": frm.doc.to_date,
						"employee_type": frm.doc.employee_type ,
						"con_name":frm.doc.contractor_name
					},
					freeze: true,
					freeze_message: 'Processing Attendance....',
					callback(r){
						// console.log(r.message)
						if(r.message == "ok"){
							frappe.msgprint("Attendance are created Successfully")
						}
					}
				})
			}
				
		}
		else{
			console.log("HII")
			frappe.call({
				"method": "dongwoo.mark_attendance.update_att_without_employee",
				"args":{
					"fdate" : frm.doc.from_date,
					"tdate": frm.doc.to_date 
				},
				freeze: true,
				freeze_message: 'Processing Attendance....',
				callback(r){
					console.log(r.message)
					if(r.message == "ok"){
						frappe.msgprint("Attendance are created Successfully")
					}
				}
			})
		}
	},
    // process_ur(frm) {
	// 	//  if (!frm.doc.from_date) {
	// 	// 	 frappe.msgprint("Please select From Date"); return; 
	// 	// 	} 
	// 	// frappe.call({
	// 	// 	method: "dongwoo.dongwoo.doctype.attendance_settings.attendance_settings.get_urc_to_ec", 
	// 	// 	args: { from_date: frm.doc.from_date }, 
	// 	// 	freeze: true, freeze_message: "Processing Checkins....", 
	// 	// 	callback: function(r) { 
	// 	// 		console.log("Response:", r.message); 
	// 	// 		if (r.message && r.message.status === "ok"){
	// 	// 			frappe.msgprint("Checkins Created successfully");
	// 	// 		} 
	// 	// 	}
	// 	// }); 
	// 	if (frm.doc.employee){
		
	// 		frappe.call({
	// 			"method": "dongwoo.dongwoo.doctype.attendance_settings.attendance_settings.get_urc_to_ec",
	// 			"args":{
	// 				"from_date" : frm.doc.from_date,
	// 				"to_date": frm.doc.to_date,
	// 				"employee": frm.doc.employee,
	// 				"employee_type": frm.doc.employee_type
	// 			},
	// 			freeze: true,
	// 			freeze_message: 'Processing UnRegistered Employee Checkin to Employee Checkin....',
	// 			callback(r){
					
	// 				if(r.message == "ok"){
	// 					frappe.msgprint("Checkins are created Successfully")
	// 				}
	// 			}
	// 		})
	// 	}
		
	
	// }

	process_ur(frm) {

    if (!frm.doc.from_date) {
        frappe.msgprint("Please select From Date");
        return;
    }

    if (!frm.doc.to_date) {
        frappe.msgprint("Please select To Date");
        return;
    }

    if (!frm.doc.employee && !frm.doc.employee_type) {
        frappe.msgprint("Please select Employee or Employee Type");
        return;
    }

    frappe.call({
        method: "dongwoo.dongwoo.doctype.attendance_settings.attendance_settings.get_urc_to_ec",

        args: {
            from_date: frm.doc.from_date,
            to_date: frm.doc.to_date,
            employee: frm.doc.employee || null,
            employee_type: frm.doc.employee_type || null
        },

        freeze: true,

        freeze_message:
            "Processing Unregistered Employee Checkin to Employee Checkin...",

        callback: function(r) {

            console.log("Response:", r.message);

            if (r.message && r.message.status === "ok") {

                frappe.msgprint({
                    title: "Success",
                    message: r.message.message,
                    indicator: "green"
                });

            } else if (r.message) {

                frappe.msgprint({
                    title: "Result",
                    message: r.message,
                    indicator: "blue"
                });
            }
        }
    });
}
	
});
