frappe.ui.form.on("Material Request", {
    refresh: function (frm) {
          // Check if the document is new (unsaved)
          if (frm.doc.__islocal) {
            // Hide the button if the document is new
            return;
        }

        // Check if the current user has the "Managing Director" role
        if (!frappe.user.has_role('Managing Director')) {
            // Add a custom button called "Send to MD"
            let btn = frm.add_custom_button(__('Send to MD'), function() {
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
    material_request_type: function(frm) {
        switch(frm.doc.material_request_type) {
            case 'Purchase':
                frm.set_value('naming_series', 'PR.YY.MM.-.####');
                break;
            // TODO: Add more cases as needed for other material request types
            // TODO: Feature #5600 MatReq-ตอนสร้างถ้าเลือก purpose แล้วให้ auto เลือก series name
            default:
                frm.set_value('naming_series', '');
        }
    }
});
