frappe.query_reports["Production and machine report"] = {
	"filters": [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			width: "80",
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		},
		{
            fieldname: "workstation_type",
            label: __("Workstation Type"),
            fieldtype: "Link",
            options: "Workstation Type",
            reqd: 1,
			on_change: function () {
				frappe.query_report.set_filter_value("workstation", "");
				console.log("on_change workstation_type")
			},
        },
        {
            fieldname: "workstation",
            label: __("Workstation"),
            fieldtype: "MultiSelectList",
			get_data: function (txt) {
				return frappe.db.get_link_options("Workstation", txt, {
					workstation_type: frappe.query_report.get_filter_value("workstation_type"),
				});
			},
        }
	]
};

