frappe.listview_settings['Payment Entry'] = {
    onload: function(listview) {
        var filters = {};
        listview.filter_area.clear();
        if (frappe.user.has_role('Payment Entry Receive')) {
            filters['payment_type'] = ['in', ['Receive']];
        }
        if (frappe.user.has_role('Payment Entry Pay')) {
            filters['payment_type'] = ['in', ['Pay']];
        }
        if (frappe.user.has_role('Payment Entry Receive') && frappe.user.has_role('Payment Entry Pay')) {
            filters['payment_type'] = ['in', ['Receive', 'Pay']];
        }
        if (!frappe.user.has_role('Payment Entry Receive') && !frappe.user.has_role('Payment Entry Pay')) {
            filters['payment_type'] = ['in', []];
        }


        if (Object.keys(filters).length > 0) {
            // Set route options before the page loads
            frappe.route_options = filters;

            // Clear route options after the page loads to prevent filters from showing in the UI
            listview.page.add_action_item('Clear Filters', function() {
                frappe.route_options = null;
            });
        } 
        /*
            else {
                frappe.msgprint(__('You do not have permission to view any Payment Entries.'));
                frappe.set_route(''); // Redirect to the home page
                return;
            }
        */
    }
};
