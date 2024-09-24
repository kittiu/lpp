// Copyright (c) 2024, Ecosoft and contributors
// For license information, please see license.txt

// frappe.query_reports["Inventory Movement Report"] = {
// 	"filters": [

// 	]
// };

frappe.query_reports["Inventory Movement Report"] = {
    "filters": [
        {
            "fieldname": "item_name",
            "label": __("Item Name"),
            "fieldtype": "Link",
            "options": "Item",
            "reqd": 0,
            "width": "80px",
            "default": "",
            "description": __("Filter by Item Name")
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "reqd": 0,
            "default": frappe.datetime.add_months(frappe.datetime.nowdate(), -1),
            "description": __("Filter by From Date")
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "reqd": 0,
            "default": frappe.datetime.nowdate(),
            "description": __("Filter by To Date")
        },
        {
            "fieldname": "warehouse",
            "label": __("Warehouse"),
            "fieldtype": "Link",
            "options": "Warehouse",
            "reqd": 0,
            "default": "",
            "description": __("Filter by Warehouse")
        }
    ]
};

