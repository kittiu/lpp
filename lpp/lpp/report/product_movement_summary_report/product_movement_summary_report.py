# Copyright (c) 2024, Ecosoft and contributors
# For license information, please see license.txt

import frappe
import json
from frappe import _, scrub
from collections import defaultdict
from erpnext.stock.report.stock_balance.stock_balance import execute as stock_balance_execute


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
   
    return columns, data

def get_columns():
    columns = [
        {
			"label": _("Item Code"),
			"fieldname": "item_code",
			"fieldtype": "Data",
			"width": 180,
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
			"label": _("Bring Forward"),
			"fieldname": "bring_forward",
			"fieldtype": "Float",
			"width": 160,
		},
		{
			"label": _("Receive"),
			"fieldname": "receive",
			"fieldtype": "Float",
			"width": 160,
		},
        {
			"label": _("Price"),
			"fieldname": "price",
			"fieldtype": "Float",
			"width": 160,
		},
        {
			"label": _("Total"),
			"fieldname": "total_receipt",
			"fieldtype": "Float",
			"width": 160,
		},
        {
			"label": _("Issue"),
			"fieldname": "issue",
			"fieldtype": "Float",
			"width": 160,
		},
		{
			"label": _("Cost"),
			"fieldname": "cost",
			"fieldtype": "Float",
			"width": 160,
		},
        {
			"label": _("Total"),
			"fieldname": "total_stock_entry_type",
			"fieldtype": "Float",
			"width": 160,
		},
        {
			"label": _("Brought Forward"),
			"fieldname": "brought_forward",
			"fieldtype": "Float",
			"width": 160,
		},
        
	]
    return columns

def get_data(filters):
    report_data = []
    conditions = ""
    conditions_date_purchase = ""
    conditions_date_stock = ""  
    
	# Check if the item_code filter exists
    if filters.get("item_group"):
        conditions += " AND ti.item_group = %(item_group)s"
        
	# Check if the item_code filter exists
    if filters.get("item_code"):
        conditions += " AND ti.item_code = %(item_code)s"
        
    # Filter by start date range
    if filters.get("from_date"):
        conditions_date_purchase += " AND pr.posting_date >= %(from_date)s"
        conditions_date_stock += "  AND se.posting_date >= %(from_date)s"
        
	# Filter by end date range
    if filters.get("to_date"):
        conditions_date_purchase += " AND pr.posting_date <= %(to_date)s"
        conditions_date_stock += "  AND se.posting_date <= %(to_date)s"
    
	# SQL Query to fetch data
    query_data = frappe.db.sql("""
		SELECT ti.item_group 
		, ti.item_code , ti.item_name 
        , SUM(tpri.qty) AS qty
		, SUM(tpri.base_rate) AS base_rate
        , se.stock_entry_type 
		, SUM(tsed.qty) AS stock_qty
		, SUM(tsed.basic_rate) AS stock_rate
		FROM `tabItem` ti 
		LEFT JOIN `tabPurchase Receipt Item` tpri ON ti.item_code = tpri.item_code 
		LEFT JOIN `tabPurchase Receipt` pr ON pr.name = tpri.parent {conditions_date_purchase}
        LEFT JOIN `tabStock Entry Detail` tsed ON ti.item_code = tsed.item_code 
		LEFT JOIN `tabStock Entry` se ON se.name = tsed.parent {conditions_date_stock}
		AND se.stock_entry_type IN ('Material Issue','Material Transfer','Material Transfer for Manufacture','Manufacture')
		WHERE pr.docstatus = 1 {conditions}
    	GROUP BY ti.item_group 
		, ti.item_code , ti.item_name
    """.format(conditions=conditions, conditions_date_purchase=conditions_date_purchase, conditions_date_stock=conditions_date_stock), filters, as_dict=1)
    
	# Prepare data for the report
    for qd in query_data:
        qty = qd['qty'] if qd['qty'] else 0
        base_rate = qd['base_rate'] if qd['base_rate'] else 0.0
        stock_qty = qd['stock_qty'] if qd['stock_qty'] else 0
        stock_rate = qd['stock_rate'] if qd['stock_rate'] else 0
        
        filter_report = frappe._dict({
            "company": filters.get("company", "Lamphun Plastpack"),  # ค่าเริ่มต้นหากไม่มี
            "from_date": filters.get("from_date"),
            "to_date": filters.get("to_date"),
            "item_code": qd['item_code']
        })
        
        stock_balance_data = stock_balance_execute(filter_report)
        
        # คำนวณค่า bring_forward และ brought_forward
        bring_forward_value = 0
        brought_forward_value = 0

        if stock_balance_data and len(stock_balance_data) > 1:
            for sb in stock_balance_data[1]:
                bring_forward_value += sb.get("opening_qty", 0)
                brought_forward_value += sb.get("bal_qty", 0)

		# เพิ่มข้อมูลลงใน report_data
        report_data.append({
            "item_code": qd['item_code'],
            "item_name": qd['item_name'],
            "bring_forward": bring_forward_value,
            "item_group": qd['item_group'],
            "receive": qty,
            "price": base_rate,
            "total_receipt": qty * base_rate,
            "issue": stock_qty,
            "cost": stock_rate,
            "total_stock_entry_type": stock_qty * stock_rate,
            "brought_forward": brought_forward_value
        })
    
    return report_data