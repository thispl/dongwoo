// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payroll Process', {
	late_in_and_early_out_process(frm){
		frappe.call({
			"method": "dongwoo.payroll_custom.attendance_calc",
			"args":{
				"from_date" : frm.doc.from_date,
				"to_date" : frm.doc.to_date,
			},
			freeze: true,
			freeze_message: 'Processing late....',
			callback(r){
				console.log(r.message)
				if(r.message == "ok"){
					frappe.msgprint("Late In and Early Out Penalty Created Successfully")
				}
			}
		})
	},
});
