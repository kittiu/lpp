# Copyright (c) 2024, Ecosoft and contributors
# For license information, please see license.txt

import frappe
import json
from datetime import date
from frappe import _, scrub
from collections import defaultdict
from erpnext.selling.report.sales_analytics.sales_analytics import execute as sales_analytics_execute


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	
	return columns, data

def get_columns():
	columns = [
        {
			"label": _("Code"),
			"fieldname": "entity",
			"fieldtype": "Data",
			"width": 140,
		},
        {
			"label": _("Customer Name"),
			"fieldname": "entity_name",
			"fieldtype": "Data",
			"width": 400,
			"align": "left"
		},
        {
			"label": _("DISC."),
			"fieldname": "disc",
			"fieldtype": "Float",
			"width": 160,
		},
		{
			"label": _("DEPOSIT"),
			"fieldname": "deposit",
			"fieldtype": "Float",
			"width": 160,
		},
		{
			"label": _("Before VAT"),
			"fieldname": "before_vat",
			"fieldtype": "Float",
			"width": 160,
		},
		{
			"label": _("VAT"),
			"fieldname": "vat",
			"fieldtype": "Float",
			"width": 160,
		},
		{
			"label": _("NET Amt"),
			"fieldname": "net_amt",
			"fieldtype": "Float",
			"width": 160,
		}
	]
	
	return columns

def get_data(filters):
	sales_analytics_data = sales_analytics_execute(filters)
	report_data = []
	target_data = []
	grand_total_amount = 0
	grand_total_tax_amount = 0
	result_grand_total = 0

	from_date = filters.get('from_date', date.today())
	to_date = filters.get('to_date', date.today())

	if sales_analytics_data and len(sales_analytics_data) > 1:
		for dt in sales_analytics_data[1]:
			query_data = frappe.db.sql(
                f"""
                SELECT 
                    tc.name, 
                    tc.customer_group,
                    COALESCE(SUM(tsoi.amount), 0) AS sum_amount,
                    COALESCE(SUM(tstac.tax_amount), 0) AS sum_tax_amount,
                    COALESCE(SUM(tso.grand_total), 0) AS sum_grand_total
                FROM 
                    `tabCustomer` tc
                LEFT JOIN 
                    `tabSales Order` tso ON tc.name = tso.customer  
                LEFT JOIN 
                    `tabSales Order Item` tsoi ON tso.name = tsoi.parent 
                LEFT JOIN 
                    `tabSales Taxes and Charges` tstac ON tso.name = tstac.parent 
                WHERE 
                    tc.name = %s
                    AND tso.docstatus = 1
                    AND tso.transaction_date BETWEEN %s AND %s
                """,
                (dt["entity"], from_date, to_date),
                as_dict=True,
            )

			for qr in query_data:
				json_data = {
					"group": qr['customer_group'] or '',
					"entity": dt["entity"],
					"entity_name": dt["entity_name"],
					"disc": 0,
					"deposit": 0,
					"before_vat": qr.get('sum_amount', 0) or 0,
					"vat": qr.get('sum_tax_amount', 0) or 0,
					"net_amt": qr.get('sum_grand_total', 0) or 0
				}

				grand_total_amount += qr.get('sum_amount', 0) or 0
				grand_total_tax_amount += qr.get('sum_tax_amount', 0) or 0
				result_grand_total += qr.get('sum_grand_total', 0) or 0

				report_data.append(json_data)

		grouped_data = defaultdict(list)
		for item in report_data:
			grouped_data[item['group']].append(item)

		for group, items in sorted(grouped_data.items()):
			group_total_before_vat = 0
			group_total_vat = 0
			group_total_net_amt = 0

			# Add group header
			target_data.append({
				"entity": group,
				"entity_name": "",
				"disc": None,
				"deposit": None,
				"before_vat": None,
				"vat": None,
				"net_amt": None
			})

			# Add each item and accumulate group totals
			for item in items:
				group_total_before_vat += item.get('before_vat', 0)
				group_total_vat += item.get('vat', 0)
				group_total_net_amt += item.get('net_amt', 0)
				target_data.append({
					"entity": item['entity'],
					"entity_name": item['entity_name'],
					"disc": 0,
					"deposit": 0,
					"before_vat": item.get('before_vat', 0),
					"vat": item.get('vat', 0),
					"net_amt": item.get('net_amt', 0)
				})

			# Add group total row
			target_data.append({
				"entity": "GROUP TOTAL",
				"entity_name": "",
				"disc": 0,
				"deposit": 0,
				"before_vat": group_total_before_vat,
				"vat": group_total_vat,
				"net_amt": group_total_net_amt
			})

		# Add grand total row
		target_data.append({
			"entity": "GRAND TOTAL",
			"entity_name": "",
			"disc": 0,
			"deposit": 0,
			"before_vat": grand_total_amount,
			"vat": grand_total_tax_amount,
			"net_amt": result_grand_total
		})

	return target_data
