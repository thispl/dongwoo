// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Permission', {
	permission_date(frm){
		frm.call('sat_res').then(j=>{
			// if (j.message) {
			// 	frm.fields_dict.perm.$wrapper.empty().append(j.message)
			// }
		})	
	},
	total_time(frm){
		frm.call('hour_res').then(j=>{
			
		})	
	},
	permission_from_time(frm){
		if (frm.doc.permission_to_time && frm.doc.permission_from_time){
			frappe.call({
				"method": "dongwoo.per_custom.calculate_flexible_time",
				"args":{
					"fdate" : frm.doc.permission_from_time,
					"tdate" : frm.doc.permission_to_time,
					"perm" : frm.doc.permission_date
				},
				callback(r){
					if(r.message){
						frm.set_value('total_time',r.message)
					}
				}
			})
		}
	},
	permission_to_time(frm){
		if (frm.doc.permission_to_time && frm.doc.permission_from_time && frm.doc.permission_date){
			frappe.call({
				"method": "dongwoo.per_custom.calculate_flexible_time",
				"args":{
					"fdate" : frm.doc.permission_from_time,
					"tdate" : frm.doc.permission_to_time,
					"perm" : frm.doc.permission_date,
					'name' :frm.doc.name				
				},
				callback: function(r) {
					if (r.message == 0) {
						frm.set_value('total_time', 0);
					} else {
						frm.set_value('total_time', r.message);
					}
				}
				
			})
		}
	}
		
						
});


