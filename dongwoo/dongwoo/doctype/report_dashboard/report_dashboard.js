// Copyright (c) 2023, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Report Dashboard', {
	start_date(frm) {
        if (frm.doc.report=='Monthly Salary Report'){
            if (frm.doc.start_date){
				let startDate = frappe.datetime.str_to_obj(frm.doc.start_date);
				if (startDate.getDate() !== 1) {
					frappe.msgprint(__('Kindly check the start date.'));
					frm.set_value('start_date', '');
					return;
				}
				else{
					frappe.call({
						method: 'dongwoo.dongwoo.doctype.report_dashboard.report_dashboard.get_end_date',
						args: {
							frequency: "Monthly",
							start_date: frm.doc.start_date
						},
						callback: function (r) {
							if (r.message) {
								frm.set_value('end_date', r.message.end_date);
							}
						}
					});
				}
                
            }
            else{
                frm.set_value('end_date', '');
            }
        }

	},
	download:function(frm){
		
		if (frm.doc.report == 'Personnel Record') {
			var path = 'dongwoo.dongwoo.doctype.report_dashboard.personnel_record.download'
			var args = 'start_date=%(start_date)s&end_date=%(end_date)s&employee_type=%(employee_type)s'
		}
		if (frm.doc.report == 'Organizational Chart') {
			if (frm.doc.employee_type=='D . Trainee'){
				var path = 'dongwoo.dongwoo.doctype.report_dashboard.d_trainee.download'
				var args = 'start_date=%(start_date)s&end_date=%(end_date)s&employee_type=%(employee_type)s'
			}  
			else if (frm.doc.employee_type == 'NAPS') {
				var path = 'dongwoo.dongwoo.doctype.report_dashboard.naps_trainee.download';
				var args = 'start_date=%(start_date)s&end_date=%(end_date)s&employee_type=%(employee_type)s';
			} 
			else if (frm.doc.employee_type == 'Worker'){
			var path = 'dongwoo.dongwoo.doctype.report_dashboard.organizational_chart.download'
			var args = 'start_date=%(start_date)s&end_date=%(end_date)s&employee_type=%(employee_type)s'
			}
			else if (frm.doc.employee_type == 'Staff'){
				var path = 'dongwoo.dongwoo.doctype.report_dashboard.staff_chart.download'
				var args = 'start_date=%(start_date)s&end_date=%(end_date)s&employee_type=%(employee_type)s'
				}
		}
		if (frm.doc.report == 'Overall Attendance Summary') {
			frappe.call({
				method : 'dongwoo.dongwoo.doctype.report_dashboard.overall_attendance_summary.download',
				args : {
					start_date : frm.doc.start_date,
					end_date : frm.doc.end_date
				}
			})
		}
		if (frm.doc.report == 'OT Report') {
			var path = 'dongwoo.dongwoo.doctype.report_dashboard.ot_report.download';
				var args = 'month=%(month)s&year=%(year)s';
		}
		if (frm.doc.report == 'Daily Attendance Summary') {
			frappe.call({
				method : 'dongwoo.dongwoo.doctype.report_dashboard.daily_summary.download',
				args : {
					start_date : frm.doc.start_date
				}
			})
		}
		
		if (frm.doc.report == "Monthly Salary Report for NAPS") {
			frappe.call({
				method: "dongwoo.dongwoo.doctype.report_dashboard.naps_salary_register.check_slip_exists",
				args: {
					start_date: frm.doc.start_date,
					end_date: frm.doc.end_date
				},
				callback: function(r) {
					if(r.message && r.message.exists) {
						let url = "/api/method/dongwoo.dongwoo.doctype.report_dashboard.naps_salary_register.download"
							+ "?start_date=" + encodeURIComponent(frm.doc.start_date)
							+ "&end_date=" + encodeURIComponent(frm.doc.end_date);
						window.open(url);
					} else {
						frappe.msgprint("Salary Slip not available for selected period.");
					}
				}
			});
		}

		
		
		

		if (frm.doc.report == "Trainee Salary Register") {
			console.log("Trainee");
		
			let url = "/api/method/dongwoo.dongwoo.doctype.report_dashboard.trainee_salary_register.download"
				+ "?start_date=" + encodeURIComponent(frm.doc.start_date)
				+ "&end_date=" + encodeURIComponent(frm.doc.end_date);
		
			window.open(url);
		}
		
		if (frm.doc.report == 'Today Canteen Count Report') {
			frappe.call({
				method : 'dongwoo.dongwoo.doctype.report_dashboard.today_summary.download',
				args : {
					start_date : frm.doc.start_date,
					end_date : frm.doc.end_date
				}
			})
		}
		if (frm.doc.report == 'CL Salary Register') {
			let url = "/api/method/dongwoo.dongwoo.doctype.report_dashboard.new_cl.download"
				+ "?start_date=" + frm.doc.start_date
				+ "&end_date=" + frm.doc.end_date
				+ "&contractor=" + frm.doc.contractor;
		
			window.open(url);
			
		}
		
		

		if (frm.doc.report == 'Monthly Salary Report') {
			if (!frm.doc.emp_type) {
				console.log("pass");
				var path = 'dongwoo.dongwoo.doctype.report_dashboard.monthly_salary_report.download';
				var args = 'start_date=%(start_date)s&end_date=%(end_date)s&company=%(company)';
			} else {
				if (frm.doc.emp_type == 'Staff & Worker') {
					var path = 'dongwoo.dongwoo.doctype.report_dashboard.monthly_salary_report_sw.download';
					var args = 'start_date=%(start_date)s&end_date=%(end_date)s&emp_type=%(emp_type)';
				}
				else if (frm.doc.emp_type == 'Staff') {
					var path = 'dongwoo.dongwoo.doctype.report_dashboard.monthly_salary_report_staff.download';
					var args = 'start_date=%(start_date)s&end_date=%(end_date)s&emp_type=%(emp_type)';
				}
				else if (frm.doc.emp_type == 'Worker') {
					var path = 'dongwoo.dongwoo.doctype.report_dashboard.monthly_salary_report_worker.download';
					var args = 'start_date=%(start_date)s&end_date=%(end_date)s&emp_type=%(emp_type)';
				}
				else if (frm.doc.emp_type == 'NAPS') {
					var path = 'dongwoo.dongwoo.doctype.report_dashboard.naps_salary_report.download';
					var args = 'start_date=%(start_date)s&end_date=%(end_date)s&emp_type=%(emp_type)';
				}
				else {
					var path = 'dongwoo.dongwoo.doctype.report_dashboard.monthly_salary_report_trainee.download';
					var args = 'start_date=%(start_date)s&end_date=%(end_date)s&emp_type=%(emp_type)';
				}
			}
		}
		
		if (frm.doc.report == 'EPF Statement report') {
			// console.log('hi')
			var path = 'dongwoo.dongwoo.doctype.report_dashboard.epf_report.download'
			var args = 'start_date=%(start_date)s&end_date=%(end_date)s&company=%(company)'
		
		}
		if (frm.doc.report == 'ESI Statement report') {
			var path = 'dongwoo.dongwoo.doctype.report_dashboard.esi_statement_report.download'
			var args = 'start_date=%(start_date)s&end_date=%(end_date)s&company=%(company)'
		}
		if (frm.doc.report == 'Billing Statement') {
			var path = 'dongwoo.dongwoo.doctype.report_dashboard.billing_report.download'
			var args = 'start_date=%(start_date)s&end_date=%(end_date)s&company=%(company)s&contractor=%(contractor)s';

		}
		if (path) {
			window.location.href = repl(frappe.request.url +
				'?cmd=%(cmd)s&%(args)s', {
				cmd: path,
				args: args,
				start_date : frm.doc.start_date,
				end_date : frm.doc.end_date,
				employee_type :frm.doc.employee_type,
                emp_type:frm.doc.emp_type,
				month:frm.doc.month,
				year:frm.doc.year,
                contractor:frm.doc.contractor
			});
		}
		if (frm.doc.report == "Salary Statement Summary") {
			var path = 'dongwoo.dongwoo.doctype.report_dashboard.salary_statement_summary.download'
			var args = 'start_date=%(start_date)s&end_date=%(end_date)s&employee_type=%(employee_type)s'
		}
		
		// frm.add_custom_button('View Current Status', () => {
		// 	frappe.call({
		// 		method: 'dongwoo.dongwoo.doctype.report_dashboard.report_dashboard.get_latest_rq_job',  // Update this path
		// 		callback: function(r) {
		// 			if (r.message) {
		// 				frappe.set_route('Form', 'RQ Job', r.message);
		// 			} else {
		// 				frappe.msgprint(__('No RQ Job found.'));
		// 			}
		// 		}
		// 	});
		// });
		frm.add_custom_button('View Current Status', () => {
            frappe.set_route('Form','RQ Job');
        });
		
	}
});
