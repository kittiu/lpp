# Copyright (c) 2024, Ecosoft and contributors
# For license information, please see license.txt

import frappe
import json
from frappe import _, scrub
from collections import defaultdict


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
   
    return columns, data

def get_columns():
    columns = [
        {
			"label": _("PO NO."),
			"fieldname": "po_no",
			"fieldtype": "Data",
			"width": 200,
            "align": "left"
		},
        {
			"label": _("INV.NO."),
			"fieldname": "inv_no",
			"fieldtype": "Data",
			"width": 180,
            "align": "left"
		},
        {
			"label": _("DATE"),
			"fieldname": "date",
			"fieldtype": "Data",
			"width": 180,
		},
        {
			"label": _("PART"),
			"fieldname": "part",
			"fieldtype": "Data",
			"width": 300,
            "align": "left"
		},
        {
			"label": _("Total QTY"),
			"fieldname": "total_qty",
			"fieldtype": "Float",
			"width": 160,
		},
        {
			"label": _("QTY"),
			"fieldname": "qty",
			"fieldtype": "Float",
			"width": 160,
		},
        {
			"label": _("B/L"),
			"fieldname": "balance",
			"fieldtype": "Float",
			"width": 160,
		}
	]
    return columns 

def get_data(filters):
    report_data = []
    conditions = ""

    # Check if the purchase_order filter exists, and use the dynamic filter value
    if filters.get("purchase_order"):
        conditions += " AND pri.purchase_order = %(purchase_order)s"
        
	# Check if the invoice_number filter exists, and use the dynamic filter value
    if filters.get("invoice_number"):
        conditions += " AND pr.custom_supplier__invoice LIKE CONCAT('%%', %(invoice_number)s, '%%')"
        
    # Check if the posting_date filter exists, and use the dynamic filter value
    if filters.get("posting_date"):
        conditions += " AND pr.posting_date = %(posting_date)s"
        
	# Check if the item_name filter exists, and use the dynamic filter value
    if filters.get("item_name"):
        conditions += " AND pri.item_name LIKE CONCAT('%%', %(item_name)s, '%%')"
        

    # SQL Query to fetch data
    query_data = frappe.db.sql("""
        SELECT 
            pri.purchase_order,
            pr.custom_supplier__invoice AS supplier_invoice,
            pr.posting_date,
            pri.item_name AS part,
            pri.qty,
            po.total_qty
        FROM 
            `tabPurchase Receipt` pr
        LEFT JOIN 
            `tabPurchase Receipt Item` pri ON pr.name = pri.parent
        LEFT JOIN 
            `tabPurchase Order Item` poi ON pri.purchase_order = poi.parent 
            AND pri.item_code = poi.item_code
        LEFT JOIN 
            `tabPurchase Order` po ON poi.parent = po.name
        WHERE 
            pr.docstatus = 1 {conditions}
    """.format(conditions=conditions), filters, as_dict=1)
    
    # Initialize total_qty to track the total ordered quantity and balance
    check_po_no = None
    check_part = None
    total_qty = 0
    
    # Loop through the query results and append to the report_data
    for pd in query_data: 
        total_qty = pd['total_qty'] if pd['total_qty'] is not None else 0
        
        # Check if the purchase order or part has changed, reset total_qty if necessary
        if check_po_no != pd['purchase_order'] or check_part != pd['part']:
            check_po_no = pd['purchase_order']
            check_part = pd['part']
            total_qty = pd['total_qty'] if pd['total_qty'] is not None else 0
        elif check_po_no == pd['purchase_order'] and check_part == pd['part']:
            total_qty = balance if balance is not None else 0
        
        # Calculate the balance as the difference between total_qty and the current qty
        balance = total_qty - pd['qty']
        
        # Append each record to the report data
        report_data.append({
            "po_no": pd['purchase_order'],
            "inv_no": pd['supplier_invoice'] if pd['supplier_invoice'] else None,  # Invoice number can be dynamic now (based on row index)
            "date": pd['posting_date'],
            "part": pd['part'],
            "total_qty": pd['total_qty'],
            "qty": pd['qty'],
            "balance": balance if balance else 0
        })
        
    return report_data