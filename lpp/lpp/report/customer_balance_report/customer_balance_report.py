# Copyright (c) 2024, Ecosoft and contributors
# For license information, please see license.txt

import frappe
from frappe import _, scrub
from erpnext.selling.report.sales_analytics.sales_analytics import execute as sales_analytics_execute


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
   
    return columns, data

def get_columns():
    print("get_columns")
    columns = [
		{
			"label": _("Customer Group"),
			"fieldname": "customer_group",
			"fieldtype": "Int",
			"width": 40,
		},
        {
			"label": _("Customer Code"),
			"fieldname": "customer_code",
			"fieldtype": "Data",
			"width": 100,
		},
        {
			"label": _("Customer Name"),
			"fieldname": "customer_name",
			"fieldtype": "Data",
			"width": 160,
		}
	]
    print(columns)
    return columns
    
def get_data(filters):
    print("get_data")
    return None
	# try:
    #     sales_analytics_data = sales_analytics_execute(filters)
    #     if sales_analytics_data:
    #         # print("column")
    #         # print(sales_analytics_data[0])
    #         print("data")
    #         print(sales_analytics_data[1])
    #         for dt in sales_analytics_data[1]:
    #             print("entity")
    #             print(dt["entity"])
    #             # print("entity_name")
    #             # print(dt["entity_name"])
	# except KeyError as e:
    #     print(f"KeyError encountered: {e}")
    # return None
    
