// Copyright (c) 2024, Ecosoft and contributors
// For license information, please see license.txt

frappe.query_reports["Purchase Balance Report"] = {
	"filters": [
		{
			fieldname: "purchase_order",
			label: __("Purchase Order"),
			fieldtype: "Link",
			options: "Purchase Order",
		},
		{
            fieldname: "invoice_number",
            label: __("Invoice Number"),
            fieldtype: "Data",  // Assuming invoice number is a text field
            width: "80"
        },
		{
			fieldname: "posting_date",
			label: __("Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		},
		{
            fieldname: "item_name",
            label: __("Item Name"),
            fieldtype: "Data",  // Assuming item_name is a text field
            width: "80"
        }
	]
};
