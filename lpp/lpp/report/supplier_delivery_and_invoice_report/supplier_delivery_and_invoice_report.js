// Copyright (c) 2024, Ecosoft and contributors
// For license information, please see license.txt

frappe.query_reports["Supplier Delivery and Invoice Report"] = {
	"filters": [
		{
            "fieldname": "customer_name",
            "label": __("Customer Name"),
            "fieldtype": "Link",
            "options": "Customer",
            "reqd": 0,
            "width": "80px",
            "default": "",
            "description": __("Filter by Customer Name")
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
        }
	]
};
