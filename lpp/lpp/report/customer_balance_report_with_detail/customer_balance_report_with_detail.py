# Copyright (c) 2024, Ecosoft and contributors
# For license information, please see license.txt

import frappe
from frappe import _, scrub
from collections import defaultdict
from erpnext.accounts.report.accounts_receivable.accounts_receivable import execute as accounts_receivable_execute

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)

	return columns, data

def get_columns():
	columns = [
		{
			"label": _("Customer Code"),
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
			"label": _("Account"),
			"fieldname": "account",
			"fieldtype": "Data",
			"width": 200,
		},
		{
			"label": _("Customer Remark"),
			"fieldname": "remark",
			"fieldtype": "Data",
			"width": 160,
		},
		{
			"label": _(""),
			"fieldname": "amount",
			"fieldtype": "Float",
			"width": 160,
		},
		{
			"label": _(""),
			"fieldname": "supplier",
			"fieldtype": "Data",
			"width": 160,
		},
		{
			"label": _("Balance"),
			"fieldname": "balance",
			"fieldtype": "Data",
			"width": 160,
		}
	]
	return columns

def get_data(filters):
	accounts_receivable_data = accounts_receivable_execute(filters)
	report_data = []
	target_data = []

	if accounts_receivable_data: 

		for dt in accounts_receivable_data[1]:

			invoice_date = frappe.db.sql(
                f"""SELECT tsi.name , posting_date , due_date , COALESCE(payment_terms_template,0) AS payment_terms_template , custom_supplier_purchase_order
					FROM `tabSales Invoice` tsi  
					WHERE tsi.customer = '{dt['party']}'
					AND tsi.name = '{dt['voucher_no']}'
                    """,
                as_dict=True,
            )

			for si in invoice_date:
				report_data.append({
					"customer_group" : dt['customer_group'],
					"entity" : dt['party'],
					"account" : dt['party_account'],
					"term" : 0,
					"voucher_number": dt['voucher_no'],
					"remark" : "-",
					"balance" : dt['invoice_grand_total'],
					"posting_date" : si['posting_date'],
					"due_date" : si['due_date'],
					"supplier_purchase" : si['custom_supplier_purchase_order'],
					"currency" : dt['currency'],
					"terms" : si['payment_terms_template']
				})


		grouped_data = defaultdict(lambda: defaultdict(list))
		for entry in report_data:
			customer_group = entry["customer_group"]
			entity = entry["entity"]
			grouped_data[customer_group][entity].append(entry)

		grand_balance_total = 0
		for customer_group, account_detail in grouped_data.items():
			group_balance_total = 0
			target_data.append({
		        "entity": customer_group,
		        "entity_name": "",
				"account" : "",
		        "remark": "",
				"amount": None,
				"supplier": "",
		        "balance": None
		    })

			customer_balance_total = 0
			for entity, invoices in account_detail.items():
				customer_name = get_customer_name_by_code(entity)
				currency = invoices[0]["currency"] if invoices else "N/A"
				account = invoices[0]["account"] if invoices else ""
				terms = str(invoices[0]["terms"]) if invoices else "0"
				target_data.append({
			        "entity": entity,
			        "entity_name": customer_name,
					"account" : account,
			        "remark": "",
					"amount": None,
					"supplier": "cr.term " + terms,
			        "balance": None
			    })

				balance_result = 0
				for item in invoices:
					balance_result += item['balance']
					customer_balance_total += item['balance']
					group_balance_total += item['balance']
					grand_balance_total += item['balance']
					target_data.append({
			            "entity": "",
			            "entity_name": item['voucher_number'],
			            "account": item['posting_date'],
						"remark" : item['due_date'],
						"amount": item['balance'],
						"supplier": item['supplier_purchase'] if item['supplier_purchase'] else "-",
			            "balance": float(balance_result)
			        })

				# Add total row for the customer
				str_customer_balance_total = str(customer_balance_total) if customer_balance_total is not None else '0.0'
				target_data.append({
					"entity": "Customer Total",
					"entity_name": "",
					"account": "",
					"remark" : "",
					"amount": None,
					"supplier": "",
					"balance": str_customer_balance_total + " " + currency
				})

			# Add total row for the group
			target_data.append({
				"entity": "Group Total",
				"entity_name": "",
				"account": "",
				"remark" : "",
				"amount": None,
				"supplier": "",
				"balance": group_balance_total
			})

		# Add total row for the group
		target_data.append({
			"entity": "",
			"entity_name": "",
			"account": "",
			"remark" : "GRAND TOTAL",
			"amount": None,
			"supplier": "",
			"balance": grand_balance_total
		})	

	return target_data

def get_customer_name_by_code(customer_id):
    # Query the Customer doctype for the customer name based on the customer code
    customer_name = frappe.db.get_value("Customer", customer_id, "customer_name")
    return customer_name