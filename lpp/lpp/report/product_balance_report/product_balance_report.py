# Import required libraries
import frappe
from frappe import _
from erpnext.stock.report.stock_balance.stock_balance import execute as stock_balance_execute

def execute(filters=None):
    # Define the columns for the report
    columns = get_columns()
    
    # Get the data and apply necessary grouping and sorting
    data = get_data(filters)

    # Return the columns and sorted data for rendering the report
    return columns, data

# Define the columns to be displayed in the report
def get_columns():
    return [
        {"label": _("รหัสสินค้า (Product Code)"), "fieldname": "item_code", "fieldtype": "Data", "width": 250},
        {"label": _("ชื่อสินค้า (Product Name)"), "fieldname": "item_name", "fieldtype": "Data", "width": 250},
        {"label": _("หน่วยนับ (Unit)"), "fieldname": "stock_uom", "fieldtype": "Data", "width": 100},
        {"label": _("ยอดคงเหลือ (Balance)"), "fieldname": "bal_qty", "fieldtype": "Float", "width": 150},
        {"label": _("มูลค่าต่อหน่วย (Unit Price)"), "fieldname": "val_rate", "fieldtype": "Currency", "width": 150},
        {"label": _("รวมมูลค่า (Total)"), "fieldname": "bal_val", "fieldtype": "Currency", "width": 150},
    ]

# Process, group, and sort the data, then return it for the report
def get_data(filters):
    # Execute the stock balance function and get the stock data
    stock_balance = stock_balance_execute(filters)

    # If there's no data, return an empty list
    if not stock_balance:
        return []

    # Get the actual stock balance data
    stock_balance_data = stock_balance[1]

    # Dictionary to store data grouped by warehouse and item group
    warehouse_grouped_data = {}

    # Process each row in the stock data
    for row in stock_balance_data:
        warehouse = row.get('warehouse')
        item_group = row.get('item_group')

        # Use setdefault to initialize nested dictionaries in one line
        group = warehouse_grouped_data.setdefault(warehouse, {}).setdefault(item_group, {
            'items': [],
            'total_bal_val': 0
        })

        # Append the item to the group and accumulate the bal_val
        group['items'].append(row)
        group['total_bal_val'] += row.get('bal_val', 0)

    # Final data to return
    data = []

    # Process the grouped data for output and sorting
    for warehouse, item_groups in warehouse_grouped_data.items():
        # Add warehouse group row
        data.append({
            'item_code': "คลังสินค้า",  # "Warehouse"
            'item_name': warehouse,
            'stock_uom': '',
            'bal_qty': None,
            'val_rate': None,
            'bal_val': None
        })

        # Variable to store total value for the warehouse
        warehouse_total_bal_val = 0

        # Sort item groups by item_group name
        sorted_item_groups = sorted(item_groups.items(), key=lambda x: x[0])

        for item_group, group_data in sorted_item_groups:
            # Add item group row
            data.append({
                'item_code': f"Product Group: {item_group}",
                'item_name': '',
                'stock_uom': '',
                'bal_qty': None,
                'val_rate': None,
                'bal_val': None
            })

            # Sort items within the group by item_code
            sorted_items = sorted(group_data['items'], key=lambda x: x['item_code'])
            
            # Add all sorted items in the current item group
            data.extend(sorted_items)

            # Add cost per item group
            data.append({
                'item_code': f"Cost Per Group: {item_group}",
                'item_name': '',
                'stock_uom': '',
                'bal_qty': None,
                'val_rate': None,
                'bal_val': group_data['total_bal_val']
            })

            # Accumulate total balance value for the warehouse
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
