# Copyright (c) 2024, Ecosoft and contributors
# For license information, please see license.txt

import frappe
import json
from frappe import _, scrub
from datetime import date
from erpnext.stock.report.stock_balance.stock_balance import execute as stock_balance_execute


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
			"width": 450,
            "align": "left"
		},
        {
            "label": _("UOM"),
			"fieldname": "uom",
			"fieldtype": "Data",
			"width": 100,
            "align": "left"
		},
		{
            "label": _("Material"),
			"fieldname": "material",
			"fieldtype": "Data",
			"width": 450,
            "align": "left"
		},
        {
            "label": _("BOM"),
			"fieldname": "bom",
			"fieldtype": "Float",
			"width": 160
		},
        {
            "label": _("PACK OUT"),
			"fieldname": "pack_out",
			"fieldtype": "Float",
			"width": 160
		},
		{
            "label": _("STD-USE"),
			"fieldname": "std_use",
			"fieldtype": "Float",
			"width": 160
		},
        {
            "label": _("WIP-ต้นงวด [FG(KGS.)]"),
			"fieldname": "wip_begin_fg",
			"fieldtype": "Float",
			"width": 200
		},
        {
            "label": _("WIP-ต้นงวด [MAT]"),
			"fieldname": "wip_begin_mat",
			"fieldtype": "Float",
			"width": 200
		},
        {
            "label": _("เบิก"),
			"fieldname": "withdraw",
			"fieldtype": "Float",
			"width": 160
		},
        {
            "label": _("คืน"),
			"fieldname": "return",
			"fieldtype": "Float",
			"width": 160
		},
		{
            "label": _("WIP-ปลายงวด [FG(KGS.)]"),
			"fieldname": "wip_end_fg",
			"fieldtype": "Float",
			"width": 200
		},
        {
            "label": _("WIP-ปลายงวด [MAT]"),
			"fieldname": "wip_end_mat",
			"fieldtype": "Float",
			"width": 200
		},
        {
            "label": _("ACT-USE"),
			"fieldname": "act_use",
			"fieldtype": "Float",
			"width": 160
		},
        {
            "label": _("VAR"),
			"fieldname": "var",
			"fieldtype": "Float",
			"width": 160
		},
        {
            "label": _("% VAR"),
			"fieldname": "percent_var",
			"fieldtype": "Float",
			"width": 160
		},
        {
            "label": _("ราคา MAT"),
			"fieldname": "price_mat",
			"fieldtype": "Float",
			"width": 160
		},
        {
            "label": _("ราคา VAR"),
			"fieldname": "price_var",
			"fieldtype": "Float",
			"width": 160
		}
	]
    return columns

