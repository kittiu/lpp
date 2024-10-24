// Copyright (c) 2024, Ecosoft and contributors
// For license information, please see license.txt

frappe.query_reports["Molds Report"] = {
	"filters": [
		{
			fieldname: "type_item",
			label: __("Item Type"),
			fieldtype: "Select",
			options: [
				"Item",
				"Mold"
			],
			default: "Item",
			reqd: 1
		},
		{
            "fieldname": "item",
            "label": __("Item"),
            "fieldtype": "Link",
            "options": "Item",
            "reqd": 0 // Optional field
        }
	]
};
