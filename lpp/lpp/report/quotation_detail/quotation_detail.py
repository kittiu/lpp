# your_app/reports/quotation_report/quotation_report.py

import frappe
from frappe import _
from frappe.utils import getdate

def execute(filters=None):
    if not filters:
        filters = {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Quotation No."), "fieldname": "name", "fieldtype": "Data", "width": 200},
        {"label": _("Date"), "fieldname": "date", "fieldtype": "Date", "width": 150},
        {"label": _("Proposer Name"), "fieldname": "custom_proposer", "fieldtype": "Data", "width": 200},
        {"label": _("Customer"), "fieldname": "customer_name", "fieldtype": "Data", "width": 200},
        {"label": _("Drawing"), "fieldname": "custom_drawing_buildsheet_no", "fieldtype": "Data", "width": 150},
        {"label": _("Product Name"), "fieldname": "item_name", "fieldtype": "Data", "width": 250},
        {"label": _("Material"), "fieldname": "custom_material", "fieldtype": "Data", "width": 200},
        {"label": _("Unit Price"), "fieldname": "rate", "fieldtype": "Currency", "width": 150},
        {"label": _("Tooling Price"), "fieldname": "amount", "fieldtype": "Currency", "width": 150},
        {"label": _("Marketing Status"), "fieldname": "custom_marketing_status", "fieldtype": "Data", "width": 150},
    ]

def get_data(filters):
    year = filters.get("year")
    if year:
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"
    else:
        # If no year filter is provided, fetch all records
        start_date = None
        end_date = None

    # Build the query
    conditions = []
    if start_date and end_date:
        conditions.append(f"quotation.transaction_date BETWEEN %(start_date)s AND %(end_date)s")

    query = """
        SELECT 
            quotation.name AS name,
            quotation.transaction_date AS date,
            quotation.custom_proposer AS custom_proposer,
            quotation.customer_name AS customer_name,
            item.custom_drawing__buildsheet_no AS custom_drawing_buildsheet_no,
            item.item_name AS item_name,
            item.custom_material AS custom_material,
            quotation_item.rate AS rate,
            quotation_item.amount AS amount,
            quotation.custom_marketing_status AS custom_marketing_status
        FROM 
            `tabQuotation` quotation
        JOIN
            `tabQuotation Item` quotation_item ON quotation.name = quotation_item.parent
        JOIN
            `tabItem` item ON quotation_item.item_code = item.name
        WHERE 
            quotation.docstatus = 1
    """

    if conditions:
        query += " AND " + " AND ".join(conditions)

    # Execute the query
    data = frappe.db.sql(
        query,
        {
            "start_date": start_date,
            "end_date": end_date
        },
        as_dict=True
    )

    return data
