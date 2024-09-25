# Copyright (c) 2024, Ecosoft and contributors
# For license information, please see license.txt

import frappe
import json
from frappe import _, scrub
from collections import defaultdict
from erpnext.accounts.report.sales_register.sales_register import execute as sales_register_execute

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
   
    return columns, data

def get_columns():
    columns = [
        {
			"label": _("ชื่อผู้ประกอบการ"),
			"fieldname": "company",
			"fieldtype": "Data",
			"width": 200,
		},
        {
			"label": _("เลขประจำตัวผู้เสียภาษี"),
			"fieldname": "company_tax_id",
			"fieldtype": "Data",
			"width": 200,
		},
        {
			"label": _("วัน เดือน ปี"),
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 140,
		},
		{
			"label": _("เลขที่ใบกำกับ"),
			"fieldname": "voucher_no",
			"fieldtype": "Data",
			"width": 200,
		},
        {
			"label": _("ชื่อในรายงานภาษี"),
			"fieldname": "customer_name",
			"fieldtype": "Data",
			"width": 200,
		},
        {
			"label": _("เลขที่ประจำตัวผู้เสียภาษี"),
			"fieldname": "tax_id",
			"fieldtype": "Data",
			"width": 180,
		},
        {
			"label": _("สาขา"),
			"fieldname": "address_line2",
			"fieldtype": "Data",
			"width": 160,
		},
        {
			"label": _("จำนวนเงินก่อนภาษี"),
			"fieldname": "net_total",
			"fieldtype": "Currency",
			"width": 140,
		},
        {
			"label": _("จำนวนภาษีมูลค่าเพิ่ม"),
			"fieldname": "tax_total",
			"fieldtype": "Currency",
			"width": 160,
		},
		{
			"label": _("ยอดรวม"),
			"fieldname": "grand_total",
			"fieldtype": "Currency",
			"width": 160,
		}
	]
    return columns

def get_data(filters):
    # try:
    sales_register_data = sales_register_execute(filters)
    report_data = []
    # target_data = []

    if sales_register_data:

        for dt in sales_register_data[1]:

            query_data = frappe.db.sql(
                f"""SELECT tsi.company ,tsi.company_tax_id ,ta.address_line2 ,tsi.name 
                from `tabSales Invoice` tsi
                inner join tabAddress ta on tsi.customer_address = ta.name 
				where tsi.name = '{dt["voucher_no"]}'
                GROUP BY tsi.name,tsi.company
                """,
                as_dict=True,
            )
            
        for dr in query_data:
            json_data = {
                "company" : dr['company'],
                "company_tax_id" : dr["company_tax_id"],
                "posting_date" : dt["posting_date"],
                "voucher_no" : dt['voucher_no'],
                "customer_name" : dt["customer_name"],
                "tax_id" : dt['tax_id'],
                "address_line2" : dr["address_line2"],
                "net_total" : dt["net_total"],
                "tax_total" : dt['tax_total'],
                "grand_total" : dt["grand_total"],
            }
            report_data.append(json_data)


    return report_data