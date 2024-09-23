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
		}
	]
}
