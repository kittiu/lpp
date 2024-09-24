frappe.query_reports["Production Delivery Request Report"] = {
    "filters": [
        {
            "fieldname": "stock_entry_type",
            "label": __("Stock Entry Type"),
            "fieldtype": "Select",
            "options": "\nManufacture\nMaterial Transfer\nMaterial Issue\nMaterial Receipt",
            "default": "Manufacture",
            // "reqd": 1
        },
        {
            "fieldname": "docstatus",
            "label": __("Docstatus"),
            "fieldtype": "Select",
            "options": [
                {},
                { "label": __("Draft"), "value": "0" },
                { "label": __("Submitted"), "value": "1" },
                { "label": __("Cancelled"), "value": "2" }
            ],
            "default": "1",  // Default to Submitted (docstatus = 1)
            // "reqd": 1
        },
        {
            "fieldname": "custom_employee_name",
            "label": __("Employee"),
            "fieldtype": "Link",
            "options": "Employee",  // Specifies the target doctype
            "placeholder": __("Select Employee"),
            "description": __("Filter by the employee associated with the Stock Entry."),
            "reqd": 0  // Set to 1 if you want to make it a mandatory filter
        },
        {
            "fieldname": "from_posting_date",
            "label": __("From Posting Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.month_start(),
            "description": __("Filter Stock Entries from this date."),
            // "reqd": 0  // Set to 1 if you want to make it a mandatory filter
        },
        {
            "fieldname": "to_posting_date",
            "label": __("To Posting Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.month_end(),
            "description": __("Filter Stock Entries up to this date."),
            // "reqd": 0  // Set to 1 if you want to make it a mandatory filter
        }
    ]
}
