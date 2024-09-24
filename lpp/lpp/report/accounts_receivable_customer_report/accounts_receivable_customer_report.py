# Copyright (c) 2024, Ecosoft and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from collections import defaultdict
from erpnext.accounts.report.bank_clearance_summary.bank_clearance_summary import execute as journal_entry_execute

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
			"width": 160,
		},
		{
			"label": _("Date"),
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 120,
		},
		{
			"label": _("Doc No."),
			"fieldname": "parent",
			"fieldtype": "Dynamic Link",
			"options": "voucher_type", 
			"width": 180,
		},
		{
			"label": _("DESCRIPTION"),
			"fieldname": "remarks",
			"fieldtype": "Data",
			"width": 160,
		},
		{
			"label": _("Exchange"),
			"fieldname": "exchange_rate",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Debit"),
			"fieldname": "debit",
			"fieldtype": "Float",
			"width": 160,
		},
		{
			"label": _("Credit"),
			"fieldname": "credit",
			"fieldtype": "Float",
			"width": 130,
		},
		{
			"label": _("Balance"),
			"fieldname": "balance",
			"fieldtype": "Float",
			"width": 130,
		},
		{
			"label": _("Debit In Local Currency"),
			"fieldname": "debit_in_account_currency",
			"fieldtype": "Float",
			"width": 130,
		},
		{
			"label": _("Credit In Local Currency"),
			"fieldname": "credit_in_account_currency",
			"fieldtype": "Float",
			"width": 130,
		},
		{
			"label": _("Balance In Local Currency"),
			"fieldname": "balance_in_account_currency",
			"fieldtype": "Float",
			"width": 130,
		},
	]
	return columns

def get_data(filters):
	# SQL query to fetch data
	query_data = frappe.db.sql(
		"""
		SELECT 
			concat(tc.name, ' ', tc.customer_name) as customer_name,
			jv.posting_date,
			jvd.parent,
			jvd.user_remark,
			jvd.exchange_rate,
			jvd.debit,
			jvd.credit,
			(jvd.debit - jvd.credit) as balance,
			jvd.debit_in_account_currency,
			jvd.credit_in_account_currency,
			(jvd.debit_in_account_currency - jvd.credit_in_account_currency) as balance_in_account_currency
		FROM
			`tabJournal Entry Account` jvd
		LEFT JOIN `tabJournal Entry` jv ON jvd.parent = jv.name
		LEFT JOIN `tabCustomer` tc ON jvd.customer = tc.name
		WHERE
			jv.docstatus = 1
			AND jv.posting_date >= %(from_date)s
			AND jv.posting_date <= %(to_date)s
		ORDER BY
			posting_date DESC, jv.name DESC
		""",
		filters,  # Passing filters with from_date, to_date
		as_dict=True,
	)

	report_data = []
	target_data = []

	# Grouping data by customer
	grouped_data = defaultdict(list)
	for qr in query_data:
		json_data = {
			"group": qr['customer_name'],
			"posting_date": qr["posting_date"],
			"parent": qr["parent"],
			"remarks": qr['user_remark'],
			"exchange_rate": qr["exchange_rate"],
			"debit": qr['debit'],
			"credit": qr["credit"],
			"balance": qr["balance"],
			"debit_in_account_currency": qr['debit_in_account_currency'],
			"credit_in_account_currency": qr["credit_in_account_currency"],
			"balance_in_account_currency": qr["balance_in_account_currency"],
		}
		report_data.append(json_data)
		grouped_data[json_data['group']].append(json_data)

	# Summing and preparing final data
	grand_total_balance = grand_total_debit = grand_total_credit = 0
	grand_total_debit_in_account_currency = grand_total_credit_in_account_currency = grand_total_balance_in_account_currency = 0

	for group, items in sorted(grouped_data.items()):
		group_total_balance = group_total_debit = group_total_credit = 0
		group_total_debit_in_account_currency = group_total_credit_in_account_currency = group_total_balance_in_account_currency = 0
		
		# Add group header
		target_data.append({
			"group": group,
			"posting_date": "",
			"parent": "",
			"remarks": "",
			"exchange_rate": "",
			"debit": None,
			"credit": None,
			"balance": None,
			"debit_in_account_currency": None,
			"credit_in_account_currency": None,
			"balance_in_account_currency": None,
		})

		# Add individual entries
		for idx, item in enumerate(items, start=1):
			group_total_balance += item['balance']
			group_total_debit += item['debit']
			group_total_credit += item['credit']
			group_total_debit_in_account_currency += item['debit_in_account_currency']
			group_total_credit_in_account_currency += item['credit_in_account_currency']
			group_total_balance_in_account_currency += item['balance_in_account_currency']

			target_data.append({
				"group": str(idx),
				"posting_date": item["posting_date"],
				"parent": item["parent"],
				"remarks": item['remarks'],
				"exchange_rate": item["exchange_rate"],
				"debit": item['debit'],
				"credit": item["credit"],
				"balance": item["balance"],
				"debit_in_account_currency": item['debit_in_account_currency'],
				"credit_in_account_currency": item["credit_in_account_currency"],
				"balance_in_account_currency": item["balance_in_account_currency"],
			})

		# Add group totals
		target_data.append({
			"group": "",
			"posting_date": "",
			"parent": "",
			"remarks": "Total",
			"exchange_rate": "",
			"debit": group_total_debit,
			"credit": group_total_credit,
			"balance": group_total_balance,
			"debit_in_account_currency": group_total_debit_in_account_currency,
			"credit_in_account_currency": group_total_credit_in_account_currency,
			"balance_in_account_currency": group_total_balance_in_account_currency,
		})

		grand_total_balance += group_total_balance
		grand_total_debit += group_total_debit
		grand_total_credit += group_total_credit
		grand_total_debit_in_account_currency += group_total_debit_in_account_currency
		grand_total_credit_in_account_currency += group_total_credit_in_account_currency
		grand_total_balance_in_account_currency += group_total_balance_in_account_currency

	# Add grand totals
	target_data.append({
		"group": "",
		"posting_date": "",
		"parent": "",
		"remarks": "Grand Total",
		"exchange_rate": "",
		"debit": grand_total_debit,
		"credit": grand_total_credit,
		"balance": grand_total_balance,
		"debit_in_account_currency": grand_total_debit_in_account_currency,
		"credit_in_account_currency": grand_total_credit_in_account_currency,
		"balance_in_account_currency": grand_total_balance_in_account_currency,
	})

	return target_data
