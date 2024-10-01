import frappe
from frappe.utils import cint

@frappe.whitelist()
def quarter(filters=None):
    if not filters:
        filters = {}
    
    # Define the columns for the report, including Customer Group
    columns = [
        {"label": "Customer Group", "fieldname": "customer_group", "fieldtype": "Data", "width": 150},
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
    customer_group_filter = filters.get('customer_group')
    customer_filter = filters.get('customer')
    item_filter = filters.get('item')

    # Build conditions and parameters for sale orders
    conditions = []
    params = {}
    if year_filter:
        conditions.append("YEAR(so.transaction_date) = %(year)s")
        params['year'] = year_filter
    if customer_group_filter:
        conditions.append("c.customer_group = %(customer_group)s")
        params['customer_group'] = customer_group_filter
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
            c.customer_group,
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
        JOIN
            `tabCustomer` c ON so.customer = c.name
        WHERE
            {where_clause}
        GROUP BY
            so.customer, so.customer_name, c.customer_group, soi.item_code, soi.item_name, soi.uom
        ORDER BY
            c.customer_group, so.customer, soi.item_code
    """.format(where_clause=where_clause)

    sales_orders = get_aggregated_data(sales_order_query, params)

    # Check if there are any Sale Orders
    if not sales_orders:
        return columns, []  # Return columns and empty data

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
                c.customer_group,
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
            JOIN
                `tabCustomer` c ON so.customer = c.name
            WHERE
                si.docstatus = 1
                AND si.is_return = 1
                AND si.return_against IS NOT NULL
                AND so.name IN %(sales_orders)s
            GROUP BY
                so.customer, so.customer_name, c.customer_group, sii.item_code, sii.item_name, sii.uom
            ORDER BY
                c.customer_group, so.customer, sii.item_code
        """

        # Combine parameters
        credit_params = {'sales_orders': tuple(sales_order_names)}
        credit_params.update(params)  # Include any additional filters

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

    # Function to process and append rows
    def process_rows(rows, data, grand_totals_key, label=None):
        current_customer_group = None
        current_customer = None
        customer_group_totals = {key: 0 for key in grand_totals[grand_totals_key]}
        customer_totals = {key: 0 for key in grand_totals[grand_totals_key]}
        group_total_items = 0
        customer_total_items = 0

        for row in rows:
            # Switch customer group
            if row.customer_group != current_customer_group:
                if current_customer_group is not None:
                    # Append totals for the last customer in the group
                    if current_customer is not None:
                        data.append({
                            "customer_group": "",
                            "code": "",
                            "customer": "",
                            "product": f"Total {customer_total_items} items for Customer",
                            "uom": "",
                            **customer_totals
                        })
                        customer_totals = {key: 0 for key in grand_totals[grand_totals_key]}
                        customer_total_items = 0
                        current_customer = None

                    # Append customer group totals
                    data.append({
                        "customer_group": "",
                        "code": "",
                        "customer": "",
                        "product": f"Total for Customer Group {current_customer_group} ({group_total_items} items)",
                        "uom": "",
                        **customer_group_totals
                    })
                    customer_group_totals = {key: 0 for key in grand_totals[grand_totals_key]}
                    group_total_items = 0

                # Append new customer group header
                current_customer_group = row.customer_group
                data.append({
                    "customer_group": current_customer_group,
                    "code": "",
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

            # Switch customer
            if row.customer != current_customer:
                if current_customer is not None:
                    # Append customer totals
                    data.append({
                        "customer_group": "",
                        "code": "",
                        "customer": "",
                        "product": f"Total {customer_total_items} items for Customer",
                        "uom": "",
                        **customer_totals
                    })
                    customer_totals = {key: 0 for key in grand_totals[grand_totals_key]}
                    customer_total_items = 0

                # Append new customer header
                current_customer = row.customer
                data.append({
                    "customer_group": "",
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
                "customer_group": "",
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

            # Update totals
            for key in grand_totals[grand_totals_key]:
                val = row.get(key, 0) or 0
                customer_totals[key] += val
                customer_group_totals[key] += val
                grand_totals[grand_totals_key][key] += val
            customer_total_items += 1
            group_total_items += 1

        # Append totals for the last customer and customer group
        if current_customer is not None:
            data.append({
                "customer_group": "",
                "code": "",
                "customer": "",
                "product": f"Total {customer_total_items} items for Customer",
                "uom": "",
                **customer_totals
            })
        if current_customer_group is not None:
            data.append({
                "customer_group": "",
                "code": "",
                "customer": "",
                "product": f"Total for Customer Group {current_customer_group} ({group_total_items} items)",
                "uom": "",
                **customer_group_totals
            })

    # Initialize report data with Sale Orders header
    data = [{
        "customer_group": "Type : Sale Orders",
        "code": "",
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

    # Process Sale Orders
    process_rows(sales_orders, data, 'sale_order')

    # Append Credit Notes Header
    if credit_notes:
        data.append({
            "customer_group": "Type : Credit Notes",
            "code": "",
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
            "customer_group": label,
            "code": "",
            "customer": "",
            "product": "",
            "uom": "",
            **totals
        })

    append_grand_total(data, grand_totals['sale_order'], "Grand Total Sale Orders")
    append_grand_total(data, grand_totals['credit_note'], "Grand Total Credit Notes")

    # Calculate Net Sales (Sale Orders + Credit Notes)
    net_totals = {}
    for key in grand_totals['sale_order']:
        net_totals[key] = grand_totals['sale_order'][key] + grand_totals['credit_note'][key]

    data.append({
        "customer_group": "Net Sales",
        "code": "",
        "customer": "",
        "product": "",
        "uom": "",
        **net_totals
    })

    return columns, data
