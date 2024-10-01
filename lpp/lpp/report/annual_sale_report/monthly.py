import frappe

@frappe.whitelist()
def monthly(filters=None):
    # Define the columns for the report (January to December)
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    columns = [
        {"label": "Customer Group", "fieldname": "customer_group", "fieldtype": "Data", "width": 180, "align": "left"},
        {"label": "Code", "fieldname": "code", "fieldtype": "Data", "width": 180, "align": "left"},
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Data", "width": 200, "align": "left"},
        {"label": "Product", "fieldname": "product", "fieldtype": "Data", "width": 220, "align": "left"},
        {"label": "UOM", "fieldname": "uom", "fieldtype": "Data", "width": 100}
    ]
    
    # Add columns for each month dynamically
    for month in months:
        columns.append({"label": f"{month} (Unit)", "fieldname": f"{month.lower()}_unit", "fieldtype": "Float", "width": 120})
        columns.append({"label": f"{month} (Baht)", "fieldname": f"{month.lower()}_baht", "fieldtype": "Currency", "width": 120})
    
    columns.append({"label": "YTD (Unit)", "fieldname": "ytd_unit", "fieldtype": "Float", "width": 120})
    columns.append({"label": "YTD (Baht)", "fieldname": "ytd_baht", "fieldtype": "Currency", "width": 120})

    # Handle filters
    filters = filters or {}
    conditions = []
    if 'year' in filters:
        conditions.append(f"YEAR(so.transaction_date) = {filters['year']}")
    if 'customer_group' in filters:
        conditions.append(f"cu.customer_group = '{filters['customer_group']}'")
    if 'customer' in filters:
        conditions.append(f"so.customer = '{filters['customer']}'")
    if 'item' in filters:
        conditions.append(f"soi.item_code = '{filters['item']}'")
    where_clause = " AND ".join(conditions) if conditions else "1 = 1"

    # SQL Query for Sales Order
    month_queries = []
    for i, month in enumerate(months):
        unit_query = f"SUM(CASE WHEN MONTH(so.transaction_date) = {i+1} THEN soi.qty ELSE 0 END) AS {month.lower()}_unit"
        baht_query = f"SUM(CASE WHEN MONTH(so.transaction_date) = {i+1} THEN soi.qty * soi.rate ELSE 0 END) AS {month.lower()}_baht"
        month_queries.append(unit_query)
        month_queries.append(baht_query)
    
    query = """
        SELECT cu.customer_group, so.customer, so.customer_name, soi.item_code, soi.item_name, soi.uom,
        {month_queries},
        SUM(soi.qty) AS ytd_unit, SUM(soi.qty * soi.rate) AS ytd_baht
        FROM `tabSales Order` so
        JOIN `tabSales Order Item` soi ON soi.parent = so.name
        JOIN `tabCustomer` cu ON so.customer = cu.name
        WHERE {where_clause}
        GROUP BY cu.customer_group, so.customer, so.customer_name, soi.item_code, soi.item_name, soi.uom
        ORDER BY cu.customer_group, so.customer, soi.item_code
    """.format(
        month_queries=", ".join(month_queries),
        where_clause=where_clause
    )
    
    results = frappe.db.sql(query, as_dict=True)

    # Helper function for updating totals
    def update_totals(row, totals):
        for month in months:
            totals[f"{month.lower()}_unit"] += row.get(f"{month.lower()}_unit", 0)
            totals[f"{month.lower()}_baht"] += row.get(f"{month.lower()}_baht", 0)
        totals["ytd_unit"] += row.get("ytd_unit", 0)
        totals["ytd_baht"] += row.get("ytd_baht", 0)

    # Initialize data structure
    data = []
    group_totals = {}
    customer_totals = {f"{month.lower()}_unit": 0 for month in months}
    customer_totals.update({f"{month.lower()}_baht": 0 for month in months})
    customer_totals.update({"ytd_unit": 0, "ytd_baht": 0})

    grand_totals = customer_totals.copy()
    current_customer = None
    current_group = None
    total_items = 0
    group_total_items = 0

    if results:
        # Append "Sales Order" 
        data.append({
            "customer_group": "Type : Sales Order",
            "code": "",
            "customer": "",
            "product": "",
            "uom": "",
            **{f"{month.lower()}_unit": None for month in months},
            **{f"{month.lower()}_baht": None for month in months},
            "ytd_unit": None, "ytd_baht": None
        })

    # Process results
    for row in results:
        # Check if we are switching customer groups
        if row.get('customer_group') != current_group:
            if current_group is not None:
                if current_customer:
                    data.append({
                        "code": "",
                        "customer": "",
                        "product": f"Total {total_items} items for Customer",
                        "uom": "",
                        **customer_totals
                    })
                    customer_totals = {key: 0 for key in customer_totals}
                    total_items = 0
                    current_customer = None
                data.append({
                    "code": "",
                    "customer": "",
                    "product": f"Total for Customer Group {current_group} ({group_total_items} items)",
                    "uom": "",
                    **group_totals
                })
                group_totals = {key: 0 for key in customer_totals}
                group_total_items = 0

            current_group = row.get('customer_group')
            # Append customer group header
            data.append({
                "customer_group": current_group,
                "code": "",
                "customer": "",
                "product": "",
                "uom": "",
                **{f"{month.lower()}_unit": None for month in months},
                **{f"{month.lower()}_baht": None for month in months},
                "ytd_unit": None, "ytd_baht": None
            })

        if row.get('customer') != current_customer:
            if current_customer: 
                data.append({
                    "code": "",
                    "customer": "",
                    "product": f"Total {total_items} items for Customer",
                    "uom": "",
                    **customer_totals
                })
                customer_totals = {key: 0 for key in customer_totals}
                total_items = 0
            current_customer = row.get('customer')
            data.append({
                "code": row.get('customer'),
                "customer": row.get('customer_name'),
                "product": "",
                "uom": "",
                **{f"{month.lower()}_unit": None for month in months},
                **{f"{month.lower()}_baht": None for month in months},
                "ytd_unit": None, "ytd_baht": None
            })

        data.append({
            "code": "",
            "customer": row.get('item_code'),
            "product": row.get('item_name'),
            "uom": row.get('uom'),
            **{f"{month.lower()}_unit": row.get(f"{month.lower()}_unit", 0) for month in months},
            **{f"{month.lower()}_baht": row.get(f"{month.lower()}_baht", 0) for month in months},
            "ytd_unit": row.get("ytd_unit", 0),
            "ytd_baht": row.get("ytd_baht", 0)
        })

        update_totals(row, customer_totals)
        update_totals(row, grand_totals)
        total_items += 1
        group_total_items += 1

    # Append the final customer totals
    if current_customer:
        data.append({
            "code": "",
            "customer": "",
            "product": f"Total {total_items} items for Customer",
            "uom": "",
            **customer_totals
        })

    if current_group:
        data.append({
            "code": "",
            "customer": "",
            "product": f"Total for Customer Group {current_group} ({group_total_items} items)",
            "uom": "",
            **group_totals
        })

    # Query for Sales Invoice Item (Credit Notes)
    result_string = ", ".join([f"'{row.get('customer')}'" for row in results])

    if result_string:
        return_queries = []
        for i, month in enumerate(months):
            unit_query = f"SUM(CASE WHEN MONTH(si.posting_date) = {i+1} THEN sii.qty ELSE 0 END) AS {month.lower()}_unit"
            baht_query = f"SUM(CASE WHEN MONTH(si.posting_date) = {i+1} THEN sii.qty * sii.rate ELSE 0 END) AS {month.lower()}_baht"
            return_queries.append(unit_query)
            return_queries.append(baht_query)

        return_query = """
            SELECT si.customer, si.customer_name,
            sii.item_code, sii.item_name, sii.uom,
            {return_queries},
            SUM(sii.qty) AS ytd_unit, SUM(sii.qty * sii.rate) AS ytd_baht
            FROM `tabSales Invoice` si
            JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
            WHERE si.customer IN ({result_string}) AND si.docstatus = 1 AND si.is_return = 1
            GROUP BY si.customer, si.customer_name
        """.format(
            return_queries=", ".join(return_queries),
            result_string=result_string
        )

        returns = frappe.db.sql(return_query, as_dict=True)
    else:
        returns = []

    # Process return (credit notes) and add them to data
    return_totals = {f"{month.lower()}_unit": 0 for month in months}
    return_totals.update({f"{month.lower()}_baht": 0 for month in months})
    return_totals.update({"ytd_unit": 0, "ytd_baht": 0})

    current_return_customer = None
    return_customer_totals = {key: 0 for key in return_totals}
    return_total_items = 0

    if returns:
        # Append "Credit Notes" header
        data.append({
            "customer_group": "Type : Credit Notes",
            "code": "",
            "customer": "",
            "product": "",
            "uom": "",
            **{f"{month.lower()}_unit": None for month in months},
            **{f"{month.lower()}_baht": None for month in months},
            "ytd_unit": None, "ytd_baht": None
        })

    for return_row in returns:
        if return_row.get('customer') != current_return_customer:
            if current_return_customer:
                data.append({
                    "code": "",
                    "customer": "",
                    "product": f"รวม {return_total_items} รายการ",
                    "uom": "",
                    **return_customer_totals
                })
            current_return_customer = return_row.get('customer')
            return_customer_totals = {key: 0 for key in return_totals}
            return_total_items = 0
            data.append({
                "code": return_row.get('customer'),
                "customer": return_row.get('customer_name'),
                "product": "",
                "uom": "",
                **{f"{month.lower()}_unit": None for month in months},
                **{f"{month.lower()}_baht": None for month in months},
                "ytd_unit": None, "ytd_baht": None
            })

        data.append({
            "code": "",
            "customer": return_row.get('item_code'),
            "product": return_row.get('item_name'),
            "uom": return_row.get('uom'),
            **{f"{month.lower()}_unit": return_row.get(f"{month.lower()}_unit", 0) for month in months},
            **{f"{month.lower()}_baht": return_row.get(f"{month.lower()}_baht", 0) for month in months},
            "ytd_unit": return_row.get("ytd_unit", 0),
            "ytd_baht": return_row.get("ytd_baht", 0)
        })

        update_totals(return_row, return_customer_totals)
        update_totals(return_row, return_totals)
        return_total_items += 1

    if current_return_customer:
        data.append({
            "code": "",
            "customer": "",
            "product": f"รวม {return_total_items} รายการ",
            "uom": "",
            **return_customer_totals
        })

    if results:
        # Append "Grand Total" after processing returns
        data.append({
            "customer_group": "Grand Total Sales Orders",
            "code": "",
            "customer": "",
            "product": "",
            "uom": "",
            **grand_totals
        })

    if returns:
        # Append return totals to data
        data.append({
            "customer_group": "Grand Total Credit Notes",
            "code": "",
            "customer": "",
            "product": "",
            "uom": "",
            **return_totals
        })

    # Calculate net totals after returns
    net_totals = {key: grand_totals[key] + return_totals[key] for key in grand_totals}

    if results or returns:
        # Append "Net Sale Orders"
        data.append({
            "customer_group": "Net Sales",
            "code": "",
            "customer": "",
            "product": "",
            "uom": "",
            **net_totals
        })

    return columns, data
