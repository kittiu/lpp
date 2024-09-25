frappe.query_reports["Purchase Invoice VAT and Shipping Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.nowdate(), -1)  // Default to one month ago
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.nowdate()  // Default to today
		},
		{
			"fieldname": "invoice_no",
			"label": __("Invoice No./Tax Invoice No."),
			"fieldtype": "Link",
			"options": "Purchase Invoice"  // Link to the Purchase Invoice doctype
		},
		{
			"fieldname": "item_code",
			"label": __("Item Code"),
			"fieldtype": "Link",
			"options": "Item"  // Link to the Item doctype
		},
		{
			"fieldname": "end_date",
			"label": __("End Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.nowdate()  // Default to today
		}
	]
};
