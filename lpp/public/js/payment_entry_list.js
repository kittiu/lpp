frappe.listview_settings['Payment Entry'] = {
    onload: function(listview) {
        var filters = [];

        if (frappe.user.has_role('Payment Entry Receive')) {
            filters.push('Receive');
        }
        if (frappe.user.has_role('Payment Entry Pay')) {
            filters.push('Pay');
        }

        if (filters.length > 0) {
            // Apply the appropriate filters based on user roles
            listview.filter_area.add('Payment Entry', 'payment_type', 'in', filters);
        } 
        /*
            else {
                // Option 1: Redirect the user to the home page or another page
                frappe.msgprint(__('You do not have permission to view any Payment Entries.'));
                frappe.set_route(''); // Redirects to the home page
                return;
            }
        */
        listview.refresh();
    }
};
