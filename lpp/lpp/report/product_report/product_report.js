// Copyright (c) 2024, Ecosoft and contributors
// For license information, please see license.txt

frappe.query_reports["Product Report"] = {
    "filters": [
        {
            "fieldname": "type",
            "label": __("Item Group"),
            "fieldtype": "Select",
            "options": [
                "Tray & Reel",
                "Tape & Protective Band"
            ],
            "default": "Tray & Reel",
            "reqd": 1
        },
        {
            "fieldname": "start_date",
            "label": __("Start Date"),
            "fieldtype": "Date",
            // "reqd": 1,  // ทำให้จำเป็นต้องเลือก
            "default": frappe.datetime.nowdate(),
            "description": "Start Date for custom_start_date_production"
        },
        {
            "fieldname": "end_date",
            "label": __("End Date"),
            "fieldtype": "Date",
            // "reqd": 1,  // ทำให้จำเป็นต้องเลือก
            "default": frappe.datetime.nowdate(),
            "description": "End Date for custom_end_date_production"
        },
        {
            "fieldname": "workstation",
            "label": __("Workstation"),
            "fieldtype": "Link",
            "options": "Workstation",  // ดึงข้อมูลจาก Doctype Workstation
            "description": "Select Workstation"
        },
        {
            "fieldname": "work_order",
            "label": __("Work Order"),
            "fieldtype": "Link",
            "options": "Work Order",  // ดึงข้อมูลจาก Doctype Work Order
            "description": "Select Work Order"
        },
        {
            "fieldname": "custom_shift",
            "label": __("Shift"),
            "fieldtype": "Link",
            "options": "Shift",
            "description": "Select Shift"
        },
        {
            "fieldname": "production_item",
            "label": __("Product ID"),
            "fieldtype": "Link",
            "options": "Item",  // ดึงข้อมูลจากฟิลด์ production_item
            "description": "Select Product ID"
        },
        {
            "fieldname": "production_name",
            "label": __("Production Name"),
            "fieldtype": "Select",
            "options": [], // ตั้งค่าเริ่มต้นเป็นค่าว่าง
        }
    ],

    onload: function(report) {
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Job Card",
                fields: ["distinct custom_production_item_name"],
                // distinct: true,
                order_by: "custom_production_item_name"
            },
            callback: function(response) {
                if (response.message) {
                    let options = [""]; // เพิ่มช่องว่างเป็นตัวเลือกแรก
                    response.message.forEach(function(item) {
                        options.push(item.custom_production_item_name);
                    });
                    if (options.length > 0) {
                        let options_filter = report.get_filter("production_name");
                        options_filter.df.options = options.join("\n");
                        options_filter.refresh();
                        // Set default value to the latest year
                        options_filter.set_input(options[0]);
                    }
                }
            }
        });
    }
};

