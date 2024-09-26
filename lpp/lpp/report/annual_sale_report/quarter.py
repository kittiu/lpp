import frappe

@frappe.whitelist()
def quarter(filters=None):
    # Define the columns for the report
    columns = [
        {"label": "Code", "fieldname": "code", "fieldtype": "Data", "width": 100},
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Data", "width": 150},
        {"label": "Product", "fieldname": "product", "fieldtype": "Data", "width": 150},
        {"label": "UOM", "fieldname": "uom", "fieldtype": "Data", "width": 100},
        # Quarterly columns
        {"label": "Q1 Unit", "fieldname": "q1_unit", "fieldtype": "Float", "width": 100},
        {"label": "Q1 Baht", "fieldname": "q1_baht", "fieldtype": "Currency", "width": 100},
        {"label": "Q2 Unit", "fieldname": "q2_unit", "fieldtype": "Float", "width": 100},
        {"label": "Q2 Baht", "fieldname": "q2_baht", "fieldtype": "Currency", "width": 100},
        {"label": "Q3 Unit", "fieldname": "q3_unit", "fieldtype": "Float", "width": 100},
        {"label": "Q3 Baht", "fieldname": "q3_baht", "fieldtype": "Currency", "width": 100},
        {"label": "Q4 Unit", "fieldname": "q4_unit", "fieldtype": "Float", "width": 100},
        {"label": "Q4 Baht", "fieldname": "q4_baht", "fieldtype": "Currency", "width": 100},
        # YTD
        {"label": "YTD Unit", "fieldname": "ytd_unit", "fieldtype": "Float", "width": 100},
        {"label": "YTD Baht", "fieldname": "ytd_baht", "fieldtype": "Currency", "width": 100},
    ]

    # Handle filters
    year_filter = filters.get('year') if filters and 'year' in filters else None
    customer_filter = filters.get('customer') if filters and 'customer' in filters else None
    item_filter = filters.get('item') if filters and 'item' in filters else None

    # Add conditions to the SQL query based on filters
    conditions = []
    if year_filter:
        conditions.append(f"YEAR(so.transaction_date) = {year_filter}")
    if customer_filter:
        conditions.append(f"so.customer = '{customer_filter}'")
    if item_filter:
        conditions.append(f"soi.item_code = '{item_filter}'")

    # Combine the conditions into a WHERE clause
    where_clause = " AND ".join(conditions) if conditions else "1 = 1"  # Default condition if no filters provided

    # Execute the SQL query to get sales order data, grouped by customer and items
    results = frappe.db.sql(f"""
        SELECT
            so.customer,
            so.customer_name,
            soi.item_code,
            soi.item_name,
            soi.uom,
            SUM(CASE WHEN QUARTER(so.transaction_date) = 1 THEN soi.qty ELSE 0 END) AS q1_unit,
            SUM(CASE WHEN QUARTER(so.transaction_date) = 1 THEN soi.qty * soi.rate ELSE 0 END) AS q1_baht,
            SUM(CASE WHEN QUARTER(so.transaction_date) = 2 THEN soi.qty ELSE 0 END) AS q2_unit,
            SUM(CASE WHEN QUARTER(so.transaction_date) = 2 THEN soi.qty * soi.rate ELSE 0 END) AS q2_baht,
            SUM(CASE WHEN QUARTER(so.transaction_date) = 3 THEN soi.qty ELSE 0 END) AS q3_unit,
            SUM(CASE WHEN QUARTER(so.transaction_date) = 3 THEN soi.qty * soi.rate ELSE 0 END) AS q3_baht,
            SUM(CASE WHEN QUARTER(so.transaction_date) = 4 THEN soi.qty ELSE 0 END) AS q4_unit,
            SUM(CASE WHEN QUARTER(so.transaction_date) = 4 THEN soi.qty * soi.rate ELSE 0 END) AS q4_baht,
            SUM(soi.qty) AS ytd_unit,
            SUM(soi.qty * soi.rate) AS ytd_baht
        FROM
            `tabSales Order` so
        JOIN
            `tabSales Order Item` soi ON soi.parent = so.name
        WHERE
            {where_clause}
        GROUP BY
            so.customer, so.customer_name, soi.item_code, soi.item_name, soi.uom
    """, as_dict=True)

    # Map results to the format required by the report
    data = []
    current_customer = None
    customer_totals = {
        "q1_unit": 0,
        "q1_baht": 0,
        "q2_unit": 0,
        "q2_baht": 0,
        "q3_unit": 0,
        "q3_baht": 0,
        "q4_unit": 0,
        "q4_baht": 0,
        "ytd_unit": 0,
        "ytd_baht": 0
    }

    for row in results:
        # Check if we are switching to a new customer
        if row.get('customer') != current_customer:
            # If this is not the first customer, append the totals for the previous customer
            if current_customer:
                data.append({
                    "code": "",
                    "customer": "",
                    "product": f"รวม {total_items} รายการ",
                    "uom": "",
                    "q1_unit": customer_totals["q1_unit"],
                    "q1_baht": customer_totals["q1_baht"],
                    "q2_unit": customer_totals["q2_unit"],
                    "q2_baht": customer_totals["q2_baht"],
                    "q3_unit": customer_totals["q3_unit"],
                    "q3_baht": customer_totals["q3_baht"],
                    "q4_unit": customer_totals["q4_unit"],
                    "q4_baht": customer_totals["q4_baht"],
                    "ytd_unit": customer_totals["ytd_unit"],
                    "ytd_baht": customer_totals["ytd_baht"]
                })

            # Reset customer-specific totals and switch to the new customer
            current_customer = row.get('customer')
            customer_totals = {
                "q1_unit": 0,
                "q1_baht": 0,
                "q2_unit": 0,
                "q2_baht": 0,
                "q3_unit": 0,
                "q3_baht": 0,
                "q4_unit": 0,
                "q4_baht": 0,
                "ytd_unit": 0,
                "ytd_baht": 0
            }
            total_items = 0

            # Add a header row for the new customer
            data.append({
                "code": row.get('customer'),
                "customer": row.get('customer_name'),
                "product": "",
                "uom": "",
                "q1_unit": None,
                "q1_baht": None,
                "q2_unit": None,
                "q2_baht": None,
                "q3_unit": None,
                "q3_baht": None,
                "q4_unit": None,
                "q4_baht": None,
                "ytd_unit": None,
                "ytd_baht": None
            })

        # Add the product row
        data.append({
            "code": '', 
            "customer": row.get('item_code'),
            "product": row.get('item_name'),
            "uom": row.get('uom'),
            "q1_unit": row.get('q1_unit', 0),
            "q1_baht": row.get('q1_baht', 0),
            "q2_unit": row.get('q2_unit', 0),
            "q2_baht": row.get('q2_baht', 0),
            "q3_unit": row.get('q3_unit', 0),
            "q3_baht": row.get('q3_baht', 0),
            "q4_unit": row.get('q4_unit', 0),
            "q4_baht": row.get('q4_baht', 0),
            "ytd_unit": row.get('ytd_unit', 0),
            "ytd_baht": row.get('ytd_baht', 0)
        })

        # Update customer totals
        customer_totals["q1_unit"] += row.get('q1_unit', 0)
        customer_totals["q1_baht"] += row.get('q1_baht', 0)
        customer_totals["q2_unit"] += row.get('q2_unit', 0)
        customer_totals["q2_baht"] += row.get('q2_baht', 0)
        customer_totals["q3_unit"] += row.get('q3_unit', 0)
        customer_totals["q3_baht"] += row.get('q3_baht', 0)
        customer_totals["q4_unit"] += row.get('q4_unit', 0)
        customer_totals["q4_baht"] += row.get('q4_baht', 0)
        customer_totals["ytd_unit"] += row.get('ytd_unit', 0)
        customer_totals["ytd_baht"] += row.get('ytd_baht', 0)
        total_items += 1

    # Append the totals for the last customer
    if current_customer:
        data.append({
            "code": "",
            "customer": "",
            "product": f"รวม {total_items} รายการ",
            "uom": "",
            "q1_unit": customer_totals["q1_unit"],
            "q1_baht": customer_totals["q1_baht"],
            "q2_unit": customer_totals["q2_unit"],
            "q2_baht": customer_totals["q2_baht"],
            "q3_unit": customer_totals["q3_unit"],
            "q3_baht": customer_totals["q3_baht"],
            "q4_unit": customer_totals["q4_unit"],
            "q4_baht": customer_totals["q4_baht"],
            "ytd_unit": customer_totals["ytd_unit"],
            "ytd_baht": customer_totals["ytd_baht"]
        })

    return columns, data
