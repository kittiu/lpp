# Copyright (c) 2024, Ecosoft and contributors
# For license information, please see license.txt

import frappe
import json
from frappe import _, scrub
from collections import defaultdict
from erpnext.accounts.report.general_ledger.general_ledger import execute as general_ledger_execute


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
   
    return columns, data

def get_columns():
    columns = [
        {
			"label": _("Date"),
			"fieldname": "date",
			"fieldtype": "Data",
			"width": 180,
		},
        {
			"label": _("Voucher Code"),
			"fieldname": "voucher_code",
			"fieldtype": "Data",
			"width": 200,
		},
        {
			"label": _("Description"),
			"fieldname": "description",
			"fieldtype": "Data",
			"width": 500,
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
			"width": 160,
		},
        {
			"label": _("Balance"),
			"fieldname": "balance",
			"fieldtype": "Float",
			"width": 160,
		}
	]
    return columns 

from collections import defaultdict

def get_data(filters):
    general_ledger_data = general_ledger_execute(filters)
    report_data = []
    target_data = []
    record_total = {"debit": 0.0, "credit": 0.0, "balance": 0.0}  # Initialize totals

    if general_ledger_data:
        for dt in general_ledger_data[1]:
            # Check if 'posting_date' exists
            if dt.get('posting_date'):
                # Append to report_data
                report_data.append({
                    "account_code": dt.get('account', ''),  # Use get() for safety
                    "date": dt.get('posting_date', ''),
                    "voucher_code": dt.get('voucher_no', ''),
                    "description": dt.get('description', '-'),
                    "debit": dt.get('debit', 0.0),
                    "credit": dt.get('credit', 0.0),
                    "balance": dt.get('balance', 0.0),
                    "voucher_type": dt.get('voucher_type', 'None')
                })

                # Update totals in record_total
                record_total["debit"] += dt.get('debit', 0.0)
                record_total["credit"] += dt.get('credit', 0.0)
                record_total["balance"] += dt.get('balance', 0.0)
        
        # Group data by 'account_code'
        grouped_data = defaultdict(list)
        for item in report_data:
            grouped_data[item['account_code']].append(item)
        
        # Initialize the grand total balance
        grand_total_balance = 0
        
        # Iterate through the grouped data and calculate group totals
        for group, items in sorted(grouped_data.items()):
            debit_group_total = 0
            credit_group_total = 0
            balance_group_total = 0
            
            # Add the group header (summary row for the group)
            target_data.append({
                "account_code": None,
                "date": group,  # Display the group name in the 'date' field
                "voucher_code": "",
                "description": "",
                "debit": None,
                "credit": None,
                "balance": None
            })
            
            # Iterate through the items for this group
            for item in items:
                debit_group_total += item['debit']
                credit_group_total += item['credit']
                balance_group_total += item['balance']
                
				# get remarks by voucher_code on voucher_type
                item['description'] = get_remark_by_voucher_code(item['voucher_type'] , item['voucher_code']) or item['description']
                
                # Append individual items
                target_data.append({
                    "account_code": item['account_code'],
                    "date": item['date'],
                    "voucher_code": item['voucher_code'],
                    "description": item['description'],
                    "debit": item['debit'],
                    "credit": item['credit'],
                    "balance": item['balance']
                })
            
            # Append the group total row
            target_data.append({
                "account_code": None,
                "date": "",
                "voucher_code": "",
                "description": "GROUP TOTAL",
                "debit": debit_group_total,
                "credit": credit_group_total,
                "balance": balance_group_total
            })

            # Update grand total
            grand_total_balance += balance_group_total

        # Add a grand total row if needed
        target_data.append({
            "account_code": None,
            "date": "",
            "voucher_code": "",
            "description": "GRAND TOTAL",
            "debit": record_total["debit"],
            "credit": record_total["credit"],
            "balance": grand_total_balance
        })

    return target_data

def get_remark_by_voucher_code(doc_type, voucher_code):
    # Fetch the remark from the Payment Entry doctype by voucher_code
    remark = frappe.db.get_value(doc_type, {"name": voucher_code}, "remarks")
    return remark