# Copyright (c) 2024, Ecosoft and contributors
# For license information, please see license.txt

import frappe
import json
from frappe import _, scrub


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
   
    return columns, data

def get_columns():
    columns = [
		{
            "label": _("Item ID"),
			"fieldname": "item_id",
			"fieldtype": "Data",
			"width": 200,
            "align": "left"
		},
        {
            "label": _("Item Name"),
			"fieldname": "item_name",
			"fieldtype": "Data",
			"width": 300,
            "align": "left"
		},
        {
            "label": _("Item ID (Mold)"),
			"fieldname": "item_molds_id",
			"fieldtype": "Data",
			"width": 200,
            "align": "left"
		},
		{
            "label": _("Mold ID"),
			"fieldname": "mold_id",
			"fieldtype": "Data",
			"width": 300,
            "align": "left"
		},
        {
            "label": _("Mold Name"),
			"fieldname": "mold_name",
			"fieldtype": "Data",
			"width": 200,
            "align": "left"
		}
	]
    return columns

def get_data(filters):
    report_data = []
    conditions = ""
    
	# Check if the item_code filter exists
    if filters.get("item"):
        if filters.get("type_item") == "Item":
            conditions += " AND ti.item_code = %(item)s"
        else: 
            conditions += " AND timd.item_code = %(item)s"
        
    query_report = frappe.db.sql(
		f"""SELECT ti.item_code
			, ti.item_name 
			, timd.item_code AS item_molds_id
			, timd.name AS molds_id
			, timd.item_name AS molds_name
			FROM `tabItem` ti 
			INNER JOIN `tabItem Molds Detail` timd ON ti.name = timd.parent 
            WHERE 1 = 1 {conditions}
		""".format(conditions=conditions), filters, as_dict=1)
    
    for qr in query_report:
        report_data.append({
            "item_id": qr.get('item_code', ""),
            "item_name": qr.get('item_name', ""),
            "item_molds_id": qr.get('item_molds_id', ""),
            "mold_id": qr.get('molds_id', ""),
            "mold_name": qr.get('molds_name', "")
		})
    return report_data