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
        // {
        //     "fieldname": "custom_production_item_name",
        //     "label": __("Product Name"),
        //     "fieldtype": "Link",
        //     "options": "Item",  // ดึงข้อมูลจากฟิลด์ custom_production_item_name
        //     "description": "Select Product Name"
        // }
    ]
};

