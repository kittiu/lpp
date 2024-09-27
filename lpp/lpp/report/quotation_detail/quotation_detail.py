import frappe
from frappe import _
from frappe.utils import getdate, formatdate

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

    # Process the data by month
    monthly_data = {}
    for row in data:
        # Extract the month and year from the date
        month = getdate(row["date"]).month
        year = getdate(row["date"]).year
        month_year = f"{month:02d}-{year}"  # Format as MM-yyyy for sorting
        
        if month_year not in monthly_data:
            monthly_data[month_year] = []
        monthly_data[month_year].append(row)

    # Sort by month-year in ascending order (1-12)
    final_data = []
    for month_year, rows in sorted(monthly_data.items(), key=lambda x: (int(x[0].split("-")[1]), int(x[0].split("-")[0]))):
        # Convert MM-yyyy to the format 'MMM yyyy'
        formatted_month_year = formatdate(f"2024-{month_year[:2]}-01", "MMM yyyy")
        # Add the month-year header row
        final_data.append({
            "name": formatted_month_year,  # Use name field to hold the month-year header
            "date": None,
            "custom_proposer": None,
            "customer_name": None,
            "custom_drawing_buildsheet_no": None,
            "item_name": None,
            "custom_material": None,
            "rate": None,
            "amount": None,
            "custom_marketing_status": None
        })
        # Add the rows for that month
        final_data.extend(rows)

    return final_data
