// For license information, please see license.txt

frappe.query_reports["Annual Sale Report"] = {
    "filters": [
        {
            "fieldname": "type",
            "label": __("Type"),
            "fieldtype": "Select",
            "options": [
                "Quarter",
                "Monthly"
            ],
            "default": "Quarter",
            "reqd": 1
        },
        {
            "fieldname": "year",
            "label": __("Year"),
            "fieldtype": "Select",
            "options": [], // Options will be populated dynamically
            "reqd": 1 // This makes the year field required
        },
        {
            "fieldname": "customer_group",
            "label": __("Customer Group"),
            "fieldtype": "Link",
            "options": "Customer Group",
            "reqd": 0 // Optional field
        },
        {
            "fieldname": "customer",
            "label": __("Customer"),
            "fieldtype": "Link",
            "options": "Customer",
            "reqd": 0 // Optional field
        },
        {
            "fieldname": "item",
            "label": __("Item"),
            "fieldtype": "Link",
            "options": "Item",
            "reqd": 0 // Optional field
        }
    ],

    onload: function(report) {
        // Fetch distinct years from Sales Order transaction_date
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Sales Order",
                fields: ["distinct YEAR(transaction_date) as year"],
                order_by: "year desc",
                limit_page_length: 0
            },
            callback: function(r) {
                if (r.message) {
                    var years = [];
                    r.message.forEach(function(d) {
                        if (d.year) {
                            years.push(d.year.toString());
                        }
                    });
                    if (years.length > 0) {
                        // Set options for the "year" filter
                        var year_filter = report.get_filter("year");
                        year_filter.df.options = years.join("\n");
                        year_filter.refresh();
                        // Set default value to the latest year
                        year_filter.set_input(years[0]);
                    }
                }
            }
        });
    }
};
