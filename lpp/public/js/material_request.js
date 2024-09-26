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
    validate: function (frm) {
        // sum grand total from item amount
        
        let items = frm.doc.items
        let total = 0
        for (let i = 0; i < items.length; i++) {
            total += items[i].amount
        }
        frm.set_value("custom_grand_total", total)        
    }

    
});
