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
	grand_total_amount = 0
	grand_total_tax_amount = 0
	result_grand_total = 0
	from_date = None
	to_date = None

	if sales_analytics_data: 

		if filters:
			from_date = filters['from_date']
			to_date = filters['to_date']
		else: 
			# Get the current date
			from_date = date.today()
			to_date = date.today()

		for dt in sales_analytics_data[1]:
			query_data = frappe.db.sql(
                f"""SELECT tc.name
					, SUM(tsoi.amount) AS sum_amount
					, SUM(tstac.tax_amount) AS sum_tax_amount
					, SUM(tso.grand_total) AS sum_grand_total
					FROM `tabCustomer`  tc
					LEFT JOIN `tabSales Order` tso ON tc.name = tso.customer  
					LEFT JOIN `tabSales Order Item` tsoi ON tso.name = tsoi.parent 
					LEFT JOIN `tabSales Taxes and Charges` tstac ON tso.name = tstac.parent 
					WHERE tc.name = '{dt["entity"]}'
					AND tso.docstatus = 1
					AND tso.transaction_date BETWEEN '{from_date}' AND '{to_date}'
                    """,
                as_dict=True,
            )

			for qr in query_data:
				json_data = {
					"entity" : dt["entity"],
					"entity_name" : dt["entity_name"],
					"disc" : 0,
					"deposit" : 0,
					"before_vat" : qr['sum_amount'],
					"vat" : qr['sum_tax_amount'],
					"net_amt" : qr['sum_grand_total']
				}

				grand_total_amount += qr['sum_amount']
				grand_total_tax_amount += qr['sum_tax_amount']
				result_grand_total += qr['sum_grand_total']
				report_data.append(json_data)

		# grand total
		report_data.append({
			"entity" : "GRAND TOTAL",
			"entity_name" : "",
			"disc" : 0,
			"deposit" : 0,
			"before_vat" : grand_total_amount,
			"vat" : grand_total_tax_amount,
			"net_amt" : result_grand_total
		})

	return report_data