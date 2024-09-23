import frappe

def execute(filters=None):
    columns, data = [], []

    # Define columns
    columns = [
        {"label": "ID", "fieldname": "id", "fieldtype": "Link", "options": "Stock Entry", "width": 120},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120},  # To show status name
        {"label": "Stock Entry Type", "fieldname": "stock_entry_type", "fieldtype": "Data", "width": 150},
        {"label": "Default Source Warehouse", "fieldname": "source_warehouse", "fieldtype": "Data", "width": 150},
        {"label": "Default Target Warehouse", "fieldname": "target_warehouse", "fieldtype": "Data", "width": 150},
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
        {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 150},
        {"label": "Quantity", "fieldname": "qty", "fieldtype": "Float", "width": 100},
        {"label": "UOM", "fieldname": "uom", "fieldtype": "Data", "width": 100},
        {"label": "Source Warehouse", "fieldname": "source_warehouse", "fieldtype": "Data", "width": 150},
        {"label": "Target Warehouse", "fieldname": "target_warehouse", "fieldtype": "Data", "width": 150},
        {"label": "Batch No", "fieldname": "batch_no", "fieldtype": "Data", "width": 150},
        {"label": "Created By", "fieldname": "created_by", "fieldtype": "Data", "width": 150},
        {"label": "Full Name", "fieldname": "full_name", "fieldtype": "Data", "width": 150}  # Add Full Name column
    ]

    # Fetch the Stock Entry details using Frappe ORM
    filters_dict = {
        "docstatus": filters.get("docstatus"),
        "stock_entry_type": filters.get("stock_entry_type")
    }

    # Remove None filters
    filters_dict = {k: v for k, v in filters_dict.items() if v is not None}

    stock_entries = frappe.get_all("Stock Entry", filters=filters_dict, fields=[
        "name as id", "docstatus", "stock_entry_type", "from_warehouse as source_warehouse",
        "to_warehouse as target_warehouse", "owner as created_by"
    ])

    # Fetch Stock Entry Details for each entry
    entries_with_details = []
    for se in stock_entries:
        details = frappe.get_all("Stock Entry Detail", filters={"parent": se["id"]}, fields=[
            "item_code", "item_name", "qty", "uom", "batch_no"
        ])
        for detail in details:
            entry = se.copy()  # Copy the stock entry fields
            entry.update(detail)  # Add detail fields
            entries_with_details.append(entry)

    # Fetch user details (for full name)
    user_full_names = frappe.get_all("User", filters={"name": ["in", [se["created_by"] for se in stock_entries]]}, fields=["name", "full_name"])
    user_map = {user["name"]: user["full_name"] for user in user_full_names}

    # Map numeric docstatus to label text
    docstatus_map = {
        0: "Draft",
        1: "Submitted",
        2: "Cancelled"
    }

    # Initialize total_qty variable to sum up all quantities
    total_qty = 0

    # Add data to the report
    for entry in entries_with_details:
        # Map the numeric docstatus to the appropriate label
        entry["status"] = docstatus_map.get(entry["docstatus"], "Unknown")  # Default to "Unknown" if the status is not recognized

        # Sum the quantity (qty)
        total_qty += entry.get("qty", 0)  # If qty is None or missing, default to 0

        # Add full name from user map
        entry["full_name"] = user_map.get(entry["created_by"], "")

        # Add the entry to the data
        data.append(entry)

    # Append the total quantity as the last row in the report
    data.append({
        "id": "Total",  # Label the row as "Total"
        "status": "",
        "stock_entry_type": "",
        "source_warehouse": "",
        "target_warehouse": "",
        "item_code": "",
        "item_name": "Total Quantity",  # Add label for the total quantity
        "qty": total_qty,  # Display the total quantity
        "uom": "",
        "source_warehouse": "",
        "target_warehouse": "",
        "batch_no": "",
        "created_by": "",
        "full_name": ""
    })

    return columns, data