def get_data(filters):
    report_data = []
    conditions = ""
    from_date = None
    to_date = None
    
	# Check if the item_code filter exists
    if filters.get("item"):
        if filters.get("type_item") == "Item":
            conditions += " AND two.production_item = %(item)s"
        else: 
            conditions += " AND twoi.item_code = %(item)s"
            
	# filter from_date , to_date
    if filters:
        from_date = filters['from_date']
        to_date = filters['to_date']
    else:
        from_date = date.today()
        to_date = date.today()
            
	# query data item by work_order
    query_report = frappe.db.sql(
		f"""SELECT two.production_item AS item_id 
			, two.item_name
			, two.custom_uom AS uom 
			, twoi.item_code AS material_id
			, twoi.item_name AS material
            , SUM(tbi.qty) AS bom
			, SUM(two.custom_ordered_quantity) AS pact_out
			FROM `tabWork Order` two 
			INNER JOIN `tabWork Order Item` twoi ON two.name = twoi.parent 
            LEFT JOIN `tabBOM` tb ON two.bom_no = tb.name 
			LEFT JOIN `tabBOM Item` tbi ON tb.name = tbi.parent 
			WHERE 1 = 1 {conditions}
			GROUP BY two.production_item
			, two.item_name
			, two.custom_uom 
            , twoi.item_code
			, twoi.item_name
			ORDER BY twoi.item_name , two.production_item
		""".format(conditions=conditions), filters, as_dict=1)
    
    for qr in query_report:
        # Fetch stock balance data for item
        filter_stock_balance_item = frappe._dict({
            "company": filters.get("company", "Lamphun Plastpack"),
            "from_date": from_date,
            "to_date": to_date,
            "item_code": qr['item_id'],
            "warehouse": "Work in process - LPP"
        })
        stock_balance_data_item = stock_balance_execute(filter_stock_balance_item)
        
		# Calculate begin and end values for the item
        begin_fg_value = sum(sb.get("opening_qty", 0) for sb in stock_balance_data_item[1]) if stock_balance_data_item and len(stock_balance_data_item) > 1 else 0
        end_fg_value = sum(sb.get("bal_qty", 0) for sb in stock_balance_data_item[1]) if stock_balance_data_item and len(stock_balance_data_item) > 1 else 0

        # Fetch stock balance data for material
        filter_stock_balance_material = frappe._dict({
            "company": filters.get("company", "Lamphun Plastpack"),
            "from_date": from_date,
            "to_date": to_date,
            "item_code": qr['material_id'],
            "warehouse": "Work in process - LPP"
        })
        stock_balance_data_material = stock_balance_execute(filter_stock_balance_material)
        
		# Calculate begin and end values for material
        begin_mat_value = sum(sb.get("opening_qty", 0) for sb in stock_balance_data_material[1]) if stock_balance_data_material and len(stock_balance_data_material) > 1 else 0
        end_mat_value = sum(sb.get("bal_qty", 0) for sb in stock_balance_data_material[1]) if stock_balance_data_material and len(stock_balance_data_material) > 1 else 0

        # Fetch withdrawal and return values by Stock Entry
        query_withdraw_return = frappe.db.sql(
            f"""
            SELECT SUM(rs.qty) AS sum_qty, SUM(rs.return_qty) AS sum_return_qty
            FROM (
                SELECT 
                    tse.name,
                    tse.work_order,
                    tsed.s_warehouse,
                    tsed.t_warehouse,
                    tsed.qty,
                    CASE 
                        WHEN tsed.s_warehouse = 'Work in process - LPP' AND tsed.t_warehouse != 'Work in process - LPP' 
                        THEN tsed.qty 
                        ELSE 0 
                    END AS return_qty
                FROM `tabStock Entry` tse
                INNER JOIN `tabStock Entry Detail` tsed ON tse.name = tsed.parent 
                INNER JOIN `tabWork Order` two ON tse.work_order = two.name 
                INNER JOIN `tabWork Order Item` twoi ON two.name = twoi.parent 
                WHERE tse.stock_entry_type = 'Material Transfer for Manufacture'
                AND tse.posting_date BETWEEN %(from_date)s AND %(to_date)s
                AND two.production_item = %(item_id)s
                AND twoi.item_code = %(material_id)s
            ) rs
            """, {
                "from_date": from_date,
                "to_date": to_date,
                "item_id": qr['item_id'],
                "material_id": qr['material_id']
            }, 
            as_dict=True
        )
        
        # Get withdrawal and return values
        withdraw_value = query_withdraw_return[0].get('sum_qty', 0) if query_withdraw_return else 0
        return_value = query_withdraw_return[0].get('sum_return_qty', 0) if query_withdraw_return else 0

        # Append report data
        report_data.append({
            "item_id": qr.get('item_id', ""),
            "item_name": qr.get('item_name', ""),
            "uom": qr.get('uom', ""),
            "material": qr.get('material', ""),
            "bom": qr.get('bom', 0),
            "pack_out": qr.get('pack_out', 0),
            "std_use": qr.get('bom', 0) * qr.get('pack_out', 0),
            "wip_begin_fg": begin_fg_value,
            "wip_begin_mat": begin_mat_value,
            "withdraw": withdraw_value,
            "return": return_value,
            "wip_end_fg": end_fg_value,
            "wip_end_mat": end_mat_value,
            "act_use": None,
            "var": None,
            "percent_var": None,
            "price_mat": None,
            "price_var": None
        })

    return report_data
