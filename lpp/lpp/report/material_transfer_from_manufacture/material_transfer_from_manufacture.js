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
		}
	]
};
