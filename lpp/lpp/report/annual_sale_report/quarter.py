import frappe
from frappe.utils import cint

@frappe.whitelist()
def quarter(filters=None):
    if not filters:
        filters = {}
    
    # Define the columns for the report
    columns = [
        {"label": "Code", "fieldname": "code", "fieldtype": "Data", "width": 160},
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

    # Handle filters with default None values
    year_filter = cint(filters.get('year'))
    customer_filter = filters.get('customer')
    item_filter = filters.get('item')

    # Build conditions and parameters for sale orders
    conditions = []
    params = {}
    if year_filter:
        conditions.append("YEAR(so.transaction_date) = %(year)s")
        params['year'] = year_filter
    if customer_filter:
        conditions.append("so.customer = %(customer)s")
        params['customer'] = customer_filter
    if item_filter:
        conditions.append("soi.item_code = %(item)s")
        params['item'] = item_filter

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    # Function to execute and return aggregated data
    def get_aggregated_data(query, params):
        return frappe.db.sql(query, params, as_dict=True)

    # Sales Orders Aggregation
    sales_order_query = """
        SELECT
            so.name AS sales_order_name,
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
            so.name, so.customer, so.customer_name, soi.item_code, soi.item_name, soi.uom
        ORDER BY
            so.customer, soi.item_code
    """.format(where_clause=where_clause)

    sales_orders = get_aggregated_data(sales_order_query, params)

    # Extract distinct sales order names
    sales_order_names = [row.sales_order_name for row in sales_orders]

    # Credit Notes Aggregation
    credit_notes = []
    if sales_order_names:
        # Prepare parameterized query for credit notes
        credit_note_query = """
            SELECT
                so.name AS sales_order_name,
                so.customer,
                so.customer_name,
                sii.item_code,
                sii.item_name,
                sii.uom,
                SUM(CASE WHEN QUARTER(si.posting_date) = 1 THEN sii.qty ELSE 0 END) AS q1_unit,
                SUM(CASE WHEN QUARTER(si.posting_date) = 1 THEN sii.amount ELSE 0 END) AS q1_baht,
                SUM(CASE WHEN QUARTER(si.posting_date) = 2 THEN sii.qty ELSE 0 END) AS q2_unit,
                SUM(CASE WHEN QUARTER(si.posting_date) = 2 THEN sii.amount ELSE 0 END) AS q2_baht,
                SUM(CASE WHEN QUARTER(si.posting_date) = 3 THEN sii.qty ELSE 0 END) AS q3_unit,
                SUM(CASE WHEN QUARTER(si.posting_date) = 3 THEN sii.amount ELSE 0 END) AS q3_baht,
                SUM(CASE WHEN QUARTER(si.posting_date) = 4 THEN sii.qty ELSE 0 END) AS q4_unit,
                SUM(CASE WHEN QUARTER(si.posting_date) = 4 THEN sii.amount ELSE 0 END) AS q4_baht,
                SUM(sii.qty) AS ytd_unit,
                SUM(sii.amount) AS ytd_baht
            FROM
                `tabSales Invoice` si
            JOIN
                `tabSales Invoice Item` sii ON sii.parent = si.name
            JOIN
                `tabSales Order` so ON sii.sales_order = so.name
            WHERE
                si.docstatus = 1
                AND si.is_return = 1
                AND si.return_against IS NOT NULL
                AND so.name IN %(sales_orders)s
            GROUP BY
                so.name, so.customer, so.customer_name, sii.item_code, sii.item_name, sii.uom
            ORDER BY
                so.customer, sii.item_code
        """
        credit_params = {'sales_orders': tuple(sales_order_names)}
        credit_notes = get_aggregated_data(credit_note_query, credit_params)

    # Initialize grand totals
    grand_totals = {
        "sale_order": {
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
        },
        "credit_note": {
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
    }

    # Function to append totals to data
    def append_totals(data, totals, label, is_credit=False):
        data.append({
            "code": label,
            "customer": "",
            "product": "",
            "uom": "",
            "q1_unit": totals["q1_unit"] if totals["q1_unit"] else None,
            "q1_baht": totals["q1_baht"] if totals["q1_baht"] else None,
            "q2_unit": totals["q2_unit"] if totals["q2_unit"] else None,
            "q2_baht": totals["q2_baht"] if totals["q2_baht"] else None,
            "q3_unit": totals["q3_unit"] if totals["q3_unit"] else None,
            "q3_baht": totals["q3_baht"] if totals["q3_baht"] else None,
            "q4_unit": totals["q4_unit"] if totals["q4_unit"] else None,
            "q4_baht": totals["q4_baht"] if totals["q4_baht"] else None,
            "ytd_unit": totals["ytd_unit"] if totals["ytd_unit"] else None,
            "ytd_baht": totals["ytd_baht"] if totals["ytd_baht"] else None
        })

    # Initialize report data with Sale Orders header
    data = [{
        "code": "Sale Orders",
        "customer": "",
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
    }]

    # Function to process and append rows
    def process_rows(rows, data, grand_totals_key, label=None):
        current_customer = None
        customer_totals = {key: 0 for key in grand_totals['sale_order']} if grand_totals_key == 'sale_order' else {key: 0 for key in grand_totals['credit_note']}
        total_items = 0

        for row in rows:
            # Switch customer
            if row.customer != current_customer:
                if current_customer is not None:
                    # Append customer totals
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

                # Reset customer totals
                current_customer = row.customer
                customer_totals = {key: 0 for key in customer_totals}
                total_items = 0

                # Append new customer header
                data.append({
                    "code": row.customer,
                    "customer": row.customer_name,
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

            # Append product row
            data.append({
                "code": '',
                "customer": row.item_code,
                "product": row.item_name,
                "uom": row.uom,
                "q1_unit": row.q1_unit,
                "q1_baht": row.q1_baht,
                "q2_unit": row.q2_unit,
                "q2_baht": row.q2_baht,
                "q3_unit": row.q3_unit,
                "q3_baht": row.q3_baht,
                "q4_unit": row.q4_unit,
                "q4_baht": row.q4_baht,
                "ytd_unit": row.ytd_unit,
                "ytd_baht": row.ytd_baht
            })

            # Update customer totals
            for key in customer_totals:
                customer_totals[key] += row.get(key, 0)
                grand_totals[grand_totals_key][key] += row.get(key, 0)
            total_items += 1

        # Append totals for the last customer
        if current_customer is not None:
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

    # Process Sale Orders
    process_rows(sales_orders, data, 'sale_order')

    # Append Credit Notes Header
    if credit_notes:
        data.append({
            "code": "Credit Notes",
            "customer": "",
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

        # Process Credit Notes
        process_rows(credit_notes, data, 'credit_note')

    # Append Grand Totals
    def append_grand_total(data, totals, label):
        data.append({
            "code": label,
            "customer": "",
            "product": "",
            "uom": "",
            "q1_unit": totals["q1_unit"],
            "q1_baht": totals["q1_baht"],
            "q2_unit": totals["q2_unit"],
            "q2_baht": totals["q2_baht"],
            "q3_unit": totals["q3_unit"],
            "q3_baht": totals["q3_baht"],
            "q4_unit": totals["q4_unit"],
            "q4_baht": totals["q4_baht"],
            "ytd_unit": totals["ytd_unit"],
            "ytd_baht": totals["ytd_baht"]
        })

    append_grand_total(data, grand_totals['sale_order'], "Grand Total Sale Orders")
    append_grand_total(data, grand_totals['credit_note'], "Grand Total Credit Notes")

    # Calculate Net Sale Orders (Sale Orders - Credit Notes)
    net_totals = {}
    for key in grand_totals['sale_order']:
        net_totals[key] = grand_totals['sale_order'][key] - grand_totals['credit_note'][key]

    data.append({
        "code": "Net Sale Orders",
        "customer": "",
        "product": "",
        "uom": "",
        "q1_unit": net_totals["q1_unit"],
        "q1_baht": net_totals["q1_baht"],
        "q2_unit": net_totals["q2_unit"],
        "q2_baht": net_totals["q2_baht"],
        "q3_unit": net_totals["q3_unit"],
        "q3_baht": net_totals["q3_baht"],
        "q4_unit": net_totals["q4_unit"],
        "q4_baht": net_totals["q4_baht"],
        "ytd_unit": net_totals["ytd_unit"],
        "ytd_baht": net_totals["ytd_baht"]
    })

    return columns, data
