// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Overtime Request', {
	
	shift(frm) {
        var shift = frm.doc.shift;
        frappe.call({
            method: 'dongwoo.dongwoo.doctype.overtime_request.overtime_request.get_start_time',
            args: {
                employee: frm.doc.employee,
                ot_date: frm.doc.ot_date,
                shift: shift
            },
            callback: function(response) {
                if (response.message) {
						frm.set_value('from_time', response.message);
                }
            }
        });
    },
    ot_date(frm) {
        frappe.call({
            method: 'dongwoo.dongwoo.doctype.overtime_request.overtime_request.get_attendance_values',
            args: {
                employee: frm.doc.employee,
                ot_date: frm.doc.ot_date
            },
            callback: function(response) {
                if (response.message) {
                    if (response.message!='No'){
                        frm.set_value('shift', response.message.shift);
                        frm.set_value('to_time', response.message.out_time);
						frm.set_value('total_hour', response.message.total_working_hours);
						frm.set_value('total_hours', response.message.total_overtime_hours);
					}
                    
                }
            }
        });
        if (frm.doc.ot_date && frm.doc.employee){
            frappe.call({
                method: 'dongwoo.dongwoo.doctype.overtime_request.overtime_request.check_for_ot_hrs',
                args: {
                    employee: frm.doc.employee,
                    ot_date: frm.doc.ot_date,
                    // shift:frm.doc.shift
                },
                callback: function(response) {
                    if (response.message) {
                        if (response.message=='yes'){
                            frm.set_value('coff_applicable',1);

                        }
                        else{
                            frm.set_value('coff_applicable',0);

                        }
                        
                    }
                }
            });
        }
        
	},
    
});
