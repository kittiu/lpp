import frappe
from collections import defaultdict

def get_columns():
    return [
        {"label": "ID", "fieldname": "id", "fieldtype": "Link", "options": "Stock Entry", "width": 120},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120},
        {"label": "Stock Entry Type", "fieldname": "stock_entry_type", "fieldtype": "Data", "width": 150},
        {"label": "Default Source Warehouse", "fieldname": "source_warehouse", "fieldtype": "Data", "width": 150},
        {"label": "Default Target Warehouse", "fieldname": "target_warehouse", "fieldtype": "Data", "width": 150},
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
        {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 150},
        {"label": "Quantity", "fieldname": "qty", "fieldtype": "Float", "width": 100},
        {"label": "UOM", "fieldname": "uom", "fieldtype": "Data", "width": 100},
        {"label": "Batch No", "fieldname": "batch_no", "fieldtype": "Data", "width": 150},
        {"label": "Created By", "fieldname": "full_name", "fieldtype": "Data", "width": 150},
    ]

def build_sql_query():
    return """
        SELECT
            se.name AS id,
            CASE se.docstatus
                WHEN 0 THEN 'Draft'
                WHEN 1 THEN 'Submitted'
                WHEN 2 THEN 'Cancelled'
                ELSE 'Unknown'
            END AS status,
            se.stock_entry_type,
            se.from_warehouse AS source_warehouse,
            se.to_warehouse AS target_warehouse,
            sed.item_code,
            sed.item_name,
            sed.qty,
            sed.uom,
            sed.batch_no,
            COALESCE(u.full_name, u.first_name, u.name) AS full_name,
            COALESCE(e.employee_name, '-') AS employee_name,
            se.posting_date
        FROM
            `tabStock Entry` se
        LEFT JOIN
            `tabStock Entry Detail` sed ON sed.parent = se.name
        LEFT JOIN
            `tabUser` u ON u.name = se.owner
        LEFT JOIN
            `tabEmployee` e ON e.name = se.custom_employee
        WHERE
            1=1
            /* Apply docstatus filter if provided */
            AND (%(docstatus)s IS NULL OR se.docstatus = %(docstatus)s)
            /* Apply stock_entry_type filter if provided */
            AND (%(stock_entry_type)s IS NULL OR se.stock_entry_type = %(stock_entry_type)s)
            /* Apply posting_date filters */
            AND (
                %(from_posting_date)s IS NULL
                OR (
                    %(to_posting_date)s IS NOT NULL
                    AND se.posting_date BETWEEN %(from_posting_date)s AND %(to_posting_date)s
                )
                OR (se.posting_date >= %(from_posting_date)s)
            )
            /* Apply custom_employee_name filter if provided */
            AND (
                %(custom_employee_name)s IS NULL
                OR e.name IN (
                    SELECT name FROM `tabEmployee` WHERE name LIKE CONCAT('%%', %(custom_employee_name)s, '%%')
                )
            )
        ORDER BY
            employee_name, se.posting_date
    """

def fetch_data(sql_query, query_params):
    return frappe.db.sql(sql_query, query_params, as_dict=True)

def group_data(data):
    grouped = defaultdict(lambda: defaultdict(list))
    for record in data:
        employee_name = record.get("employee_name", "-")
        posting_date = record.get("posting_date").strftime('%Y-%m-%d') if record.get("posting_date") else "-"
        grouped[employee_name][posting_date].append(record)
    return grouped

def calculate_summaries(grouped_data):
    final_data = []
    grand_total = 0

    for employee_name, posting_dates in grouped_data.items():
        employee_total = 0
        # Employee Header
        final_data.append({
            "id": f"EMPLOYEE : {employee_name}",
            "status": "",
            "stock_entry_type": "",
            "source_warehouse": "",
            "target_warehouse": "",
            "item_code": "",
            "item_name": "",
            "qty": None,
            "uom": "",
            "batch_no": "",
            "full_name": ""
        })
        for posting_date, records in sorted(posting_dates.items()):
            date_total = 0
            # Posting Date Header
            final_data.append({
                "id": posting_date,
                "status": "",
                "stock_entry_type": "",
                "source_warehouse": "",
                "target_warehouse": "",
                "item_code": "",
                "item_name": "",
                "qty": None,
                "uom": "",
                "batch_no": "",
                "full_name": ""
            })
            for record in records:
                qty = record["qty"] or 0
                date_total += qty
                employee_total += qty
                final_data.append(record)
            # Posting Date Summary
            final_data.append({
                "id": "Summary",
                "status": "",
                "stock_entry_type": "",
                "source_warehouse": "",
                "target_warehouse": "",
                "item_code": "",
                "item_name": "Total Quantity",
                "qty": date_total,
                "uom": "",
                "batch_no": "",
                "full_name": ""
            })
        # Employee Summary
        final_data.append({
            "id": "Summary",
            "status": "",
            "stock_entry_type": "",
            "source_warehouse": "",
            "target_warehouse": "",
            "item_code": "",
            "item_name": "Total Quantity",
            "qty": employee_total,
            "uom": "",
            "batch_no": "",
            "full_name": ""
        })
        grand_total += employee_total

    # Grand Total
    final_data.append({
        "id": "Grand Total",
        "status": "",
        "stock_entry_type": "",
        "source_warehouse": "",
        "target_warehouse": "",
        "item_code": "",
        "item_name": "Overall Total Quantity",
        "qty": grand_total,
        "uom": "",
        "batch_no": "",
        "full_name": ""
    })

    return final_data

def assemble_final_data(grouped_data):
    return calculate_summaries(grouped_data)

def execute(filters=None):
    filters = filters or {}
    
    # Step 1: Define Columns
    columns = get_columns()
    
    # Step 2: Build SQL Query
    sql_query = build_sql_query()
    
    # Step 3: Prepare Query Parameters
    query_params = {
        "docstatus": filters.get("docstatus"),
        "stock_entry_type": filters.get("stock_entry_type"),
        "from_posting_date": filters.get("from_posting_date"),
        "to_posting_date": filters.get("to_posting_date"),
        "custom_employee_name": filters.get("custom_employee_name"),
    }
    
    # Step 4: Execute SQL Query
    data = fetch_data(sql_query, query_params)
    
    if not data:
        return columns, []
    
    # Step 5: Group Data
    grouped_data = group_data(data)
    
    # Step 6: Assemble Final Data with Summaries
    final_data = assemble_final_data(grouped_data)
    
    return columns, final_data
