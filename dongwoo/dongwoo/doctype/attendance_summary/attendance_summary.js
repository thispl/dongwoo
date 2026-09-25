frappe.ui.form.on('Attendance Summary', {
	refresh: function (frm) {
        frm.fields_dict.html.$wrapper.empty();
        frm.disable_save();
        frappe.model.clear_table(frm.doc, "attendance");

        // Check if the user is a System Manager or if no employee is selected
        if (frappe.user.has_role('System Manager') || !frm.doc.employee) {
            frm.fields_dict.html.$wrapper.empty().append("<center><h2>Please select an employee</h2></center>");
            frm.set_value('employee', null); // Reset employee field
        
            // Set default values for from_date and to_date
			var today = frappe.datetime.nowdate();
			frm.set_value('from_date', frappe.datetime.month_start(today));
			frm.set_value('to_date', frappe.datetime.month_end(today));
        }
        frappe.db.get_value("Employee", {'user_id': frappe.session.user}, ['employee', 'employee_name','department'], (r) => {
            if (r){
                frm.set_value('employee', r.employee);
                frm.set_value('employee_name', r.employee_name);
                frm.set_value("department", r.department);
            }
        });
        // frm.set_df_property('employee','read_only',1)
        frm.fields_dict.html.$wrapper.empty().append('<center><h2>Loading Data....</h2></center>');
        frm.trigger('get_data'); // Moved here to ensure it's triggered after setting dates
    },
    onload: function (frm) {
        if (frm.doc.employee && frm.doc.from_date && frm.doc.to_date){
            frm.fields_dict.html.$wrapper.empty().append('<center><h2>Loading Data....</h2></center>');
        }
		if (frappe.user.has_role('System Manager')) {
            if (frm.fields_dict.employee) {
                frm.set_df_property('employee', 'read_only', 0); // Proper way to disable
                frm.set_value('employee', null);
                // frm.fields_dict.employee.$input.prop("disabled", true); 
		        // 	frm.set_value('employee', null); 
            }
        }
		// if (frappe.user.has_role('System Manager')) {
		// 	frm.fields_dict.employee.$input.prop("disabled", true); 
		// 	frm.set_value('employee', null); 
		// }
        else if (frappe.user.has_role('HOD')) {
            // console.log(frappe.user.has_role('HOD'))
            // frm.fields_dict.employee.$input.prop("disabled", true); 
			// frm.set_value('employee', null); 
            // console.log(frappe.session.user)
            frappe.call({
                method: 'dongwoo.dongwoo.doctype.attendance_summary.attendance_summary.get_department_hods',
                args: {
                    user: frappe.session.user
                },
                callback: function(response) {
                    if (response.message) {
                        let departments = response.message;
                        // console.log("HOD Departments:", departments);
            
                        // Apply filter after getting department values
                        frm.set_query('employee', function() {
                            return {
                                filters: {
                                    "status": "Active",
                                    "department": ['in', departments],
                                }
                            };
                        });
                    }
                }
            });
            
		}
        else {
            frm.set_df_property('employee', 'read_only', 1);
			frappe.call({
				method: 'dongwoo.dongwoo.doctype.attendance_summary.attendance_summary.get_employee',
				args: {},
				callback: function (r) {
					frm.set_value('employee', r.message[0]);
					frm.set_value('employee_name', r.message[1]);
                    frm.fields_dict.html.$wrapper.empty().append('<center><h2>Loading Data....</h2></center>');
					frm.trigger('get_data');
				}
			});
            if (!frappe.user.has_role(['HR User'])) {

                frm.set_query('employee', function (doc) {
                    return {
                        filters: {
                            "status": "Active",
                            "department": frm.doc.department,
                            "user_id":frappe.session.user 
                        }
                    };
                });
            }
			
		}
	
		// Set default values for from_date and to_date
        var today = frappe.datetime.nowdate();
        frm.set_value('from_date', frappe.datetime.month_start(today));
        frm.set_value('to_date', frappe.datetime.month_end(today));

        frm.fields_dict.html.$wrapper.empty().append('<center><h2>Loading Data....</h2></center>');
		frm.trigger('get_data');
	},

    from_date: function (frm) {
        frm.fields_dict.html.$wrapper.empty().append('<center><h2>Loading Data....</h2></center>');
        frm.trigger('get_data');
    },
    to_date: function (frm) {
        frm.fields_dict.html.$wrapper.empty().append('<center><h2>Loading Data....</h2></center>');
        frm.trigger('get_data');
    },
    get_data: function (frm) {
        if (frm.doc.employee) {
            if (!frappe.is_mobile()) {
                frm.trigger('get_data_system');
            } else {
                frm.trigger('get_data_system');
            }
        } else {
            frm.fields_dict.html.$wrapper.empty().append("<center><h2>Please select an employee</h2></center>");
        }
    },
    get_data_system: function (frm) {
        if (frm.doc.employee) {
            // console.log('TEST')
            frappe.call({
                method: "dongwoo.dongwoo.doctype.attendance_summary.attendance_summary.get_data_system",
                args: {
                    emp: frm.doc.employee,
                    from_date: frm.doc.from_date,
                    to_date: frm.doc.to_date
                },
                callback: function (r) {
                    frm.fields_dict.html.$wrapper.empty().append(r.message);
                }
            });
        } else {
            frm.fields_dict.html.$wrapper.empty().append("<center><h2>Attendance Not Found</h2></center>");
        }
    },
    get_data_mobile: function (frm) {
        if (frm.doc.employee) {
            frappe.call({
                method: "dongwoo.dongwoo.doctype.attendance_summary.attendance_summary.get_data_system",
                args: {
                    emp: frm.doc.employee,
                    from_date: frm.doc.from_date,
                    to_date: frm.doc.to_date
                },
                callback: function (r) {
                    frm.fields_dict.html.$wrapper.empty().append(r.message);
                }
            });
        } else {
            frm.fields_dict.html.$wrapper.empty().append("<center><h2>Attendance Not Found</h2></center>");
        }
    },
    employee(frm){
        if (frm.doc.employee){
            frm.fields_dict.html.$wrapper.empty().append('<center><h2>Loading Data....</h2></center>');
            if (frappe.user.has_role('HOD') && frappe.session.user !='Administrator') {
                frappe.call({
                    method: "dongwoo.dongwoo.doctype.attendance_summary.attendance_summary.get_employee_details",
                    args: { employee: frm.doc.employee },
                    callback: function (r) {
                        if (r.message) {
                            // console.log(r.message);
					        frm.set_value('employee_name', r.message[0]);
                            frm.set_value("department", r.message[0]);
                        }
                    }
                });
                frappe.call({
                    method: 'dongwoo.dongwoo.doctype.attendance_summary.attendance_summary.get_department_hods',
                    args: {
                        user: frappe.session.user
                    },
                    callback: function(response) {
                        if (response.message) {
                            let departments = response.message;
                            var emp = frm.doc.employee
                            var emp_department = frm.doc.department
                            let hod_employee
                            // console.log(departments)
                            // console.log(emp_department)
                            frappe.db.get_value("Employee", {'user_id': frappe.session.user}, ['employee'], (r) => {
                                if (r){
                                    hod_employee = r.employee;
                                }
                                if (hod_employee != emp){
                                    if (!departments.includes(emp_department)) {
                                        frm.set_value('employee','')
                                        frm.set_value('employee_name','');
                                        frm.set_value('department','');
                                        frappe.msgprint(`Insufficient Permission for Employee ${emp}`);
                                    }
                                    else{
                                        frm.fields_dict.html.$wrapper.empty().append('<center><h2>Loading Data....</h2></center>');
                                        frm.trigger('get_data');
                                    }
                                }
                                else{
                                    frm.fields_dict.html.$wrapper.empty().append('<center><h2>Loading Data....</h2></center>');
                                    frm.trigger('get_data');
                                }
                            });
                        }
                    }
                });
            }
            else{
                frm.fields_dict.html.$wrapper.empty().append('<center><h2>Loading Data....</h2></center>');
                frm.trigger('get_data');
            }
            
        }
        else{
            frm.fields_dict.html.$wrapper.empty().append("<center><h2>Please select an employee</h2></center>");
            frm.set_value('employee_name','')
            frm.set_value('department','')
        }

    }
});


