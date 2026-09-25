// Copyright (c) 2024, TEAMPRO and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Monthly Attendance Register"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1,
			on_change: function () {
				var from_date = frappe.query_report.get_filter_value('from_date')
				frappe.call({
					method: "dongwoo.dongwoo.report.monthly_attendance_register.monthly_attendance_register.get_to_date",
					args: {
						from_date: from_date
					},
					callback(r) {
						frappe.query_report.set_filter_value('to_date', r.message);
						frappe.query_report.refresh();
					}
				})
			}
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1,
		},
		{
			"fieldname": "employee_type",
			"label": __("Employee Type"),
			"fieldtype": "Link",
			"options": "Employee Type",
		},
		{
			"fieldname": "contractor",
			"label": __("Contractor"),
			"fieldtype": "Link",
			"options": "Contractor",
			"depends_on": "eval:doc.employee_type == 'Contract Employee'"
		},
		{
			"fieldname": "department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Department",
		},
		{
			"fieldname": "employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee"
		},
	],
	onload: function (report) {
		var employee = frappe.query_report.get_filter('employee');
		employee.refresh();
		var employee_category = frappe.query_report.get_filter('employee_type');
		employee_category.refresh();
		var department = frappe.query_report.get_filter('department');
		department.refresh();
		if (!frappe.user.has_role('System Manager' || "HR Manager" || "HR User" || "HOD")) {
			frappe.db.get_value("Employee", { 'user_id': frappe.session.user }, ["name", "employee_category", "department"], (r) => {
				employee.set_input(r.name);
				employee_category.set_input(r.employee_category); 
				department.set_input(r.department); 
			});
		}
	},
};
