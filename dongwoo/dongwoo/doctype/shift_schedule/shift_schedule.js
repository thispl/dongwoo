// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Shift Schedule', {
	get_template: function (frm) {
	console.log(frm.doc.employee_type)
	console.log(frm.doc.department)
        window.location.href = repl(frappe.request.url +
            '?cmd=%(cmd)s&from_date=%(from_date)s&to_date=%(to_date)s&department=%(department)s&employee_type=%(employee_type)s&name=%(name)s',{
            cmd: "dongwoo.dongwoo.doctype.shift_schedule.shift_schedule.get_template",
            from_date: frm.doc.from_date,
            to_date: frm.doc.to_date,
            department:frm.doc.department,
			employee_type:frm.doc.employee_type,
			name:frm.doc.name
        })
	},
	// attach:function(frm){
	// 	if (frm.doc.attach){
	// 		frappe.call({
    //             method: "dongwoo.dongwoo.doctype.shift_schedule.shift_schedule.check_shift_assignment",
    //             args: {
    //                 'file': frm.doc.attach,
    //                 'from_date': frm.doc.from_date,
    //                 'to_date': frm.doc.to_date,
    //             },
    //             callback: function (r) {
    //                 frm.fields_dict.html.$wrapper.empty().append(r.message);
    //             }
    //         });
	// 	}
	// },
	to_date(frm) {
		if (frm.doc.to_date) {
			// if (frm.doc.to_date < frappe.datetime.now_date()) {
			// 	frappe.msgprint("To Date should not be a Past Date")
			// 	frm.set_value('to_date', '')
			// }
		    if (frm.doc.to_date < frm.doc.from_date) {
				frappe.msgprint("To Date should not be greater than From Date")
				frm.set_value('to_date', '')
			}
			// else if (frm.doc.to_date > frappe.datetime.add_days(frm.doc.from_date, 7)) {
			// 	frappe.msgprint("To Date should be within 8 days from From Date")
			// 	frm.set_value('to_date', '')
			// }
			else if (frm.doc.department && frm.doc.from_date && frm.doc.to_date)
			frm.call('validate').then(r => {
				frappe.msgprint(r.message)
				// console.log('Hi')
			})
		}
	},	
	// refresh: function(frm) {

	// }
});
