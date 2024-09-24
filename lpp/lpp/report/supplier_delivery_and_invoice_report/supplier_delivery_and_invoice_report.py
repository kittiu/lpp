# Copyright (c) 2024, Ecosoft and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt

def execute(filters=None):
	columns = get_columns()
	data = []
	return columns, data

def get_columns():
	return [
		{
			"label": _("Supplyer Name"),
			"fieldname": "customer_name",
			"fieldtype": "Data",
			"width": 140,
            "align": "left"
		},
		{
			"label": _("Delivery Date"),
			"fieldname": "due_date",
			"fieldtype": "Date",
			"width": 140,
            "align": "left"
		},
		{
			"label": _("Vendor Invoice Number for Delivery"),
			"fieldname": "custom_supplier_purchase_order",
			"fieldtype": "Data",
			"width": 140,
            "align": "left"
		},
		{
			"label": _("Purchasing Document Number"),
			"fieldname": "",
			"fieldtype": "Data",
			"width": 140,
            "align": "left"
		},
		{
			"label": _("Inco terms"),
			"fieldname": "",
			"fieldtype": "Data",
			"width": 140,
            "align": "left"
		},
		{
			"label": _("Material Number"),
			"fieldname": "custom_material",
			"fieldtype": "Data",
			"width": 140,
            "align": "left"
		},
		{
			"label": _("Actual quantity delivered (in sale units)"),
			"fieldname": "actual_qty",
			"fieldtype": "Data",
			"width": 140,
            "align": "left"
		}
	]