// Copyright (c) 2025, TEAMPRO and contributors
// For license information, please see license.txt

frappe.ui.form.on('Mark Attendance', {
	// onload(frm) {
    //     if(!frm.doc.is__local){
    //         if (!frappe.user.has_role("Admin")) {
    //     frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    //         .then(r => {
    //             if (r.message && r.message.name) {
    //                 frm.set_value('employee', r.message.name);
    //                 frm.set_df_property('employee','read_only',1)
    //             }
    //         });
    //         }
    //     }
        
    // },
	refresh(frm) {
        let permission;
        let department_hod;
        frappe.call({
            method: "frappe.client.get",
            args: {
                doctype: "User",
                name: frappe.session.user
            },
            callback: function(response) {
                let user = response.message;
                // console.log(user);

                if (user && user.roles.some(role => role.role === "HOD")) {
                    console.log("User has HOD role.");
                    permission = 'HOD';
                }

                check_approval_buttons(frm, permission, department_hod);
                // frm.reload_doc();
            }
        });
        if (frm.doc.department) {
            frappe.db.get_value('Department', { "name": frm.doc.department }, 'hod')
                .then(r => {
                    department_hod = r.message.hod;
                    check_approval_buttons(frm, permission, department_hod);
                    // frm.reload_doc();
                });
        }
        if(frm.doc.approved_in_time == 1 && frm.doc.approved_out_time == 1){
            frm.set_df_property('employee','read_only',1)
            frm.set_df_property('purpose','read_only',1)
        }
    }
});
function check_approval_buttons(frm, permission, department_hod) {
    console.log("message1");
    if (frm.doc.approved_in_time == 0 && frm.doc.in_time && permission === 'HOD' && (department_hod === frappe.session.user || frappe.session.user =='Administrator')) {
        console.log("message");
        frm.add_custom_button(__('Approve In Time'), function () {
            frappe.call({
                freeze: true,
                freeze_message: 'Processing the data',
                method: "dongwoo.dongwoo.doctype.mark_attendance.mark_attendance.create_in_checkins",
                args: {
                    date: frm.doc.date,
                    employee: frm.doc.employee,
                    in_time: frm.doc.in_time,
                    name: frm.doc.name
                },
                callback: function(r) {
                    console.log(r.message);
                }
            });
            frm.set_value('approved_in_time', 1);
            frm.save();
            
        }).css({
            "background-color": "#0398fc",
            "color": "#fff",
            "border": "1px solid #0398fc"
        });
        
    }
    
    if (frm.doc.approved_out_time == 0 && frm.doc.out_time && permission === 'HOD' && (department_hod === frappe.session.user || frappe.session.user =='Administrator')) {
        frm.add_custom_button(__('Approve Out Time'), function () {
            frappe.call({
                freeze: true,
                freeze_message: 'Processing the data',
                method: "dongwoo.dongwoo.doctype.mark_attendance.mark_attendance.create_out_checkins",
                args: {
                    date: frm.doc.date,
                    employee: frm.doc.employee,
                    out_time: frm.doc.out_time,
                    name: frm.doc.name
                },
                callback: function(r) {
                    console.log(r.message);
                }
            });
            frm.set_value('approved_out_time', 1);
            frm.save();
        }).css({
            "background-color": "#0398fc",
            "color": "#fff",
            "border": "1px solid #0398fc"
        });
    }
}

