// Copyright (c) 2025, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Live Attendance', {
	refresh: function(frm) {
		frm.disable_save()
        const now = frappe.datetime.now_time();
        if (now < '08:30:00') {
            const yesterday = frappe.datetime.add_days(frappe.datetime.get_today(), -1);
            frm.set_value('date', yesterday);
        }
		if(frm.doc.date){
            frappe.call({
                method: "dongwoo.dongwoo.doctype.live_attendance.live_attendance.get_att_data",
                args:{
                    date:frm.doc.date
                },
                freeze: true,  
                freeze_message: __("<strong style='font-size:26px;'><b>Processing...</b></strong>"),
                callback: function (r) {
                    frm.fields_dict.attendance_data.$wrapper.empty().append(r.message)
                }
            })
        }
	},
	date(frm) {
        if(frm.doc.date){
            frappe.call({
                method: "dongwoo.dongwoo.doctype.live_attendance.live_attendance.get_att_data",
                args:{
                    date:frm.doc.date
                },
                freeze: true,  
                freeze_message: __("<strong style='font-size:26px;'><b>Processing...</b></strong>"),
                callback: function (r) {
                    frm.fields_dict.attendance_data.$wrapper.empty().append(r.message)
                }
        })
        }
	}
});
