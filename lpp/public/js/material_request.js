frappe.ui.form.on("Material Request", {
    onload: function(frm) {
        if (!frm.doc.custom_requester) {
            frappe.call({
                method: 'frappe.client.get_value',
                args: {
                    doctype: 'Employee',
                    filters: {
                        user_id: frappe.session.user
                    },
                    fieldname: 'name'
                },
                callback: function(response) {
                    if (response.message) {
                        frm.set_value('custom_requester', response.message.name);
                    } 
                }
            });
        }
    },
    refresh: function (frm) {
          // Check if the document is new (unsaved)
          if (frm.doc.__islocal) {
            // Hide the button if the document is new
            return;
        }

        // Check if the current user has the "Managing Director" role
        if (!frappe.user.has_role('Managing Director')) {
            // Add a custom button called "Send to MD"
            frm.add_custom_button(__('Send to MD'), function() {
                // Call the server-side method
                frappe.call({
                    method: 'lpp.custom.material_request.trigger_notification', // Adjust the method path as needed
                    args: {
                        docname: frm.doc.name // Pass the document name or any other necessary arguments
                    },
                    callback: function(r) {
                        if (!r.exc) {
                            // Handle the response (optional)
                            frappe.msgprint(__('Notification sent to MD successfully.'));
                        }
                    }
                });
            });
        }
    },
    validate: function (frm) {
        // sum grand total from item amount
        
        let items = frm.doc.items
        let total = 0
        for (let i = 0; i < items.length; i++) {
            total += items[i].amount
        }
        frm.set_value("custom_grand_total", total)        
    },
    schedule_date: function(frm) {
        // ตรวจสอบว่ามีการแก้ไขฟิลด์ schedule_date หรือไม่
        if (frm.doc.schedule_date) {
            // วนลูปผ่านรายการใน items เพื่อแก้ไขฟิลด์ schedule_date ของแต่ละรายการ
            frm.doc.items.forEach(function(item) {
                item.schedule_date = frm.doc.schedule_date;
            });
            // บันทึกข้อมูลการเปลี่ยนแปลงกลับไปที่ฟอร์ม
            frm.refresh_field('items');
        }
    },
    custom_cost_center : function(frm) {
        frm.doc.custom_department = frm.doc.custom_cost_center
        frm.refresh_field('custom_department');
    }
});

frappe.listview_settings['Material Request'] = {
    onload: function(listview) {
        // Check if 'columns' is accessible and iterable
        if (listview && listview.columns && Array.isArray(listview.columns)) {
            listview.columns.forEach(field => {
                if (field.df && field.df.label === "Progress") {
                    field.df.fieldname = 'status';
                }
            });

            listview.refresh(); // Refresh the list to apply changes
        }
    }
};