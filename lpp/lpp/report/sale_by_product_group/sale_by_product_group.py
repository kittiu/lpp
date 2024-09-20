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
			"label": _("DocNo."),
			"fieldname": "entity",
			"fieldtype": "Data",
			"width": 140,
		},
        {
			"label": _("PROD Name"),
			"fieldname": "entity_name",
			"fieldtype": "Data",
			"width": 400,
		},
		{
			"label": _("Sale Qty"),
			"fieldname": "sale_qty",
			"fieldtype": "Float",
			"width": 160,
		},
		{
			"label": _("Unit"),
			"fieldname": "unit",
			"fieldtype": "Float",
			"width": 160,
		},
		{
			"label": _("PRICE"),
			"fieldname": "price",
			"fieldtype": "Float",
			"width": 160,
		},
		{
			"label": _("BEFORE TOTAL"),
			"fieldname": "before_total",
			"fieldtype": "Float",
			"width": 160,
		},
		{
			"label": _("TOTAL"),
			"fieldname": "total",
			"fieldtype": "Float",
			"width": 160,
		},
		{
			"label": _("STD.COST"),
			"fieldname": "std_cost",
			"fieldtype": "Float",
			"width": 160,
		},
		{
			"label": _("PROFIT"),
			"fieldname": "profit",
			"fieldtype": "Float",
			"width": 160,
		}
	]
	
	return columns

def get_data(filters):
	sales_analytics_data = sales_analytics_execute(filters)
	report_data = []
	target_data = []
	grand_total_sale_qty = 0
	grand_total_before_total = 0
	grand_total_total = 0
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
                f"""SELECT ti.name , ti.item_group
					, tsoi.qty AS sale_qty
					, tsoi.uom AS unit
					, tsoi.rate AS price
					, SUM(tsoi.amount) AS before_total
					, SUM(tso.grand_total) AS total
					, ti.valuation_rate AS std_cost
					FROM `tabItem` ti 
					LEFT JOIN `tabSales Order Item` tsoi ON ti.name = tsoi.item_code 
					LEFT JOIN `tabSales Order` tso ON tsoi.parent = tso.name 
					WHERE ti.name = '{dt["entity"]}'
					AND tso.docstatus = 1
					AND tso.transaction_date BETWEEN '{from_date}' AND '{to_date}'
                    """,
                as_dict=True,
            )

			for qr in query_data:
				json_data = {
					"group" : qr['item_group'],
					"entity" : dt["entity"],
					"entity_name" : dt["entity_name"],
					"sale_qty" : qr['sale_qty'],
					"unit" : qr['unit'],
					"price" : qr['price'],
					"before_total" : qr['before_total'],
					"total" : qr['total'],
					"std_cost" : qr['std_cost'],
					"profit" : qr['before_total']
				}

				grand_total_sale_qty += qr['sale_qty']
				grand_total_before_total += qr['before_total']
				grand_total_total += qr['total']
				report_data.append(json_data)

		grouped_data = defaultdict(list)
		for item in report_data:
			grouped_data[item['group']].append(item)

		for group, items in sorted(grouped_data.items()):
			group_total_sale_qty = 0
			group_total_before_total = 0
			group_total_total = 0
			# Add the summary row for the group
			target_data.append({
				"entity" : group,
				"entity_name" : "",
				"sale_qty" : None,
				"unit" : None,
				"price" : None,
				"before_total" : None,
				"total" : None,
				"std_cost" : None,
				"profit" : None
			})

			# Add numbered items for each group
			for item in items:
				group_total_sale_qty += item['sale_qty']
				group_total_before_total += item['before_total']
				group_total_total += item['total']
				target_data.append({
					"entity" : item['entity'],
					"entity_name" : item['entity_name'],
					"sale_qty" : item['sale_qty'],
					"unit" : item['unit'],
					"price" : item['price'],
					"before_total" : item['before_total'],
					"total" : item['total'],
					"std_cost" : item['std_cost'],
					"profit" : item['before_total']
				})

			# Add total row for the group
			target_data.append({
				"entity" : "GROUP TOTAL",
				"entity_name" : "",
				"sale_qty" : group_total_sale_qty,
				"unit" : None,
				"price" : None,
				"before_total" : group_total_before_total,
				"total" : group_total_total,
				"std_cost" : None,
				"profit" : group_total_before_total
			})

		# grand total
		target_data.append({
			"entity" : "GRAND TOTAL",
			"entity_name" : "",
			"sale_qty" : grand_total_sale_qty,
			"unit" : None,
			"price" : None,
			"before_total" : grand_total_before_total,
			"total" : grand_total_total,
			"std_cost" : None,
			"profit" : grand_total_before_total
		})

	return target_data