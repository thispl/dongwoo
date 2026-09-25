// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('On Duty Application', {
	// validate(frm){
	// 	if (frm.doc.to_time && frm.doc.from_time){
	// 		if (frm.doc.from_time > frm.doc.to_time){
	// 			frappe.throw("From time should be less than To time. Kindly Check the time once again.")
	// 		}
	// 	}
		
	// },
	session(frm){
		if (frm.doc.session=='Flexible'){
			frm.set_value('from_time','')
			frm.set_value('to_date','')
		}
		else{
			frappe.call({
				"method": "dongwoo.dongwoo.doctype.on_duty_application.on_duty_application.get_shift_time",
				"args": {
					"name": frm.doc.shift,
					"session" : frm.doc.session
				},
				"callback": function(r) {
					if (r.message) {
						frm.set_value('from_time', r.message.start_time);
						frm.set_value('to_time', r.message.end_time);
					}
				}
			});
			
		}
	},
	shift(frm){
		if(frm.doc.session){
			if (frm.doc.session=='Flexible'){
				frm.set_value('from_time','')
				frm.set_value('to_time','')
			}
			else{
				frappe.call({
					"method": "dongwoo.dongwoo.doctype.on_duty_application.on_duty_application.get_shift_time",
					"args": {
						"name": frm.doc.shift,
						"session" : frm.doc.session
					},
					"callback": function(r) {
						if (r.message) {
							console.log(r.message)
							frm.set_value('from_time', r.message.start_time);
							frm.set_value('to_time', r.message.end_time);
						}
					}
				});
				
			}
		}
	},
	ffrom_time(frm){
		if (frm.doc.session=='Flexible'){
			if (frm.doc.tto_time && frm.doc.ffrom_time){
				frappe.call({
					"method": "dongwoo.on_duty_custom.calculate_od_time",
					"args":{
						"ftime" : frm.doc.ffrom_time,
						"ttime" : frm.doc.tto_time,
						// "od" : frm.doc.od_date
					},
					callback(r){
						if(r.message){
							frm.set_value('od_duration',r.message)
						}
					}
				})
			}
		}
	},
	tto_time(frm){
		if (frm.doc.session=='Flexible'){
			if (frm.doc.tto_time && frm.doc.ffrom_time && frm.doc.od_date){
				frappe.call({
					"method": "dongwoo.on_duty_custom.calculate_od_time",
					"args":{
						"ftime" : frm.doc.ffrom_time,
						"ttime" : frm.doc.tto_time,
						"od" : frm.doc.od_date,
						'name' :frm.doc.name				
					},
					callback: function(r) {
						if (r.message == 0) {
							frm.set_value('od_duration', 0);
						} else {
							frm.set_value('od_duration', r.message);
						}
					}
				
				
			})
		}
	}
	}
		
});
