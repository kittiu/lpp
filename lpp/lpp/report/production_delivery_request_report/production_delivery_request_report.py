import frappe
from collections import defaultdict

def execute(filters=None):
    if not filters:
        filters = {}

    # Define columns
    columns = [
        {"label": "ID", "fieldname": "id", "fieldtype": "Link", "options": "Stock Entry", "width": 120},
        {"label": "Employee", "fieldname": "custom_employee_name", "fieldtype": "Data", "width": 150},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120},
        {"label": "Stock Entry Type", "fieldname": "stock_entry_type", "fieldtype": "Data", "width": 150},
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 120},
        {"label": "Default Source Warehouse", "fieldname": "source_warehouse", "fieldtype": "Data", "width": 150},
        {"label": "Default Target Warehouse", "fieldname": "target_warehouse", "fieldtype": "Data", "width": 150},
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
        {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 150},
        {"label": "Quantity", "fieldname": "qty", "fieldtype": "Float", "width": 100},
        {"label": "UOM", "fieldname": "uom", "fieldtype": "Data", "width": 100},
        {"label": "Batch No", "fieldname": "batch_no", "fieldtype": "Data", "width": 150},
        {"label": "Created By", "fieldname": "full_name", "fieldtype": "Data", "width": 150},
    ]

    # Initialize filters for Stock Entry
    stock_entry_filters = {
        "docstatus": filters.get("docstatus"),
        "stock_entry_type": filters.get("stock_entry_type")
    }

    # Handle Posting Date filters
    from_posting_date = filters.get("from_posting_date")
    to_posting_date = filters.get("to_posting_date")

    # Apply 'posting_date' filter only if 'from_posting_date' is provided
    if from_posting_date:
        if to_posting_date:
            stock_entry_filters["posting_date"] = ["between", [from_posting_date, to_posting_date]]
        else:
            stock_entry_filters["posting_date"] = [">=", from_posting_date]
    # Do not apply 'posting_date' filter if 'from_posting_date' is not provided

    # Handle custom_employee_name filter
    custom_employee_name = filters.get("custom_employee_name")
    if custom_employee_name:
        # Search Employee by employee_name using a case-insensitive partial match
        matching_employees = frappe.get_all(
            "Employee",
            filters={
                "employee_name": ["like", f"%{custom_employee_name}%"]
            },
            fields=["name"]
        )
        if matching_employees:
            employee_ids = [emp["name"] for emp in matching_employees]
            stock_entry_filters["custom_employee"] = ["in", employee_ids]
        else:
            # If no employees match the filter, return empty data
            return columns, []

    # Remove filters with None or empty values
    stock_entry_filters = {k: v for k, v in stock_entry_filters.items() if v}

    # Fetch Stock Entries with required fields
    stock_entries = frappe.get_all(
        "Stock Entry",
        filters=stock_entry_filters,
        fields=[
            "name as id",
            "docstatus",
            "stock_entry_type",
            "posting_date",
            "from_warehouse as source_warehouse",
            "to_warehouse as target_warehouse",
            "owner as created_by",
            "custom_employee"
        ]
    )

    if not stock_entries:
        return columns, []

    # Extract unique Stock Entry IDs
    stock_entry_ids = [entry["id"] for entry in stock_entries]

    # Fetch all Stock Entry Details in bulk
    stock_entry_details = frappe.get_all(
        "Stock Entry Detail",
        filters={"parent": ["in", stock_entry_ids]},
        fields=["parent", "item_code", "item_name", "qty", "uom", "batch_no"]
    )

    # Group details by parent Stock Entry ID
    details_map = defaultdict(list)
    for detail in stock_entry_details:
        details_map[detail["parent"]].append(detail)

    # Fetch unique User full names
    created_by_users = list({entry["created_by"] for entry in stock_entries})
    user_map = {
        user["name"]: user["full_name"]
        for user in frappe.get_all(
            "User",
            filters={"name": ["in", created_by_users]},
            fields=["name", "full_name"]
        )
    }

    # Fetch unique Employee full names
    custom_employee_ids = list({entry["custom_employee"] for entry in stock_entries if entry.get("custom_employee")})
    if custom_employee_ids:
        employee_map = {
            emp["name"]: emp["employee_name"]
            for emp in frappe.get_all(
                "Employee",
                filters={"name": ["in", custom_employee_ids]},
                fields=["name", "employee_name"]
            )
        }
    else:
        employee_map = {}

    # Map numeric docstatus to label
    docstatus_map = {
        "0": "Draft",
        "1": "Submitted",
        "2": "Cancelled"
    }

    # Initialize data list and total quantity
    data = []
    total_qty = 0

    # Iterate over Stock Entries and their details to build the report data
    for entry in stock_entries:
        employee_name = employee_map.get(entry.get("custom_employee"), "") if entry.get("custom_employee") else ""
        status = docstatus_map.get(str(entry["docstatus"]), "Unknown")
        created_by = user_map.get(entry["created_by"], "")

        for detail in details_map.get(entry["id"], []):
            qty = detail.get("qty") or 0
            total_qty += qty

            record = {
                "id": entry["id"],
                "custom_employee_name": employee_name,
                "status": status,
                "stock_entry_type": entry["stock_entry_type"],
                "posting_date": entry["posting_date"],
                "source_warehouse": entry["source_warehouse"],
                "target_warehouse": entry["target_warehouse"],
                "item_code": detail["item_code"],
                "item_name": detail["item_name"],
                "qty": qty,
                "uom": detail["uom"],
                "batch_no": detail["batch_no"],
                "full_name": created_by
            }
            data.append(record)

    # Append the total quantity as the last row in the report
    total_row = {
        "id": "Total",
        "custom_employee_name": "",
        "status": "",
        "stock_entry_type": "",
        "posting_date": "",
        "source_warehouse": "",
        "target_warehouse": "",
        "item_code": "",
        "item_name": "Total Quantity",
        "qty": total_qty,
        "uom": "",
        "batch_no": "",
        "full_name": ""
    }
    data.append(total_row)

    return columns, data
