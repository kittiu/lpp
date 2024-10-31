# Copyright (c) 2024, Ecosoft and contributors
# For license information, please see license.txt

import frappe
import json
from frappe import _, scrub
from datetime import date
from decimal import Decimal
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
            "fieldtype": "Float",
            "width": 160
            
        },
        {
            "label": _("STD Mat'l"),
            "fieldname": "std_use",
            "fieldtype": "Data",
            "width": 160,
            "align": "right"
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
    price_mat_value_array = []
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

            # Fetch Batch no. by item_id , material_id
            query_batch_no = frappe.db.sql(
                f"""SELECT two.production_item
                    , twoi.item_code AS material_id
                    , tsed.batch_no 
                    , tsed.qty 
                    FROM `tabWork Order` two 
                    INNER JOIN `tabWork Order Item` twoi ON two.name = twoi.parent 
                    INNER JOIN `tabStock Entry` tse ON two.name = tse.work_order 
                    INNER JOIN `tabStock Entry Detail` tsed ON tse.name = tsed.parent 
                    WHERE tse.posting_date BETWEEN %(from_date)s AND %(to_date)s
                    AND two.production_item = %(item_id)s
                    AND twoi.item_code = %(material_id)s
                    AND tsed.batch_no IS NOT NULL
                """, {
                    "from_date": from_date,
                    "to_date": to_date,
                    "item_id": qr['item_id'],
                    "material_id": qr['material_id']
                }, 
                as_dict=True
            )

            price_mat = 0
            sum_value_batch_no = 0
            number_batch_no = 0
            if query_batch_no:
                for qb in query_batch_no:
                    number_batch_no += 1
                    # Fetch stock ledger data for item
                    filter_stock_ledger_item = frappe._dict({
                        "company": filters.get("company", "Lamphun Plastpack"),
                        "from_date": from_date,
                        "to_date": to_date,
                        "item_code": qr['material_id'],
                        "batch_no": qb['batch_no']
                    })
                    stock_ledger_data = stock_ledger_execute(filter_stock_ledger_item)

                    incoming_rate = 0
                    if stock_ledger_data[1]:
                        for sld in stock_ledger_data[1]:
                            incoming_rate += sld.get("incoming_rate", 0)
                    sum_value_batch_no += (qb['qty']*incoming_rate)
            price_mat = sum_value_batch_no/number_batch_no if number_batch_no != 0 else 0
            price_mat_value_array.append(price_mat)

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
    json_total_price_mat = {
        "pack_out": None,
		"bom": None,
        "std_use": "PACK OUT"
	}

    # Add a mat used row with dynamic material fields
    json_mat_used = {
        "pack_out": None,
		"bom": None,
        "std_use": "MAT'L USED"
	}
    json_mat_used_price_mat = {
        "pack_out": None,
		"bom": None,
        "std_use": "ยอดเบิก"
	}

    # Add a wip value row with dynamic material fields
    json_wip_from_date = {
        "pack_out": None,
		"bom": None,
        "std_use": "WIP " + from_date
	}
    json_wip_to_date = {
        "pack_out": None,
		"bom": None,
        "std_use": "WIP " + to_date
	}
    json_wip_from_date_price_mat = {
        "pack_out": None,
		"bom": None,
        "std_use": "WIP " + from_date
	}
    json_wip_to_date_price_mat = {
        "pack_out": None,
		"bom": None,
        "std_use": "WIP " + to_date
	}

    # Add a total result row with dynamic material fields
    json_total_result = {
        "pack_out": None,
		"bom": None,
        "std_use": None
	}
    json_total_result_price_mat = {
        "pack_out": None,
		"bom": None,
        "std_use": "ยอดวัตถุดิบใช้ไป"
	}

    # Add a difference result row with dynamic material fields
    json_difference_result = {
        "pack_out": None,
		"bom": None,
        "std_use": None
	}
    json_difference_result_price_mat = {
        "pack_out": None,
		"bom": None,
        "std_use": "ผลต่าง"
	}

    # Add a difference group result row
    json_total_difference_group_result = {
        "pack_out": None,
		"bom": None,
        "std_use": None
	}

    # Add a json header result price material
    json_header_result_price_mat = {
        "pack_out": None,
		"bom": None,
        "std_use": "มูลค่าวัตถุดิบ (บาท)"
	}


	# Add dynamic material fields to json_total
    total_mat_used = 0
    total_wip_from_date = 0
    total_wip_to_date = 0
    total_result = 0
    total_result_material = 0
    total_difference_result = 0

    total_price_mat = 0
    total_mat_used_price_mat = 0
    total_wip_from_date_price_mat = 0
    total_wip_to_date_price_mat = 0
    total_result_price_mat = 0
    total_difference_result_price_mat = 0
    for i in range(len(material_array)):
        # Fetch stock balance data for material
        filter_stock_balance_material = frappe._dict({
            "company": filters.get("company", "Lamphun Plastpack"),
            "from_date": from_date,
            "to_date": to_date,
            "item_code": material_array[i],
            "warehouse": "Work in process - LPP"
        })
        stock_balance_data_material = stock_balance_execute(filter_stock_balance_material)
        
        # Calculate begin and end values for material
        begin_mat_value = sum(sb.get("opening_qty", 0) for sb in stock_balance_data_material[1]) if stock_balance_data_material and len(stock_balance_data_material) > 1 else 0
        end_mat_value = sum(sb.get("bal_qty", 0) for sb in stock_balance_data_material[1]) if stock_balance_data_material and len(stock_balance_data_material) > 1 else 0

        # Show Value on Json Result
        json_total[material_array[i]] = material_value_array[i]
        json_mat_used[material_array[i]] = mat_use_value_array[i]
        total_mat_used += mat_use_value_array[i]
        json_wip_from_date[material_array[i]] = begin_mat_value
        total_wip_from_date += begin_mat_value
        json_wip_to_date[material_array[i]] = end_mat_value
        total_wip_to_date += end_mat_value
        total_result_material = (mat_use_value_array[i] + begin_mat_value + end_mat_value)
        json_total_result[material_array[i]] = total_result_material
        total_result += total_result_material
        difference_result = (material_value_array[i] - total_result_material)
        json_difference_result[material_array[i]] = difference_result
        total_difference_result += difference_result
        json_total_difference_group_result[material_array[i]] = None

        # Show Value on Json Result Price Material
        price_mat_value = price_mat_value_array[i]
        json_header_result_price_mat[material_array[i]] = None
        json_total_price_mat[material_array[i]] = material_value_array[i]*price_mat_value
        total_price_mat += material_value_array[i]*price_mat_value
        json_mat_used_price_mat[material_array[i]] = mat_use_value_array[i]*price_mat_value
        total_mat_used_price_mat += mat_use_value_array[i]*price_mat_value
        json_wip_from_date_price_mat[material_array[i]] = begin_mat_value*price_mat_value
        total_wip_from_date_price_mat += begin_mat_value*price_mat_value
        json_wip_to_date_price_mat[material_array[i]] = end_mat_value*price_mat_value
        total_wip_to_date_price_mat += end_mat_value*price_mat_value
        json_total_result_price_mat[material_array[i]] = total_result_material*price_mat_value
        total_result_price_mat += total_result_material*price_mat_value
        json_difference_result_price_mat[material_array[i]] = difference_result*price_mat_value
        total_difference_result_price_mat += difference_result*price_mat_value
        

    # add column total summary by result
    json_mat_used['total'] = total_mat_used
    json_wip_from_date['total'] = total_wip_from_date
    json_wip_to_date['total'] = total_wip_to_date
    json_total_result['total'] = total_result
    json_difference_result['total'] = total_difference_result
    json_total_difference_group_result['total'] = total_difference_result/total_std_use

    json_total_price_mat['total'] = total_price_mat
    json_mat_used_price_mat['total'] = total_mat_used_price_mat
    json_wip_from_date_price_mat['total'] = total_wip_from_date_price_mat
    json_wip_to_date_price_mat['total'] = total_wip_to_date_price_mat
    json_total_result_price_mat['total'] = total_result_price_mat
    json_difference_result_price_mat['total'] = total_difference_result_price_mat

	# Append the total row to report data
    report_data.append(json_total)
    report_data.append(json_mat_used)
    report_data.append(json_wip_from_date)
    report_data.append(json_wip_to_date)
    report_data.append(json_total_result)
    report_data.append(json_difference_result)
    report_data.append(json_total_difference_group_result)
    report_data.append(json_header_result_price_mat)
    report_data.append(json_total_price_mat)
    report_data.append(json_mat_used_price_mat)
    report_data.append(json_wip_from_date_price_mat)
    report_data.append(json_wip_to_date_price_mat)
    report_data.append(json_total_result_price_mat)
    report_data.append(json_difference_result_price_mat)
    
    
    return columns, report_data
