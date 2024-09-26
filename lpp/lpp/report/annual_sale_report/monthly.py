import frappe

@frappe.whitelist()
def monthly(filters=None):
    # Define the columns for the report (January to December)
    columns = [
        {"label": "Code", "fieldname": "code", "fieldtype": "Data", "width": 100},
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Data", "width": 200},
        {"label": "Product", "fieldname": "product", "fieldtype": "Data", "width": 220},
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

    # Execute the SQL query to get sales order data, grouped by customer and items
    results = frappe.db.sql("""
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
            `tabSales Order Item` soi
        ON
            soi.parent = so.name
        GROUP BY
            so.customer, so.customer_name, soi.item_code, soi.item_name, soi.uom
    """, as_dict=True)

    # Map results to the format required by the report
    data = []
    current_customer = None
    customer_totals = {
        "jan_unit": 0, "jan_baht": 0, "feb_unit": 0, "feb_baht": 0, "mar_unit": 0, "mar_baht": 0,
        "apr_unit": 0, "apr_baht": 0, "may_unit": 0, "may_baht": 0, "jun_unit": 0, "jun_baht": 0,
        "jul_unit": 0, "jul_baht": 0, "aug_unit": 0, "aug_baht": 0, "sep_unit": 0, "sep_baht": 0,
        "oct_unit": 0, "oct_baht": 0, "nov_unit": 0, "nov_baht": 0, "dec_unit": 0, "dec_baht": 0,
        "ytd_unit": 0, "ytd_baht": 0
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

    return columns, data
