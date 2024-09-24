# Copyright (c) 2024, Ecosoft and contributors
# For license information, please see license.txt

import frappe
import json
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
			"label": _(""),
			"fieldname": "group",
			"fieldtype": "Data",
			"width": 120,
		},
        {
			"label": _("Customer Code"),
			"fieldname": "entity",
			"fieldtype": "Data",
			"width": 140,
            "align": "left"
		},
        {
			"label": _("Customer Name"),
			"fieldname": "entity_name",
			"fieldtype": "Data",
			"width": 400,
            "align": "left"
		},
        {
			"label": _("Customer Remark"),
			"fieldname": "remark",
			"fieldtype": "Data",
			"width": 160,
            "align": "left"
		},{
			"label": _("Balance"),
			"fieldname": "balance",
			"fieldtype": "Currency",
			"width": 160,
		}
	]
    return columns
    
def get_data(filters):
    # try:
    sales_analytics_data = sales_analytics_execute(filters)
    report_data = []
    target_data = []

    if sales_analytics_data and len(sales_analytics_data) > 1:

        for dt in sales_analytics_data[1]:

            query_data = frappe.db.sql(
                f"""SELECT tc.name , tc.customer_group
                    , (CASE WHEN tso.currency is NULL THEN 'THB' ELSE tso.currency END) AS result_currency
                    FROM `tabCustomer`  tc
                    LEFT JOIN `tabSales Order` tso ON tc.name = tso.customer  
                    WHERE tc.name = '{dt["entity"]}'
                    GROUP BY tc.name , tc.customer_group , tso.currency
                    """,
                as_dict=True,
            )

            for qr in query_data:
                json_data = {
                    "group" : qr['customer_group'],
                    "entity" : dt["entity"],
                    "entity_name" : dt["entity_name"],
                    "remark" : qr['result_currency'],
                    "balance" : dt["total"],
                }
                report_data.append(json_data)

        grouped_data = defaultdict(list)
        for item in report_data:
            grouped_data[item['group']].append(item)

        # Prepare the target JSON with summary rows for each group
        grand_total_balance = 0
        for group, items in sorted(grouped_data.items()):
            group_total_balance = 0
            # Add the summary row for the group
            target_data.append({
                "group": group,
                "entity": "",
                "entity_name": "",
                "remark": "",
                "balance": None
            })

            # Add numbered items for each group
            for idx, item in enumerate(items, start=1):
                group_total_balance += item['balance']
                target_data.append({
                    "group": str(idx),  # Sequential numbering as string
                    "entity": item['entity'],
                    "entity_name": item['entity_name'],
                    "remark": item['remark'],
                    "balance": item['balance']
                })

            # Add total row for the group
            target_data.append({
                "group": "",
                "entity": "",
                "entity_name": "Total",
                "remark": "",
                "balance": group_total_balance
            })

            grand_total_balance += group_total_balance

        target_data.append({
            "group": "",
            "entity": "",
            "entity_name": "Grand Total",
            "remark": "",
            "balance": grand_total_balance
        })
	# except KeyError as e:
        # print(f"KeyError encountered: {e}")

    return target_data
    
