import frappe

@frappe.whitelist()
def monthly(filters=None):
    # Define the columns for the report (January to December)
    columns = [
        {"label": "Code", "fieldname": "code", "fieldtype": "Data", "width": 180},
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Data", "width": 200},
        {"label": "Product", "fieldname": "product", "fieldtype": "Data", "width": 220, "align": "left"},
        {"label": "UOM", "fieldname": "uom", "fieldtype": "Data", "width": 100},
        # Monthly columns (Jan to Dec)
        {"label": "Jan (Unit)", "fieldname": "jan_unit", "fieldtype": "Float", "width": 120},
        {"label": "Jan (Baht)", "fieldname": "jan_baht", "fieldtype": "Currency", "width": 120},
        {"label": "Feb (Unit)", "fieldname": "feb_unit", "fieldtype": "Float", "width": 120},
        {"label": "Feb (Baht)", "fieldname": "feb_baht", "fieldtype": "Currency", "width": 120},
        {"label": "Mar (Unit)", "fieldname": "mar_unit", "fieldtype": "Float", "width": 120},
        {"label": "Mar (Baht)", "fieldname": "mar_baht", "fieldtype": "Currency", "width": 120},
        {"label": "Apr (Unit)", "fieldname": "apr_unit", "fieldtype": "Float", "width": 120},
        {"label": "Apr (Baht)", "fieldname": "apr_baht", "fieldtype": "Currency", "width": 120},
        {"label": "May (Unit)", "fieldname": "may_unit", "fieldtype": "Float", "width": 120},
        {"label": "May (Baht)", "fieldname": "may_baht", "fieldtype": "Currency", "width": 120},
        {"label": "Jun (Unit)", "fieldname": "jun_unit", "fieldtype": "Float", "width": 120},
        {"label": "Jun (Baht)", "fieldname": "jun_baht", "fieldtype": "Currency", "width": 120},
        {"label": "Jul (Unit)", "fieldname": "jul_unit", "fieldtype": "Float", "width": 120},
        {"label": "Jul (Baht)", "fieldname": "jul_baht", "fieldtype": "Currency", "width": 120},
        {"label": "Aug (Unit)", "fieldname": "aug_unit", "fieldtype": "Float", "width": 120},
        {"label": "Aug (Baht)", "fieldname": "aug_baht", "fieldtype": "Currency", "width": 120},
        {"label": "Sep (Unit)", "fieldname": "sep_unit", "fieldtype": "Float", "width": 120},
        {"label": "Sep (Baht)", "fieldname": "sep_baht", "fieldtype": "Currency", "width": 120},
        {"label": "Oct (Unit)", "fieldname": "oct_unit", "fieldtype": "Float", "width": 120},
        {"label": "Oct (Baht)", "fieldname": "oct_baht", "fieldtype": "Currency", "width": 120},
        {"label": "Nov (Unit)", "fieldname": "nov_unit", "fieldtype": "Float", "width": 120},
        {"label": "Nov (Baht)", "fieldname": "nov_baht", "fieldtype": "Currency", "width": 120},
        {"label": "Dec (Unit)", "fieldname": "dec_unit", "fieldtype": "Float", "width": 120},
        {"label": "Dec (Baht)", "fieldname": "dec_baht", "fieldtype": "Currency", "width": 120},
        # YTD (Year to Date)
        {"label": "YTD (Unit)", "fieldname": "ytd_unit", "fieldtype": "Float", "width": 120},
        {"label": "YTD (Baht)", "fieldname": "ytd_baht", "fieldtype": "Currency", "width": 120},
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
            SUM(CASE WHEN MONTH(so.transaction_date) = 1 THEN soi.qty ELSE 0 END) AS jan_unit,
            SUM(CASE WHEN MONTH(so.transaction_date) = 1 THEN soi.qty * soi.rate ELSE 0 END) AS jan_baht,
            SUM(CASE WHEN MONTH(so.transaction_date) = 2 THEN soi.qty ELSE 0 END) AS feb_unit,
            SUM(CASE WHEN MONTH(so.transaction_date) = 2 THEN soi.qty * soi.rate ELSE 0 END) AS feb_baht,
            SUM(CASE WHEN MONTH(so.transaction_date) = 3 THEN soi.qty ELSE 0 END) AS mar_unit,
            SUM(CASE WHEN MONTH(so.transaction_date) = 3 THEN soi.qty * soi.rate ELSE 0 END) AS mar_baht,
            SUM(CASE WHEN MONTH(so.transaction_date) = 4 THEN soi.qty ELSE 0 END) AS apr_unit,
            SUM(CASE WHEN MONTH(so.transaction_date) = 4 THEN soi.qty * soi.rate ELSE 0 END) AS apr_baht,
            SUM(CASE WHEN MONTH(so.transaction_date) = 5 THEN soi.qty ELSE 0 END) AS may_unit,
            SUM(CASE WHEN MONTH(so.transaction_date) = 5 THEN soi.qty * soi.rate ELSE 0 END) AS may_baht,
            SUM(CASE WHEN MONTH(so.transaction_date) = 6 THEN soi.qty ELSE 0 END) AS jun_unit,
            SUM(CASE WHEN MONTH(so.transaction_date) = 6 THEN soi.qty * soi.rate ELSE 0 END) AS jun_baht,
            SUM(CASE WHEN MONTH(so.transaction_date) = 7 THEN soi.qty ELSE 0 END) AS jul_unit,
            SUM(CASE WHEN MONTH(so.transaction_date) = 7 THEN soi.qty * soi.rate ELSE 0 END) AS jul_baht,
            SUM(CASE WHEN MONTH(so.transaction_date) = 8 THEN soi.qty ELSE 0 END) AS aug_unit,
            SUM(CASE WHEN MONTH(so.transaction_date) = 8 THEN soi.qty * soi.rate ELSE 0 END) AS aug_baht,
            SUM(CASE WHEN MONTH(so.transaction_date) = 9 THEN soi.qty ELSE 0 END) AS sep_unit,
            SUM(CASE WHEN MONTH(so.transaction_date) = 9 THEN soi.qty * soi.rate ELSE 0 END) AS sep_baht,
            SUM(CASE WHEN MONTH(so.transaction_date) = 10 THEN soi.qty ELSE 0 END) AS oct_unit,
            SUM(CASE WHEN MONTH(so.transaction_date) = 10 THEN soi.qty * soi.rate ELSE 0 END) AS oct_baht,
            SUM(CASE WHEN MONTH(so.transaction_date) = 11 THEN soi.qty ELSE 0 END) AS nov_unit,
            SUM(CASE WHEN MONTH(so.transaction_date) = 11 THEN soi.qty * soi.rate ELSE 0 END) AS nov_baht,
            SUM(CASE WHEN MONTH(so.transaction_date) = 12 THEN soi.qty ELSE 0 END) AS dec_unit,
            SUM(CASE WHEN MONTH(so.transaction_date) = 12 THEN soi.qty * soi.rate ELSE 0 END) AS dec_baht,
            SUM(soi.qty) AS ytd_unit,
            SUM(soi.qty * soi.rate) AS ytd_baht,
            soi.uom
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
    distinct_customers = set()
    current_customer = None
    customer_totals = {
        "jan_unit": 0, "jan_baht": 0, "feb_unit": 0, "feb_baht": 0, "mar_unit": 0, "mar_baht": 0,
        "apr_unit": 0, "apr_baht": 0, "may_unit": 0, "may_baht": 0, "jun_unit": 0, "jun_baht": 0,
        "jul_unit": 0, "jul_baht": 0, "aug_unit": 0, "aug_baht": 0, "sep_unit": 0, "sep_baht": 0,
        "oct_unit": 0, "oct_baht": 0, "nov_unit": 0, "nov_baht": 0, "dec_unit": 0, "dec_baht": 0,
        "ytd_unit": 0, "ytd_baht": 0
    }
    grand_totals = {
        "jan_unit": 0, "jan_baht": 0, "feb_unit": 0, "feb_baht": 0, "mar_unit": 0, "mar_baht": 0,
        "apr_unit": 0, "apr_baht": 0, "may_unit": 0, "may_baht": 0, "jun_unit": 0, "jun_baht": 0,
        "jul_unit": 0, "jul_baht": 0, "aug_unit": 0, "aug_baht": 0, "sep_unit": 0, "sep_baht": 0,
        "oct_unit": 0, "oct_baht": 0, "nov_unit": 0, "nov_baht": 0, "dec_unit": 0, "dec_baht": 0,
        "ytd_unit": 0, "ytd_baht": 0
    }

    for row in results:
        distinct_customers.add(row.get('customer'))
        # Check if we are switching to a new customer
        if row.get('customer') != current_customer:
            # If this is not the first customer, append the totals for the previous customer
            if current_customer:
                data.append({
                    "code": "",
                    "customer": "",
                    "product": f"รวม {total_items} รายการ",
                    "uom": "",
                    "jan_unit": customer_totals["jan_unit"],
                    "jan_baht": customer_totals["jan_baht"],
                    "feb_unit": customer_totals["feb_unit"],
                    "feb_baht": customer_totals["feb_baht"],
                    "mar_unit": customer_totals["mar_unit"],
                    "mar_baht": customer_totals["mar_baht"],
                    "apr_unit": customer_totals["apr_unit"],
                    "apr_baht": customer_totals["apr_baht"],
                    "may_unit": customer_totals["may_unit"],
                    "may_baht": customer_totals["may_baht"],
                    "jun_unit": customer_totals["jun_unit"],
                    "jun_baht": customer_totals["jun_baht"],
                    "jul_unit": customer_totals["jul_unit"],
                    "jul_baht": customer_totals["jul_baht"],
                    "aug_unit": customer_totals["aug_unit"],
                    "aug_baht": customer_totals["aug_baht"],
                    "sep_unit": customer_totals["sep_unit"],
                    "sep_baht": customer_totals["sep_baht"],
                    "oct_unit": customer_totals["oct_unit"],
                    "oct_baht": customer_totals["oct_baht"],
                    "nov_unit": customer_totals["nov_unit"],
                    "nov_baht": customer_totals["nov_baht"],
                    "dec_unit": customer_totals["dec_unit"],
                    "dec_baht": customer_totals["dec_baht"],
                    "ytd_unit": customer_totals["ytd_unit"],
                    "ytd_baht": customer_totals["ytd_baht"]
                })

            # Reset customer-specific totals and switch to the new customer
            current_customer = row.get('customer')
            customer_totals = {
                "jan_unit": 0, "jan_baht": 0, "feb_unit": 0, "feb_baht": 0, "mar_unit": 0, "mar_baht": 0,
                "apr_unit": 0, "apr_baht": 0, "may_unit": 0, "may_baht": 0, "jun_unit": 0, "jun_baht": 0,
                "jul_unit": 0, "jul_baht": 0, "aug_unit": 0, "aug_baht": 0, "sep_unit": 0, "sep_baht": 0,
                "oct_unit": 0, "oct_baht": 0, "nov_unit": 0, "nov_baht": 0, "dec_unit": 0, "dec_baht": 0,
                "ytd_unit": 0, "ytd_baht": 0
            }
            total_items = 0

            # Add a header row for the new customer
            data.append({
                "code": row.get('customer'),
                "customer": row.get('customer_name'),
                "product": "",
                "uom": "",
                "jan_unit": None, "jan_baht": None,
                "feb_unit": None, "feb_baht": None,
                "mar_unit": None, "mar_baht": None,
                "apr_unit": None, "apr_baht": None,
                "may_unit": None, "may_baht": None,
                "jun_unit": None, "jun_baht": None,
                "jul_unit": None, "jul_baht": None,
                "aug_unit": None, "aug_baht": None,
                "sep_unit": None, "sep_baht": None,
                "oct_unit": None, "oct_baht": None,
                "nov_unit": None, "nov_baht": None,
                "dec_unit": None, "dec_baht": None,
                "ytd_unit": None, "ytd_baht": None
            })

        # Add the product row
        data.append({
            "code": '', 
            "customer": row.get('item_code'),
            "product": row.get('item_name'),
            "uom": row.get('uom'),
            "jan_unit": row.get('jan_unit', 0),
            "jan_baht": row.get('jan_baht', 0),
            "feb_unit": row.get('feb_unit', 0),
            "feb_baht": row.get('feb_baht', 0),
            "mar_unit": row.get('mar_unit', 0),
            "mar_baht": row.get('mar_baht', 0),
            "apr_unit": row.get('apr_unit', 0),
            "apr_baht": row.get('apr_baht', 0),
            "may_unit": row.get('may_unit', 0),
            "may_baht": row.get('may_baht', 0),
            "jun_unit": row.get('jun_unit', 0),
            "jun_baht": row.get('jun_baht', 0),
            "jul_unit": row.get('jul_unit', 0),
            "jul_baht": row.get('jul_baht', 0),
            "aug_unit": row.get('aug_unit', 0),
            "aug_baht": row.get('aug_baht', 0),
            "sep_unit": row.get('sep_unit', 0),
            "sep_baht": row.get('sep_baht', 0),
            "oct_unit": row.get('oct_unit', 0),
            "oct_baht": row.get('oct_baht', 0),
            "nov_unit": row.get('nov_unit', 0),
            "nov_baht": row.get('nov_baht', 0),
            "dec_unit": row.get('dec_unit', 0),
            "dec_baht": row.get('dec_baht', 0),
            "ytd_unit": row.get('ytd_unit', 0),
            "ytd_baht": row.get('ytd_baht', 0)
        })

        # Update customer totals
        customer_totals["jan_unit"] += row.get('jan_unit', 0)
        customer_totals["jan_baht"] += row.get('jan_baht', 0)
        customer_totals["feb_unit"] += row.get('feb_unit', 0)
        customer_totals["feb_baht"] += row.get('feb_baht', 0)
        customer_totals["mar_unit"] += row.get('mar_unit', 0)
        customer_totals["mar_baht"] += row.get('mar_baht', 0)
        customer_totals["apr_unit"] += row.get('apr_unit', 0)
        customer_totals["apr_baht"] += row.get('apr_baht', 0)
        customer_totals["may_unit"] += row.get('may_unit', 0)
        customer_totals["may_baht"] += row.get('may_baht', 0)
        customer_totals["jun_unit"] += row.get('jun_unit', 0)
        customer_totals["jun_baht"] += row.get('jun_baht', 0)
        customer_totals["jul_unit"] += row.get('jul_unit', 0)
        customer_totals["jul_baht"] += row.get('jul_baht', 0)
        customer_totals["aug_unit"] += row.get('aug_unit', 0)
        customer_totals["aug_baht"] += row.get('aug_baht', 0)
        customer_totals["sep_unit"] += row.get('sep_unit', 0)
        customer_totals["sep_baht"] += row.get('sep_baht', 0)
        customer_totals["oct_unit"] += row.get('oct_unit', 0)
        customer_totals["oct_baht"] += row.get('oct_baht', 0)
        customer_totals["nov_unit"] += row.get('nov_unit', 0)
        customer_totals["nov_baht"] += row.get('nov_baht', 0)
        customer_totals["dec_unit"] += row.get('dec_unit', 0)
        customer_totals["dec_baht"] += row.get('dec_baht', 0)
        customer_totals["ytd_unit"] += row.get('ytd_unit', 0)
        customer_totals["ytd_baht"] += row.get('ytd_baht', 0)
        total_items += 1

        # Update grand total
        grand_totals["jan_unit"] += row.get('jan_unit', 0)
        grand_totals["jan_baht"] += row.get('jan_baht', 0)
        grand_totals["feb_unit"] += row.get('feb_unit', 0)
        grand_totals["feb_baht"] += row.get('feb_baht', 0)
        grand_totals["mar_unit"] += row.get('mar_unit', 0)
        grand_totals["mar_baht"] += row.get('mar_baht', 0)
        grand_totals["apr_unit"] += row.get('apr_unit', 0)
        grand_totals["apr_baht"] += row.get('apr_baht', 0)
        grand_totals["may_unit"] += row.get('may_unit', 0)
        grand_totals["may_baht"] += row.get('may_baht', 0)
        grand_totals["jun_unit"] += row.get('jun_unit', 0)
        grand_totals["jun_baht"] += row.get('jun_baht', 0)
        grand_totals["jul_unit"] += row.get('jul_unit', 0)
        grand_totals["jul_baht"] += row.get('jul_baht', 0)
        grand_totals["aug_unit"] += row.get('aug_unit', 0)
        grand_totals["aug_baht"] += row.get('aug_baht', 0)
        grand_totals["sep_unit"] += row.get('sep_unit', 0)
        grand_totals["sep_baht"] += row.get('sep_baht', 0)
        grand_totals["oct_unit"] += row.get('oct_unit', 0)
        grand_totals["oct_baht"] += row.get('oct_baht', 0)
        grand_totals["nov_unit"] += row.get('nov_unit', 0)
        grand_totals["nov_baht"] += row.get('nov_baht', 0)
        grand_totals["dec_unit"] += row.get('dec_unit', 0)
        grand_totals["dec_baht"] += row.get('dec_baht', 0)
        grand_totals["ytd_unit"] += row.get('ytd_unit', 0)
        grand_totals["ytd_baht"] += row.get('ytd_baht', 0)

    # Append the totals for the last customer
    if current_customer:
        data.append({
            "code": "",
            "customer": "",
            "product": f"รวม {total_items} รายการ",
            "uom": "",
            "jan_unit": customer_totals["jan_unit"],
            "jan_baht": customer_totals["jan_baht"],
            "feb_unit": customer_totals["feb_unit"],
            "feb_baht": customer_totals["feb_baht"],
            "mar_unit": customer_totals["mar_unit"],
            "mar_baht": customer_totals["mar_baht"],
            "apr_unit": customer_totals["apr_unit"],
            "apr_baht": customer_totals["apr_baht"],
            "may_unit": customer_totals["may_unit"],
            "may_baht": customer_totals["may_baht"],
            "jun_unit": customer_totals["jun_unit"],
            "jun_baht": customer_totals["jun_baht"],
            "jul_unit": customer_totals["jul_unit"],
            "jul_baht": customer_totals["jul_baht"],
            "aug_unit": customer_totals["aug_unit"],
            "aug_baht": customer_totals["aug_baht"],
            "sep_unit": customer_totals["sep_unit"],
            "sep_baht": customer_totals["sep_baht"],
            "oct_unit": customer_totals["oct_unit"],
            "oct_baht": customer_totals["oct_baht"],
            "nov_unit": customer_totals["nov_unit"],
            "nov_baht": customer_totals["nov_baht"],
            "dec_unit": customer_totals["dec_unit"],
            "dec_baht": customer_totals["dec_baht"],
            "ytd_unit": customer_totals["ytd_unit"],
            "ytd_baht": customer_totals["ytd_baht"]
        })

    distinct_customer_list = list(distinct_customers)

    result_string = ", ".join([f"'{item}'" for item in distinct_customer_list])

    if result_string:
        data.append({
            "code": "Credit Note Report",
            "customer": "",
            "product": "",
            "uom": "",
            "jan_unit": None,
            "jan_baht": None,
            "feb_unit": None,
            "feb_baht": None,
            "mar_unit": None,
            "mar_baht": None,
            "apr_unit": None,
            "apr_baht": None,
            "may_unit": None,
            "may_baht": None,
            "jun_unit": None,
            "jun_baht": None,
            "jul_unit": None,
            "jul_baht": None,
            "aug_unit": None,
            "aug_baht": None,
            "sep_unit": None,
            "sep_baht": None,
            "oct_unit": None,
            "oct_baht": None,
            "nov_unit": None,
            "nov_baht": None,
            "dec_unit": None,
            "dec_baht": None,
            "ytd_unit": None,
            "ytd_baht": None
        })

        returns = frappe.db.sql(f"""
            SELECT
                si.customer as si_customer,
                si.customer_name as si_customer_name,
                SUM(CASE WHEN MONTH(so.transaction_date) = 1 THEN sii.qty ELSE 0 END) AS jan_unit,
                SUM(CASE WHEN MONTH(so.transaction_date) = 1 THEN si.total ELSE 0 END) AS jan_baht,
                SUM(CASE WHEN MONTH(so.transaction_date) = 2 THEN sii.qty ELSE 0 END) AS feb_unit,
                SUM(CASE WHEN MONTH(so.transaction_date) = 2 THEN si.total ELSE 0 END) AS feb_baht,
                SUM(CASE WHEN MONTH(so.transaction_date) = 3 THEN sii.qty ELSE 0 END) AS mar_unit,
                SUM(CASE WHEN MONTH(so.transaction_date) = 3 THEN si.total ELSE 0 END) AS mar_baht,
                SUM(CASE WHEN MONTH(so.transaction_date) = 4 THEN sii.qty ELSE 0 END) AS apr_unit,
                SUM(CASE WHEN MONTH(so.transaction_date) = 4 THEN si.total ELSE 0 END) AS apr_baht,
                SUM(CASE WHEN MONTH(so.transaction_date) = 5 THEN sii.qty ELSE 0 END) AS may_unit,
                SUM(CASE WHEN MONTH(so.transaction_date) = 5 THEN si.total ELSE 0 END) AS may_baht,
                SUM(CASE WHEN MONTH(so.transaction_date) = 6 THEN sii.qty ELSE 0 END) AS jun_unit,
                SUM(CASE WHEN MONTH(so.transaction_date) = 6 THEN si.total ELSE 0 END) AS jun_baht,
                SUM(CASE WHEN MONTH(so.transaction_date) = 7 THEN sii.qty ELSE 0 END) AS jul_unit,
                SUM(CASE WHEN MONTH(so.transaction_date) = 7 THEN si.total ELSE 0 END) AS jul_baht,
                SUM(CASE WHEN MONTH(so.transaction_date) = 8 THEN sii.qty ELSE 0 END) AS aug_unit,
                SUM(CASE WHEN MONTH(so.transaction_date) = 8 THEN si.total ELSE 0 END) AS aug_baht,
                SUM(CASE WHEN MONTH(so.transaction_date) = 9 THEN sii.qty ELSE 0 END) AS sep_unit,
                SUM(CASE WHEN MONTH(so.transaction_date) = 9 THEN si.total ELSE 0 END) AS sep_baht,
                SUM(CASE WHEN MONTH(so.transaction_date) = 10 THEN sii.qty ELSE 0 END) AS oct_unit,
                SUM(CASE WHEN MONTH(so.transaction_date) = 10 THEN si.total ELSE 0 END) AS oct_baht,
                SUM(CASE WHEN MONTH(so.transaction_date) = 11 THEN sii.qty ELSE 0 END) AS nov_unit,
                SUM(CASE WHEN MONTH(so.transaction_date) = 11 THEN si.total ELSE 0 END) AS nov_baht,
                SUM(CASE WHEN MONTH(so.transaction_date) = 12 THEN sii.qty ELSE 0 END) AS dec_unit,
                SUM(CASE WHEN MONTH(so.transaction_date) = 12 THEN si.total ELSE 0 END) AS dec_baht,
                SUM(sii.qty) AS ytd_unit,
                SUM(si.total) AS ytd_baht
            FROM
                `tabSales Order` so
            JOIN
                `tabSales Order Item` soi ON soi.parent = so.name
            INNER JOIN
                `tabSales Invoice Item` sii ON sii.sales_order = so.name AND sii.item_code = soi.item_code
            INNER JOIN
                `tabSales Invoice` si ON si.name = sii.parent AND si.status = 'Return'
            WHERE 
                si.customer in ({result_string})
            GROUP BY
                so.customer, so.customer_name, soi.item_code, soi.item_name, soi.uom
        """, as_dict=True)

        returns_totals = {
            "jan_unit": 0, "jan_baht": 0, "feb_unit": 0, "feb_baht": 0, "mar_unit": 0, "mar_baht": 0,
            "apr_unit": 0, "apr_baht": 0, "may_unit": 0, "may_baht": 0, "jun_unit": 0, "jun_baht": 0,
            "jul_unit": 0, "jul_baht": 0, "aug_unit": 0, "aug_baht": 0, "sep_unit": 0, "sep_baht": 0,
            "oct_unit": 0, "oct_baht": 0, "nov_unit": 0, "nov_baht": 0, "dec_unit": 0, "dec_baht": 0,
            "ytd_unit": 0, "ytd_baht": 0
        }
        totals = {
            "jan_unit": 0, "jan_baht": 0, "feb_unit": 0, "feb_baht": 0, "mar_unit": 0, "mar_baht": 0,
            "apr_unit": 0, "apr_baht": 0, "may_unit": 0, "may_baht": 0, "jun_unit": 0, "jun_baht": 0,
            "jul_unit": 0, "jul_baht": 0, "aug_unit": 0, "aug_baht": 0, "sep_unit": 0, "sep_baht": 0,
            "oct_unit": 0, "oct_baht": 0, "nov_unit": 0, "nov_baht": 0, "dec_unit": 0, "dec_baht": 0,
            "ytd_unit": 0, "ytd_baht": 0
        }

        # Append the 'Return' rows to the data
        for return_row in returns:
            data.append({
                "code": f"{return_row.get('si_customer')}",
                "customer": return_row.get('si_customer_name'),
                "product": "",
                "uom": "",
                "jan_unit": return_row.get('jan_unit', 0),
                "jan_baht": return_row.get('jan_baht', 0),
                "feb_unit": return_row.get('feb_unit', 0),
                "feb_baht": return_row.get('feb_baht', 0),
                "mar_unit": return_row.get('mar_unit', 0),
                "mar_baht": return_row.get('mar_baht', 0),
                "apr_unit": return_row.get('apr_unit', 0),
                "apr_baht": return_row.get('apr_baht', 0),
                "may_unit": return_row.get('may_unit', 0),
                "may_baht": return_row.get('may_baht', 0),
                "jun_unit": return_row.get('jun_unit', 0),
                "jun_baht": return_row.get('jun_baht', 0),
                "jul_unit": return_row.get('jul_unit', 0),
                "jul_baht": return_row.get('jul_baht', 0),
                "aug_unit": return_row.get('aug_unit', 0),
                "aug_baht": return_row.get('aug_baht', 0),
                "sep_unit": return_row.get('sep_unit', 0),
                "sep_baht": return_row.get('sep_baht', 0),
                "oct_unit": return_row.get('oct_unit', 0),
                "oct_baht": return_row.get('oct_baht', 0),
                "nov_unit": return_row.get('nov_unit', 0),
                "nov_baht": return_row.get('nov_baht', 0),
                "dec_unit": return_row.get('dec_unit', 0),
                "dec_baht": return_row.get('dec_baht', 0),
                "ytd_unit": return_row.get('ytd_unit', 0),
                "ytd_baht": return_row.get('ytd_baht', 0),
            })

            #Update returns total
            returns_totals["jan_unit"] += return_row.get('jan_unit', 0)
            returns_totals["jan_baht"] += return_row.get('jan_baht', 0)
            returns_totals["feb_unit"] += return_row.get('feb_unit', 0)
            returns_totals["feb_baht"] += return_row.get('feb_baht', 0)
            returns_totals["mar_unit"] += return_row.get('mar_unit', 0)
            returns_totals["mar_baht"] += return_row.get('mar_baht', 0)
            returns_totals["apr_unit"] += return_row.get('apr_unit', 0)
            returns_totals["apr_baht"] += return_row.get('apr_baht', 0)
            returns_totals["may_unit"] += return_row.get('may_unit', 0)
            returns_totals["may_baht"] += return_row.get('may_baht', 0)
            returns_totals["jun_unit"] += return_row.get('jun_unit', 0)
            returns_totals["jun_baht"] += return_row.get('jun_baht', 0)
            returns_totals["jul_unit"] += return_row.get('jul_unit', 0)
            returns_totals["jul_baht"] += return_row.get('jul_baht', 0)
            returns_totals["aug_unit"] += return_row.get('aug_unit', 0)
            returns_totals["aug_baht"] += return_row.get('aug_baht', 0)
            returns_totals["sep_unit"] += return_row.get('sep_unit', 0)
            returns_totals["sep_baht"] += return_row.get('sep_baht', 0)
            returns_totals["oct_unit"] += return_row.get('oct_unit', 0)
            returns_totals["oct_baht"] += return_row.get('oct_baht', 0)
            returns_totals["nov_unit"] += return_row.get('nov_unit', 0)
            returns_totals["nov_baht"] += return_row.get('nov_baht', 0)
            returns_totals["dec_unit"] += return_row.get('dec_unit', 0)
            returns_totals["dec_baht"] += return_row.get('dec_baht', 0)
            returns_totals["ytd_unit"] += return_row.get('ytd_unit', 0)
            returns_totals["ytd_baht"] += return_row.get('ytd_baht', 0)

        # คำนวณ grand_totals - returns_totals
        totals["jan_unit"] = grand_totals["jan_unit"] + returns_totals["jan_unit"]
        totals["jan_baht"] = grand_totals["jan_baht"] + returns_totals["jan_baht"]
        totals["feb_unit"] = grand_totals["feb_unit"] + returns_totals["feb_unit"]
        totals["feb_baht"] = grand_totals["feb_baht"] + returns_totals["feb_baht"]
        totals["mar_unit"] = grand_totals["mar_unit"] + returns_totals["mar_unit"]
        totals["mar_baht"] = grand_totals["mar_baht"] + returns_totals["mar_baht"]
        totals["apr_unit"] = grand_totals["apr_unit"] + returns_totals["apr_unit"]
        totals["apr_baht"] = grand_totals["apr_baht"] + returns_totals["apr_baht"]
        totals["may_unit"] = grand_totals["may_unit"] + returns_totals["may_unit"]
        totals["may_baht"] = grand_totals["may_baht"] + returns_totals["may_baht"]
        totals["jun_unit"] = grand_totals["jun_unit"] + returns_totals["jun_unit"]
        totals["jun_baht"] = grand_totals["jun_baht"] + returns_totals["jun_baht"]
        totals["jul_unit"] = grand_totals["jul_unit"] + returns_totals["jul_unit"]
        totals["jul_baht"] = grand_totals["jul_baht"] + returns_totals["jul_baht"]
        totals["aug_unit"] = grand_totals["aug_unit"] + returns_totals["aug_unit"]
        totals["aug_baht"] = grand_totals["aug_baht"] + returns_totals["aug_baht"]
        totals["sep_unit"] = grand_totals["sep_unit"] + returns_totals["sep_unit"]
        totals["sep_baht"] = grand_totals["sep_baht"] + returns_totals["sep_baht"]
        totals["oct_unit"] = grand_totals["oct_unit"] + returns_totals["oct_unit"]
        totals["oct_baht"] = grand_totals["oct_baht"] + returns_totals["oct_baht"]
        totals["nov_unit"] = grand_totals["nov_unit"] + returns_totals["nov_unit"]
        totals["nov_baht"] = grand_totals["nov_baht"] + returns_totals["nov_baht"]
        totals["dec_unit"] = grand_totals["dec_unit"] + returns_totals["dec_unit"]
        totals["dec_baht"] = grand_totals["dec_baht"] + returns_totals["dec_baht"]
        totals["ytd_unit"] = grand_totals["ytd_unit"] + returns_totals["ytd_unit"]
        totals["ytd_baht"] = grand_totals["ytd_baht"] + returns_totals["ytd_baht"]

        #Add Grand Total
        data.append({
            "code": "Grand Total Sale Orders",
            "customer": "",
            "product": "",
            "uom": "",
            "jan_unit": grand_totals["jan_unit"],
            "jan_baht": grand_totals["jan_baht"],
            "feb_unit": grand_totals["feb_unit"],
            "feb_baht": grand_totals["feb_baht"],
            "mar_unit": grand_totals["mar_unit"],
            "mar_baht": grand_totals["mar_baht"],
            "apr_unit": grand_totals["apr_unit"],
            "apr_baht": grand_totals["apr_baht"],
            "may_unit": grand_totals["may_unit"],
            "may_baht": grand_totals["may_baht"],
            "jun_unit": grand_totals["jun_unit"],
            "jun_baht": grand_totals["jun_baht"],
            "jul_unit": grand_totals["jul_unit"],
            "jul_baht": grand_totals["jul_baht"],
            "aug_unit": grand_totals["aug_unit"],
            "aug_baht": grand_totals["aug_baht"],
            "sep_unit": grand_totals["sep_unit"],
            "sep_baht": grand_totals["sep_baht"],
            "oct_unit": grand_totals["oct_unit"],
            "oct_baht": grand_totals["oct_baht"],
            "nov_unit": grand_totals["nov_unit"],
            "nov_baht": grand_totals["nov_baht"],
            "dec_unit": grand_totals["dec_unit"],
            "dec_baht": grand_totals["dec_baht"],
            "ytd_unit": grand_totals["ytd_unit"],
            "ytd_baht": grand_totals["ytd_baht"]
        })

        #Add Returns Total
        data.append({
            "code": "Grand Total Credit Notes",
            "customer": "",
            "product": "",
            "uom": "",
            "jan_unit": returns_totals["jan_unit"],
            "jan_baht": returns_totals["jan_baht"],
            "feb_unit": returns_totals["feb_unit"],
            "feb_baht": returns_totals["feb_baht"],
            "mar_unit": returns_totals["mar_unit"],
            "mar_baht": returns_totals["mar_baht"],
            "apr_unit": returns_totals["apr_unit"],
            "apr_baht": returns_totals["apr_baht"],
            "may_unit": returns_totals["may_unit"],
            "may_baht": returns_totals["may_baht"],
            "jun_unit": returns_totals["jun_unit"],
            "jun_baht": returns_totals["jun_baht"],
            "jul_unit": returns_totals["jul_unit"],
            "jul_baht": returns_totals["jul_baht"],
            "aug_unit": returns_totals["aug_unit"],
            "aug_baht": returns_totals["aug_baht"],
            "sep_unit": returns_totals["sep_unit"],
            "sep_baht": returns_totals["sep_baht"],
            "oct_unit": returns_totals["oct_unit"],
            "oct_baht": returns_totals["oct_baht"],
            "nov_unit": returns_totals["nov_unit"],
            "nov_baht": returns_totals["nov_baht"],
            "dec_unit": returns_totals["dec_unit"],
            "dec_baht": returns_totals["dec_baht"],
            "ytd_unit": returns_totals["ytd_unit"],
            "ytd_baht": returns_totals["ytd_baht"]
        })

        #Add Total
        data.append({
            "code": "Net Sales Orders",
            "customer": "",
            "product": "",
            "uom": "",
            "jan_unit": totals["jan_unit"],
            "jan_baht": totals["jan_baht"],
            "feb_unit": totals["feb_unit"],
            "feb_baht": totals["feb_baht"],
            "mar_unit": totals["mar_unit"],
            "mar_baht": totals["mar_baht"],
            "apr_unit": totals["apr_unit"],
            "apr_baht": totals["apr_baht"],
            "may_unit": totals["may_unit"],
            "may_baht": totals["may_baht"],
            "jun_unit": totals["jun_unit"],
            "jun_baht": totals["jun_baht"],
            "jul_unit": totals["jul_unit"],
            "jul_baht": totals["jul_baht"],
            "aug_unit": totals["aug_unit"],
            "aug_baht": totals["aug_baht"],
            "sep_unit": totals["sep_unit"],
            "sep_baht": totals["sep_baht"],
            "oct_unit": totals["oct_unit"],
            "oct_baht": totals["oct_baht"],
            "nov_unit": totals["nov_unit"],
            "nov_baht": totals["nov_baht"],
            "dec_unit": totals["dec_unit"],
            "dec_baht": totals["dec_baht"],
            "ytd_unit": totals["ytd_unit"],
            "ytd_baht": totals["ytd_baht"]
        })

    return columns, data
