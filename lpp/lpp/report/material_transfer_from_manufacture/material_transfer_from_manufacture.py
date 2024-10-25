# Copyright (c) 2024, Ecosoft and contributors
# For license information, please see license.txt

import frappe
from frappe import _, scrub


def execute(filters=None):
	columns = get_column()
	data = get_data(filters)
	return columns, data

def get_column():
	columns = [
		{
			"label": _("รายการคลังสินค้า (Stock Entry)"),
			"fieldname": "stock_entry",
			"fieldtype": "Data",
			"width": 180,
            "align": "left"
		},
		{
			"label": _("Already Printed"),
			"fieldname": "already_printed",
			"fieldtype": "Data",
			"width": 180,
            "align": "left"
		},
		{
			"label": _("รหัสสินค้า (Item Code)"),
			"fieldname": "item_code",
			"fieldtype": "Data",
			"width": 180,
            "align": "left"
		},
		{
			"label": _("ชื่อรายการ (Item Name)"),
			"fieldname": "item_name",
			"fieldtype": "Data",
			"width": 450,
            "align": "left"
		},
		{
			"label": _("Work Order"),
			"fieldname": "work_order",
			"fieldtype": "Data",
			"width": 220,
            "align": "left"
		},
		{
			"label": _("Production Batch No."),
			"fieldname": "lot_no",
			"fieldtype": "Data",
			"width": 300,
            "align": "left"
		},
		{
			"label": _("จำนวนต่อ Pack"),
			"fieldname": "quantity_per_pack",
			"fieldtype": "Data",
			"width": 160,
			"align": "right"
		},
		{
			"label": _("จำนวนต่อ Box"),
			"fieldname": "quantity_per_box",
			"fieldtype": "Data",
			"width": 160,
			"align": "right"
		},
		{
			"label": _("จำนวนรวม Quantity"),
			"fieldname": "sum_quantity",
			"fieldtype": "Float",
			"width": 160,
		},
		{
			"label": _("แผนก (Department)"),
			"fieldname": "department",
			"fieldtype": "Data",
			"width": 180,
            "align": "left"
		},
		{
			"label": _("กะ (Shift)"),
			"fieldname": "shift",
			"fieldtype": "Data",
			"width": 180,
            "align": "left"
		},
	]

	return columns

def get_data(filters):
	report_data = []

	# if filters:
	# 	department = filters['department']
	# 	shift_type = filters['shift_type']
	# Map "True" to 1 and "False" to 0
	already_printed = 1 if filters.get('already_printed') == 'True' else 0

	query = """
		SELECT sed.item_code, sed.item_name, se.work_order, sed.batch_no as lot_no,
			sed.qty, se.custom_department, se.custom_shift,
			ti.custom_unit__pack, ti.custom_unit__box,
			se.name as stock_entry_name, 
			CASE 
				WHEN se.custom_already_printed = 1 THEN 'True'
				ELSE 'False'
			END as custom_already_printed
		FROM `tabStock Entry Detail` sed
		INNER JOIN `tabStock Entry` se ON sed.parent = se.name
		LEFT JOIN `tabItem` ti ON sed.item_code = ti.name 
		WHERE se.docstatus = 0
		AND se.purpose = 'Manufacture'
	"""

	
	conditions = []
	if filters.get("department"):
		conditions.append(f"se.custom_department = '{filters['department']}'")
	if filters.get("shift_type"):
		conditions.append(f"se.custom_shift = '{filters['shift_type']}'")
	# Add filter for stock_entry_id using WHERE IN
	if filters.get("stock_entry_id"):
		# Convert the list of stock_entry_id into a SQL-compatible string
		stock_entry_ids = ", ".join(f"'{id}'" for id in filters["stock_entry_id"])
		conditions.append(f"se.name IN ({stock_entry_ids})")
	# Apply the already_printed condition
	if filters.get("already_printed"):
		conditions.append(f"se.custom_already_printed = {already_printed}")

	if conditions:
		query += " AND " + " AND ".join(conditions)

    # Execute the query with optional filtering
	stock_entries = frappe.db.sql(query, as_dict=1)
	

    # Append each stock entry record to the data list
	for idx, entry in enumerate(stock_entries, start=1):
		report_data.append({
			"no": idx,
			"already_printed": entry.custom_already_printed,
			"stock_entry": entry.stock_entry_name,
            "item_code": entry.item_code,
            "item_name": entry.item_name,
            "work_order": entry.work_order,
            "lot_no": entry.lot_no if entry.lot_no else "-",
			"quantity_per_pack": entry.custom_unit__pack if entry.custom_unit__pack else "-",
			"quantity_per_box": entry.custom_unit__box if entry.custom_unit__box else "-",
			"sum_quantity": entry.qty,
			"department": entry.custom_department if entry.custom_department else "-",
			"shift": entry.custom_shift if entry.custom_shift else "-"
        })

	return report_data