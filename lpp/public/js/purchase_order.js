frappe.ui.form.on("Purchase Order", {
    refresh: function (frm) {
        // Check if the document is new (unsaved)
        if (frm.doc.__islocal) {
            // Hide the button if the document is new
            return;
        }

        var field = frm.fields_dict.status;
        console.log('field', field);
        // Check if the current user has the "Managing Director" role
        if (!frappe.user.has_role('Managing Director')) {
            // Add a custom button called "Send to MD"
            let btn = frm.add_custom_button(__('Send to MD'), function () {
                // Call the server-side method
                frappe.call({
                    method: 'lpp.custom.purchase_order.trigger_notification', // Adjust the method path as needed
                    args: {
                        docname: frm.doc.name // Pass the document name or any other necessary arguments
                    },
                    callback: function (r) {
                        if (!r.exc) {
                            // Handle the response (optional)
                            frappe.msgprint(__('Notification sent to MD successfully.'));
                        }
                    }
                });
            });
        }
    }
});

frappe.listview_settings['Purchase Order'] = {

    onload: function (listview) {
        // console.log('Original listview columns:', listview.columns);
        // console.log('Original listview data:', listview.data);

        listview.columns.forEach(field => {
            if (field.df && field.df.label === "Progress") {
                field.df.fieldname = 'status';
            }
        });
        listview.refresh();
    }
};
