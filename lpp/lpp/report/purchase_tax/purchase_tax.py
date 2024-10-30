# Copyright (c) 2024, Ecosoft and contributors
# For license information, please see license.txt

import frappe
import json
from frappe import _, scrub
from collections import defaultdict
from erpnext.accounts.report.purchase_register.purchase_register import execute as purchase_register_execute


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
   
    return columns, data

def get_columns():
    columns = [
        {
			"label": _("ลำดับ"),
			"fieldname": "no",
			"fieldtype": "Int",
			"width": 60,
		},
        {
			"label": _("วัน/เดือน/ปี ใบกำกับภาษี"),
			"fieldname": "posting_date",
			"fieldtype": "Data",
			"width": 180,
            "align": "left"
		},
        {
			"label": _("เลขที่ใบกำกับภาษี"),
			"fieldname": "voucher_no",
			"fieldtype": "Data",
			"width": 200,
		},
        {
			"label": _("ชื่อในรายงานภาษี"),
			"fieldname": "supplier_name",
			"fieldtype": "Data",
			"width": 400,
            "align": "left"
		},
        {
			"label": _("เลขประจำตัวผู้เสียภาษี"),
			"fieldname": "tax_id",
			"fieldtype": "Data",
			"width": 200,
            "align": "left"
		},
        {
			"label": _("สาขาสถานประกอบการ"),
			"fieldname": "address_line2",
			"fieldtype": "Data",
			"width": 200,
            "align": "left"
		},
        {
			"label": _("จำนวนเงิน"),
			"fieldname": "net_total",
			"fieldtype": "Float",
			"width": 160,
		},
        {
			"label": _("ภาษี"),
			"fieldname": "total_tax",
			"fieldtype": "Float",
			"width": 160,
		},
        {
			"label": _("ยอดรวม"),
			"fieldname": "grand_total",
			"fieldtype": "Float",
			"width": 160,
		}
	]
    return columns 

def get_data(filters):
    # Execute the purchase register report
    purchase_register_data = purchase_register_execute(filters)
    report_data = []
    target_data = []

    company_tax_id = get_company_tax_id(filters['company'])

    # Initialize row number
    row_number = 1

    if purchase_register_data and len(purchase_register_data) > 1:
        for dt in purchase_register_data[1]:
            # Get supplier's address_line2 from linked address
            address_line2 = get_customer_address_line2(dt.get('supplier_id', ''))
            
            # Append to report_data
            report_data.append({
                "posting_date": dt.get('posting_date', ''),
                "voucher_no": dt.get('voucher_no', ''),
                "supplier_name": dt.get('supplier_name', ''),
                "tax_id": dt.get('tax_id', ''),
                "address_line2": address_line2,
                "net_total": dt.get('net_total', 0.0),
                "total_tax": dt.get('total_tax', 0.0),
                "grand_total": dt.get('grand_total', 0.0),
                "company_tax_id": company_tax_id
            })
        
        # Group data by 'address_line2'
        grouped_data = defaultdict(list)
        for item in report_data:
            grouped_data[item['address_line2']].append(item)
		
		
        # Iterate through the grouped data and calculate group totals
        grand_total_net = 0
        grand_total_tax = 0
        grand_total_balance = 0
        for group, items in sorted(grouped_data.items()):
            group_total_net = 0
            group_total_tax = 0
            group_total_balance = 0

            
            
            # Add the summary row for the group
            target_data.append({
                "no": None,
                "posting_date": group,
                "voucher_no": None,
                "supplier_name": None,
                "tax_id": None,
                "address_line2": None,
                "net_total": None,
                "total_tax": None,
                "grand_total": None,
                "company_tax_id" : company_tax_id
            })
            
            # Add numbered items for each group
            for idx, item in enumerate(items, start=1):
                group_total_net += item['net_total']
                group_total_tax += item['total_tax']
                group_total_balance += item['grand_total']
                grand_total_net += item['net_total']
                grand_total_tax += item['total_tax']
                grand_total_balance += item['grand_total']
                target_data.append({
                    "no": idx,
                    "posting_date": item['posting_date'],
                    "voucher_no": item['voucher_no'],
                    "supplier_name": item['supplier_name'],
                    "tax_id": item['tax_id'],
                    "address_line2": item['address_line2'],
                    "net_total": item['net_total'],
                    "total_tax": item['total_tax'],
                    "grand_total": item['grand_total'],
                    "company_tax_id" : company_tax_id
                })

            # Add the group total row
            target_data.append({
                "no": None,
                "posting_date": None,
                "voucher_no": None,
                "supplier_name": "รวมยอดสาขา " + group,
                "tax_id": None,
                "address_line2": None,
                "net_total": group_total_net,
                "total_tax": group_total_tax,
                "grand_total": group_total_balance,
                "company_tax_id" : company_tax_id
            })
            
        target_data.append({
			"no": None,
			"posting_date": None,
			"voucher_no": None,
			"supplier_name": "รวมยอดทั้งสิ้น",
			"tax_id": None,
			"address_line2": None,
			"net_total": grand_total_net,
			"total_tax": grand_total_tax,
			"grand_total": grand_total_balance,
            "company_tax_id" : company_tax_id
		})

    return target_data

def get_customer_address_line2(customer_name):
    # Query for address_line2 in the Address linked to Customer
    address = frappe.get_all('Address', 
                            filters={
                                'link_doctype': 'Supplier',
                                'link_name': customer_name
                            }, 
                            fields=['address_line2'], 
                            limit=1)	

    # Check if the customer was found and has an address_line2
    if address:
        return address[0].get('address_line2', "-")
    else:
        return "-"
    
def get_company_tax_id(company_name):
    # Fetch the tax ID of the company
    tax_id = frappe.get_value('Company', company_name, 'tax_id')
    return tax_id