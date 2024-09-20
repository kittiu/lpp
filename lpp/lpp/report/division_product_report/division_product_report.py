# Copyright (c) 2024, Ecosoft and contributors
# For license information, please see license.txt

import frappe
import json
from frappe import _, scrub
from collections import defaultdict
from erpnext.selling.report.sales_analytics.sales_analytics import execute as sales_analytics_execute


def execute(filters=None):
	columns = get_column()
	data = get_data(filters)

	return columns, data

def get_column():
	column = [
        {
			"label": _(""),
			"fieldname": "entity",
			"fieldtype": "Data",
			"width": 180,
		},
        {
			"label": _(""),
			"fieldname": "entity_name",
			"fieldtype": "Data",
			"width": 400,
		},
        {
			"label": _("มค."),
			"fieldname": "jan",
			"fieldtype": "Float",
			"width": 120,
		},
		{
			"label": _("กพ."),
			"fieldname": "feb",
			"fieldtype": "Float",
			"width": 120,
		},
		{
			"label": _("มีค."),
			"fieldname": "mar",
			"fieldtype": "Float",
			"width": 120,
		},
		{
			"label": _("เมย."),
			"fieldname": "apr",
			"fieldtype": "Float",
			"width": 120,
		},
		{
			"label": _("พค."),
			"fieldname": "may",
			"fieldtype": "Float",
			"width": 120,
		},
		{
			"label": _("มิย."),
			"fieldname": "jun",
			"fieldtype": "Float",
			"width": 120,
		},
		{
			"label": _("กค."),
			"fieldname": "jul",
			"fieldtype": "Float",
			"width": 120,
		},
		{
			"label": _("สค."),
			"fieldname": "aug",
			"fieldtype": "Float",
			"width": 120,
		},
		{
			"label": _("กย."),
			"fieldname": "sep",
			"fieldtype": "Float",
			"width": 120,
		},
		{
			"label": _("ตค."),
			"fieldname": "oct",
			"fieldtype": "Float",
			"width": 120,
		},
		{
			"label": _("พย."),
			"fieldname": "nov",
			"fieldtype": "Float",
			"width": 120,
		},
		{
			"label": _("ธค."),
			"fieldname": "dec",
			"fieldtype": "Float",
			"width": 120,
		},
		{
			"label": _("รวมทั้งสิ้น"),
			"fieldname": "all_year",
			"fieldtype": "Float",
			"width": 120,
		}
	]

	return column

def get_data(filters=None):
	sales_analytics_data = sales_analytics_execute(filters)
	report_data = []
	target_data = []
	grand_total_balance = 0

	if sales_analytics_data:

		for dt in sales_analytics_data[1]:
			value_sum = get_value_summary_by_month(dt)
			address_line2 = get_customer_address_line2(dt["entity"])
			json_data = {
				"address_line2": address_line2,
				"entity" : dt["entity"],
				"entity_name" : dt["entity_name"],
				"jan" : value_sum['total_jan'],
				"feb" : value_sum['total_feb'],
				"mar" : value_sum['total_mar'],
				"apr" : value_sum['total_apr'],
				"may" : value_sum['total_may'],
				"jun" : value_sum['total_jun'],
				"jul" : value_sum['total_jul'],
				"aug" : value_sum['total_aug'],
				"sep" : value_sum['total_sep'],
				"oct" : value_sum['total_oct'],
				"nov" : value_sum['total_nov'],
				"dec" : value_sum['total_dec'],
				"all_year" : dt["total"]
			}
			report_data.append(json_data)

		grouped_data = defaultdict(list)
		for item in report_data:
			grouped_data[item['address_line2']].append(item)

		grand_total_balance = 0
		grand_total_jan = 0
		grand_total_feb = 0
		grand_total_mar = 0
		grand_total_apr = 0
		grand_total_may = 0
		grand_total_jun = 0
		grand_total_jul = 0
		grand_total_aug = 0
		grand_total_sep = 0
		grand_total_oct = 0
		grand_total_nov = 0
		grand_total_dec = 0
		for group, items in sorted(grouped_data.items()):
			group_total_balance = 0
			group_total_jan = 0
			group_total_feb = 0
			group_total_mar = 0
			group_total_apr = 0
			group_total_may = 0
			group_total_jun = 0
			group_total_jul = 0
			group_total_aug = 0
			group_total_sep = 0
			group_total_oct = 0
			group_total_nov = 0
			group_total_dec = 0

            # Add the summary row for the group
			target_data.append({
				"address_line2": group,
				"entity" : address_line2,
				"entity_name" : "",
				"jan" : None,
				"feb" : None,
				"mar" : None,
				"apr" : None,
				"may" : None,
				"jun" : None,
				"jul" : None,
				"aug" : None,
				"sep" : None,
				"oct" : None,
				"nov" : None,
				"dec" : None,
				"all_year" : None
			})

			# Add numbered items for each group
			for item in items:
				group_total_balance += item['all_year']
				group_total_jan += item['jan']
				group_total_feb += item['feb']
				group_total_mar += item['mar']
				group_total_apr += item['apr']
				group_total_may += item['may']
				group_total_jun += item['jun']
				group_total_jul += item['jul']
				group_total_aug += item['aug']
				group_total_sep += item['sep']
				group_total_oct += item['oct']
				group_total_nov += item['nov']
				group_total_dec += item['dec']

				target_data.append({
                    "address_line2": group,
					"entity" : item["entity"],
					"entity_name" : item["entity_name"],
					"jan" : item["jan"],
					"feb" : item["feb"],
					"mar" : item["mar"],
					"apr" : item["apr"],
					"may" : item["may"],
					"jun" : item["jun"],
					"jul" : item["jul"],
					"aug" : item["aug"],
					"sep" : item["sep"],
					"oct" : item["oct"],
					"nov" : item["nov"],
					"dec" : item["dec"],
					"all_year" : item["all_year"]
                })
			# target_data.extend(items)
	
			# Add total row for the group
			target_data.append({
				"address_line2": group,
				"entity" : "Summary : " + group,
				"entity_name" : "",
				"jan" : group_total_jan,
				"feb" : group_total_feb,
				"mar" : group_total_mar,
				"apr" : group_total_apr,
				"may" : group_total_may,
				"jun" : group_total_jun,
				"jul" : group_total_jul,
				"aug" : group_total_aug,
				"sep" : group_total_sep,
				"oct" : group_total_oct,
				"nov" : group_total_nov,
				"dec" : group_total_dec,
				"all_year" : group_total_balance
			})

			grand_total_balance += group_total_balance
			grand_total_jan += group_total_jan
			grand_total_feb += group_total_feb
			grand_total_mar += group_total_mar
			grand_total_apr += group_total_apr
			grand_total_may += group_total_may
			grand_total_jun += group_total_jun
			grand_total_jul += group_total_jul
			grand_total_aug += group_total_aug
			grand_total_sep += group_total_sep
			grand_total_oct += group_total_oct
			grand_total_nov += group_total_nov
			grand_total_dec += group_total_dec

		target_data.append({
			"address_line2": group,
			"entity" : "Grand Total",
			"entity_name" : "",
			"jan" : grand_total_jan,
			"feb" : grand_total_feb,
			"mar" : grand_total_mar,
			"apr" : grand_total_apr,
			"may" : grand_total_may,
			"jun" : grand_total_jun,
			"jul" : grand_total_jul,
			"aug" : grand_total_aug,
			"sep" : grand_total_sep,
			"oct" : grand_total_oct,
			"nov" : grand_total_nov,
			"dec" : grand_total_dec,
			"all_year" : grand_total_balance
		})

	return target_data

