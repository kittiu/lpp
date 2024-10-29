# Copyright (c) 2024, Ecosoft and contributors
# For license information, please see license.txt

import frappe
import json
from frappe import _, scrub
from datetime import date
from erpnext.stock.report.stock_balance.stock_balance import execute as stock_balance_execute
from erpnext.stock.report.stock_ledger.stock_ledger import execute as stock_ledger_execute


def execute(filters=None):
    # columns = get_columns()
    columns , data = get_data(filters)
   
    return columns, data

def get_data(filters):
    report_data = []
    conditions = ""
    from_date = None
    to_date = None
    
	# Define fixed columns
    columns = [
        {
            "label": _("รหัสสินค้า"),
            "fieldname": "item_id",
            "fieldtype": "Data",
            "width": 200,
            "align": "left"
        },
        {
            "label": _("ชื่อสินค้า"),
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
            "label": _("PACK OUT"),
            "fieldname": "pack_out",
            "fieldtype": "Float",
            "width": 160
        },
        {
            "label": _("BOM"),
            "fieldname": "bom",
            "fieldtype": "Data",
            "width": 160,
            "align": "right"
        },
        {
            "label": _("STD Mat'l"),
            "fieldname": "std_use",
            "fieldtype": "Float",
            "width": 160
        }
    ]
    
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
        
	# filter by item_color on like item_name
    if filters.get("item_color"):
        conditions += " AND two.item_name LIKE CONCAT('%%', %(item_color)s, '%%')"
        
	# query data item by work_order
    query_report = frappe.db.sql(
		f"""SELECT two.production_item AS item_id 
			, two.item_name
			, two.custom_uom AS uom 
			, twoi.item_code AS material_id
			, twoi.item_name AS material
			, SUM(tbi.qty) AS bom
			, SUM(two.custom_ordered_quantity) AS pack_out
            , SUM(twoi.required_qty) AS mat_use
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
    
	# Process and append report data
    total_pack_out = 0
    total_std_use = 0
    material_array = []
    material_value_array = []
    mat_use_value_array = []
    for qr in query_report:
        std_use = qr.get('bom', 0) * qr.get('pack_out', 0)
        total_pack_out += qr.get('pack_out', 0)
        total_std_use += std_use

        report_data.append({
            "item_id": qr.get('item_id', ""),
            "item_name": qr.get('item_name', ""),
            "uom": qr.get('uom', ""),
            "pack_out": qr.get('pack_out', 0),
            "bom": qr.get('bom', 0),
            "std_use": std_use,
            qr['material_id']: std_use,
            "total": std_use
        })
        
        # Check if material_id is duplicated
        is_duplicate = material_array.count(qr['material_id']) > 0
        
        if not is_duplicate:
            columns.append({
                "label": qr['material'],
                "fieldname": qr['material_id'],
                "fieldtype": "Float",
                "width": 350
            })
            material_array.append(qr['material_id'])
            material_value_array.append(std_use)
            mat_use_value_array.append(qr.get('mat_use', 0))
        else:
            # Sum Total By Material ID
            position_material_id = material_array.index(qr['material_id'])
            material_value_array[position_material_id] += std_use
            mat_use_value_array[position_material_id] += qr.get('mat_use', 0)

    columns.append({
        "label": _("Total"),
        "fieldname": "total",
        "fieldtype": "Float",
        "width": 160
    })

    # Add a total row with dynamic material fields
    json_total = {
		"item_id": None,
		"item_name": "Total",
		"uom": None,
		"pack_out": total_pack_out,
		"bom": None,
		"std_use": total_std_use,
        "total": total_std_use
	}

    # Add a mat used row with dynamic material fields
    json_mat_used = {
        "pack_out": None,
		"bom": "MAT'L USED",
        "std_use": None
	}

    # # Fetch stock balance data for material
    # filter_stock_balance_material = frappe._dict({
    #     "company": filters.get("company", "Lamphun Plastpack"),
    #     "from_date": from_date,
    #     "to_date": to_date,
    #     "item_code": qr['material_id'],
    #     "warehouse": "Work in process - LPP"
    # })
    # stock_balance_data_material = stock_balance_execute(filter_stock_balance_material)
    
    # # Calculate begin and end values for material
    # begin_mat_value = sum(sb.get("opening_qty", 0) for sb in stock_balance_data_material[1]) if stock_balance_data_material and len(stock_balance_data_material) > 1 else 0
    # end_mat_value = sum(sb.get("bal_qty", 0) for sb in stock_balance_data_material[1]) if stock_balance_data_material and len(stock_balance_data_material) > 1 else 0

    # Add a wip value row with dynamic material fields
    json_wip_from_date = {
        "pack_out": None,
		"bom": "WIP " + from_date,
        "std_use": None
	}
    json_wip_to_date = {
        "pack_out": None,
		"bom": "WIP " + to_date,
        "std_use": None
	}

	# Add dynamic material fields to json_total
    for i in range(len(material_array)):
        json_total[material_array[i]] = material_value_array[i]
        json_mat_used[material_array[i]] = mat_use_value_array[i]

	# Append the total row to report data
    report_data.append(json_total)
    report_data.append(json_mat_used)
    report_data.append(json_wip_from_date)
    report_data.append(json_wip_to_date)

    
    return columns, report_data
