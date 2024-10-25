// Copyright (c) 2024, Ecosoft and contributors
// For license information, please see license.txt

frappe.query_reports["Material Transfer from Manufacture"] = {
	"filters": [
		{
			fieldname: "department",
			label: __("Department"),
			fieldtype: "Link",
			options: "Department",
		},
		{
			fieldname: "shift_type",
			label: __("Shift Type"),
			fieldtype: "Link",
			options: "Shift Type",
		},
		{
			fieldname: "stock_entry_id",
			label: __("Stock Entry"),
			fieldtype: "MultiSelectList",
			get_data: function(txt) {
				// Use Frappe's built-in function to get Stock Entry options
				return frappe.db.get_link_options("Stock Entry", txt);
			}
		},
		{
			fieldname: "already_printed",
			label: __("Already Printed"),
			fieldtype: "Select",
			options: "\nTrue\nFalse",  // Add True/False options for the select field
			default: 'True'
		}
	],

	// Use the onload event to adjust the width
	onload: function(report) {
		// Find the stock_entry_id filter element by using fieldname
		const stockEntryFilter = report.get_filter("stock_entry_id").$wrapper;

		// Remove the 'col-md-2' class to adjust the layout
		stockEntryFilter.removeClass('col-md-2');

		// Add custom class for width adjustment
		stockEntryFilter.addClass('col-md-3');
	},
};