def get_customer_address_line2(customer_name):
    address = frappe.get_all('Address', 
							filters={
								'link_doctype': 'Customer',
								'link_name': customer_name
							}, 
							fields=['address_line2'], 
							limit=1)	

    # Check if the customer was found and has an address_line2
    if address:
        return address[0].get('address_line2', "No address_line2 found")
    else:
        return None

def get_value_summary_by_month(data):
	attributes_with_jan = [key for key in data.keys() if 'jan_' in key]
	attributes_with_feb = [key for key in data.keys() if 'feb_' in key]
	attributes_with_mar = [key for key in data.keys() if 'mar_' in key]
	attributes_with_apr = [key for key in data.keys() if 'apr_' in key]
	attributes_with_may = [key for key in data.keys() if 'may_' in key]
	attributes_with_jun = [key for key in data.keys() if 'jun_' in key]
	attributes_with_jul = [key for key in data.keys() if 'jul_' in key]
	attributes_with_aug = [key for key in data.keys() if 'aug_' in key]
	attributes_with_sep = [key for key in data.keys() if 'sep_' in key]
	attributes_with_oct = [key for key in data.keys() if 'oct_' in key]
	attributes_with_nov = [key for key in data.keys() if 'nov_' in key]
	attributes_with_dec = [key for key in data.keys() if 'dec_' in key]

	jan_values = [(attr, data.get(attr, 0.0)) for attr in attributes_with_jan]
	feb_values = [(attr, data.get(attr, 0.0)) for attr in attributes_with_feb]
	mar_values = [(attr, data.get(attr, 0.0)) for attr in attributes_with_mar]
	apr_values = [(attr, data.get(attr, 0.0)) for attr in attributes_with_apr]
	may_values = [(attr, data.get(attr, 0.0)) for attr in attributes_with_may]
	jun_values = [(attr, data.get(attr, 0.0)) for attr in attributes_with_jun]
	jul_values = [(attr, data.get(attr, 0.0)) for attr in attributes_with_jul]
	aug_values = [(attr, data.get(attr, 0.0)) for attr in attributes_with_aug]
	sep_values = [(attr, data.get(attr, 0.0)) for attr in attributes_with_sep]
	oct_values = [(attr, data.get(attr, 0.0)) for attr in attributes_with_oct]
	nov_values = [(attr, data.get(attr, 0.0)) for attr in attributes_with_nov]
	dec_values = [(attr, data.get(attr, 0.0)) for attr in attributes_with_dec]

	total_jan = sum(value for attr, value in jan_values)
	total_feb = sum(value for attr, value in feb_values)
	total_mar = sum(value for attr, value in mar_values)
	total_apr = sum(value for attr, value in apr_values)
	total_may = sum(value for attr, value in may_values)
	total_jun = sum(value for attr, value in jun_values)
	total_jul = sum(value for attr, value in jul_values)
	total_aug = sum(value for attr, value in aug_values)
	total_sep = sum(value for attr, value in sep_values)
	total_oct = sum(value for attr, value in oct_values)
	total_nov = sum(value for attr, value in nov_values)
	total_dec = sum(value for attr, value in dec_values)

	return {
		"total_jan" : total_jan,
		"total_feb" : total_feb,
		"total_mar" : total_mar,
		"total_apr" : total_apr,
		"total_may" : total_may,
		"total_jun" : total_jun,
		"total_jul" : total_jul,
		"total_aug" : total_aug,
		"total_sep" : total_sep,
		"total_oct" : total_oct,
		"total_nov" : total_nov,
		"total_dec" : total_dec
	}