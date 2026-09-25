// Copyright (c) 2025, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Attendance Upload', {
	year: function(frm) {
        set_dates(frm);
    },
    month: function(frm) {
        set_dates(frm);
    },
	to_date: function(frm) {
        if (frm.doc.from_date && frm.doc.to_date) {
            if (frm.doc.from_date > frm.doc.to_date) {
                frm.set_value('to_date', null); 
                frappe.msgprint(__('To Date cannot be less than From Date'));
            }
        }
    },
    from_date: function(frm) {
        if (frm.doc.from_date && frm.doc.to_date) {
            if (frm.doc.from_date > frm.doc.to_date) {
                frm.set_value('from_date', null);
                frappe.msgprint(__('From Date cannot be greater than To Date'));
            }
        }
    },
	get_template: function (frm) {
        window.location.href = repl(frappe.request.url +
                 '?cmd=%(cmd)s&from_date=%(from_date)s&to_date=%(to_date)s&department=%(department)s&category=%(category)s&name=%(name)s',{
                 cmd: "dongwoo.dongwoo.doctype.attendance_upload.attendance_upload.get_template",
                 from_date: frm.doc.from_date,
                 to_date: frm.doc.to_date,
                 department:frm.doc.department,
                 category:frm.doc.category,
                 name:frm.doc.name,
             })
         },
});
function set_dates(frm) {
    if (frm.doc.year && frm.doc.month) {
        const year = parseInt(frm.doc.year);
        const monthStr = frm.doc.month;

        const monthMap = {
            'Jan': 0, 'Feb': 1, 'Mar': 2, 'Apr': 3,
            'May': 4, 'June': 5, 'July': 6, 'Aug': 7,
            'Sep': 8, 'Oct': 9, 'Nov': 10, 'Dec': 11
        };

        const month = monthMap[monthStr];
        if (month !== undefined) {
            // First day of the month
            const fromDate = new Date(year, month, 1);
            // Last day of the month
            const toDate = new Date(year, month + 1, 0);

            frm.set_value('from_date', frappe.datetime.obj_to_str(fromDate));
            frm.set_value('to_date', frappe.datetime.obj_to_str(toDate));
        } else {
            frappe.msgprint('Invalid month selected.');
        }
    } else {
        frm.set_value('from_date', null);
        frm.set_value('to_date', null);
    }
}