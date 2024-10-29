// Copyright (c) 2024, Ecosoft and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sample Record", {
	refresh(frm) {
        if (frm.is_new()) {
            frm.events.set_table_parameters(frm)
        }        
	},
    customer: function(frm) {
        if (frm.doc.customer) {
            // Call server script to get filtered items based on selected customer
            frappe.call({
                method: "lpp.lpp.doctype.sample_record.sample_record.get_customer_items",
                args: {
                    customer_name: frm.doc.customer
                },
                callback: function(response) {
                    const items = response.message || [];

                    // Filter item_code field based on server response
                    frm.set_query('item_code', function() {
                        return {
                            filters: [
                                ['Item', 'name', 'in', items]  // Show only items in the list
                            ]
                        };
                    });

                    // Clear item_code, item_name if it does not match the filtered items
                    if (!items.includes(frm.doc.item_code)) {
                        frm.set_value({
                            'item_code': null,
                            'item_name': null
                        });
                    }
                }
            });
        } else {
            // Clear item_code, item_name if no customer is selected
            frm.set_value({
                'item_code': null,
                'item_name': null
            });

            // Remove filters to show all items in item_code
            frm.set_query('item_code', function() {
                return {};
            });
        }
    },
    set_table_parameters: function (frm) {
        // Clear existing rows
        frm.clear_table('sample_parameters');

        // Example data to add
        const set_parameters = [
            { sample_parameters: 'Planned Date' },
            { sample_parameters: 'Actual Date' }
        ];

        // Add new rows
        set_parameters.forEach(data => {
            const child = frm.add_child('sample_parameters');
            frappe.model.set_value(child.doctype, child.name, 'sample_parameters', data.sample_parameters);
        });
        // Refresh the child table to show changes
        frm.refresh_field('sample_parameters');
    },
});
