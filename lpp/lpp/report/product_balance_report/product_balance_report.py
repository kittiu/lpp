# Import required libraries
import frappe
from frappe import _
from erpnext.stock.report.stock_balance.stock_balance import execute as stock_balance_execute

def execute(filters=None):
    # Define the columns for the report
    columns = get_columns()
    
    # Get the data and apply necessary grouping and calculations
    data = get_data(filters)

    # Return the columns and data for rendering the report
    return columns, data

# Define the columns to be displayed in the report
def get_columns():
    return [
        {"label": _("รหัสสินค้า (Product Code)"), "fieldname": "item_code", "fieldtype": "Data", "width": 250},
        {"label": _("ชื่อสินค้า (Product Name)"), "fieldname": "item_name", "fieldtype": "Data", "width": 200},
        {"label": _("หน่วยนับ (Unit)"), "fieldname": "stock_uom", "fieldtype": "Data", "width": 150},
        {"label": _("ยอดคงเหลือ (Balance)"), "fieldname": "bal_qty", "fieldtype": "Float", "width": 150},
        {"label": _("มูลค่าต่อหน่วย (Unit Price)"), "fieldname": "val_rate", "fieldtype": "Currency", "width": 150},
        {"label": _("รวมมูลค่า (Total)"), "fieldname": "bal_val", "fieldtype": "Currency", "width": 150},
    ]

# Process and group the data, then return it for the report
def get_data(filters):
    data = []

    # Execute the stock balance function and get the stock data
    stock_balance = stock_balance_execute(filters)

    if not stock_balance:
        return data

    stock_balance_data = stock_balance[1]  # Get the actual data part of the result

    # A dictionary to accumulate data per warehouse and item group
    warehouse_grouped_data = {}

    # Process each row in the stock data
    for row in stock_balance_data:
        warehouse = row.get('warehouse')
        item_group = row.get('item_group')

        # Initialize the warehouse group if not already done
        if warehouse not in warehouse_grouped_data:
            warehouse_grouped_data[warehouse] = {}

        # Initialize the item group inside the warehouse group if not already done
        if item_group not in warehouse_grouped_data[warehouse]:
            warehouse_grouped_data[warehouse][item_group] = {
                'items': [],
                'total_bal_val': 0
            }

        # Add the item to the respective item group and accumulate the bal_val
        warehouse_grouped_data[warehouse][item_group]['items'].append(row)
        warehouse_grouped_data[warehouse][item_group]['total_bal_val'] += row.get('bal_val', 0)

    # Process the grouped data to generate the final output
    for warehouse, item_groups in warehouse_grouped_data.items():
        # Add a row to indicate the start of a warehouse group
        data.append({
            'item_code': "คลังสินค้า",
            'item_name': warehouse,
            'stock_uom': '',
            'bal_qty': None,
            'val_rate': None,
            'bal_val': None
        })

        warehouse_total_bal_val = 0  # Accumulate total balance value per warehouse

        for item_group, group_data in item_groups.items():
            # Add a row to indicate the start of an item group within the warehouse
            data.append({
                'item_code': f"Product Group: {item_group}",
                'item_name': '',
                'stock_uom': '',
                'bal_qty': None,
                'val_rate': None,
                'bal_val': None
            })

            # Add all the items in this item group
            data.extend(group_data['items'])

            # Add a row for the cost per item group
            data.append({
                'item_code': f"Cost Per Group: {item_group}",
                'item_name': '',
                'stock_uom': '',
                'bal_qty': None,
                'val_rate': None,
                'bal_val': group_data['total_bal_val']
            })

            # Accumulate the total balance value for the warehouse
            warehouse_total_bal_val += group_data['total_bal_val']

        # After all item groups, add a row for the total cost per warehouse
        data.append({
            'item_code': f"Cost Per Warehouse: {warehouse}",
            'item_name': '',
            'stock_uom': '',
            'bal_qty': None,
            'val_rate': None,
            'bal_val': warehouse_total_bal_val
        })

    return data
