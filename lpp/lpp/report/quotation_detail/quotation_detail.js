// Copyright (c) 2024, Ecosoft and contributors
// For license information, please see license.txt

frappe.query_reports["Quotation Detail"] = {
    "filters": [
        {
            "fieldname": "year",
            "label": __("Year"),
            "fieldtype": "Select",
            "default": new Date().getFullYear(),  // Set default to current year
            "reqd": 1,  // This makes the field required
            "options": []
        },
        {
            "fieldname": "customer",
            "label": __("Customer"),
            "fieldtype": "Link",
            "options": "Customer",
            "reqd": 0 // Optional field
        },
        {
            "fieldname": "product",
            "label": __("Product"),
            "fieldtype": "Link",
            "options": "Item",
            "reqd": 0 // Optional field
        },
        {
            "fieldname": "marketing_status",
            "label": __("Marketing Status"),
            "fieldtype": "Select",
            "options": [
                " ",
                "Failed",
                "Waiting",
                "Followed Up",
                "Go Sample",
                "Go Mass"
            ],
            "reqd": 0 // Optional field
        },
    ],
    onload: function (report) {
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Quotation",
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
