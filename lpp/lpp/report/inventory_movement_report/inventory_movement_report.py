import frappe
from frappe.utils import flt

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    total_transactions = count_transactions(data)  # นับจำนวนแถวรายการทั้งหมดที่ไม่ใช่แถวชื่อ item หรือสรุปกลุ่ม
    total_summary = get_total_summary(total_transactions)  # ส่งจำนวนรายการทั้งหมดไปยังฟังก์ชัน get_total_summary
    data.append(total_summary)  # เพิ่มแถวสรุปสุดท้ายที่สรุปจำนวนรายการทั้งหมด
    return columns, data

def get_columns():
    return [
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Data", "width": 230},
        {"label": "ID", "fieldname": "name", "fieldtype": "Link", "options": "Stock Entry", "width": 280},
        {"label": "In Qty", "fieldname": "in_qty", "fieldtype": "Float", "width": 120},
        {"label": "Out Qty", "fieldname": "out_qty", "fieldtype": "Float", "width": 120},
        {"label": "UOM", "fieldname": "uom", "fieldtype": "Data", "width": 90},
        {"label": "Actual Qty", "fieldname": "actual_qty", "fieldtype": "Float", "width": 100},
        {"label": "Remarks", "fieldname": "remarks", "fieldtype": "Data", "width": 150},
        {"label": "Warehouse", "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 180}
    ]

def get_data(filters):
    conditions = ""

    # Filter by item_name
    if filters.get("item_name"):
        conditions += " AND wo.production_item = %(item_name)s"
    
    # Filter by date range
    if filters.get("from_date"):
        conditions += " AND se.posting_date >= %(from_date)s"
    
    if filters.get("to_date"):
        conditions += " AND se.posting_date <= %(to_date)s"
    
    # Filter by warehouse
    if filters.get("warehouse"):
        conditions += " AND (sed.s_warehouse = %(warehouse)s OR sed.t_warehouse = %(warehouse)s)"
    
    stock_entries = frappe.db.sql("""
        SELECT 
            se.name, se.posting_date, se.remarks, se.work_order,
            sed.qty, sed.uom, sed.actual_qty, sed.s_warehouse, sed.t_warehouse, 
            COALESCE(wo.production_item, '-') as production_item,
            COALESCE(wo.item_name, '-') as item_name,
            CASE WHEN wo.item_name is null THEN '-'
            ELSE CONCAT(wo.item_name, " (", wo.production_item, ") ") END as item_full_name
        FROM 
            `tabStock Entry` se
        INNER JOIN 
            `tabStock Entry Detail` sed ON se.name = sed.parent
        LEFT JOIN 
            `tabWork Order` wo ON se.work_order = wo.name
        WHERE 
            se.docstatus = 1 {conditions}
        ORDER BY 
            wo.production_item ASC, sed.s_warehouse ASC, sed.t_warehouse ASC, se.posting_date DESC
    """.format(conditions=conditions), filters, as_dict=True)
    
    data = []
    current_item = None
    current_group = None
    group_in_qty = 0
    group_out_qty = 0
    group_actual_qty = 0
    item_transaction_count = 0  # ใช้สำหรับนับจำนวนรายการในกลุ่ม item_name

    for entry in stock_entries:
        item_name = entry.item_name
        item_full_name = entry.item_full_name
        group_key = entry.s_warehouse or entry.t_warehouse
        in_qty = 0
        out_qty = 0
        
        # Logic to set In Qty and Out Qty
        if entry.s_warehouse and not entry.t_warehouse:
            in_qty = entry.qty
        elif entry.t_warehouse and not entry.s_warehouse:
            out_qty = entry.qty
        elif entry.t_warehouse and entry.s_warehouse:
            in_qty = entry.qty
        
        # Check if we are in a new item group
        if current_item is None or item_name != current_item:
            if current_item:
                # Add summary row for the previous warehouse group within the current item
                data.append(get_group_summary(current_group, group_in_qty, group_out_qty, group_actual_qty))
                # Add summary row for the previous item group with the count of transactions
                data.append(get_item_transaction_summary(current_item, item_transaction_count))

            # Reset the group and item totals for the new item
            current_item = item_name
            current_group = None
            item_transaction_count = 0  # Reset count for new item group
            group_in_qty = 0
            group_out_qty = 0
            group_actual_qty = 0
            
            # Add row to display the item name
            data.append(get_item_name_row(item_full_name))

        # Check if we are in a new warehouse group within the current item
        if current_group is None or group_key != current_group:
            if current_group:
                # Add summary row for the previous warehouse group
                data.append(get_group_summary(current_group, group_in_qty, group_out_qty, group_actual_qty))

            # Reset the group totals for the new warehouse group
            current_group = group_key
            group_in_qty = 0
            group_out_qty = 0
            group_actual_qty = 0
            
            # Add row to display the warehouse group name
            data.append(get_group_name_row(current_group))

        # Add the current entry to the data
        data.append({
            "posting_date": entry.posting_date,
            "name": entry.name,
            "in_qty": in_qty,
            "out_qty": out_qty,
            "uom": entry.uom,
            "actual_qty": entry.actual_qty,
            "warehouse": entry.s_warehouse or entry.t_warehouse,  # Warehouse column shows either s_warehouse or t_warehouse
            "remarks": entry.remarks
        })

        # Update the group totals and item transaction count
        group_in_qty += in_qty
        group_out_qty += out_qty
        group_actual_qty = entry.actual_qty  # Keep the latest actual_qty for this group
        item_transaction_count += 1  # Increase count for each transaction

    # Add the final group summary and item summary
    if current_group:
        data.append(get_group_summary(current_group, group_in_qty, group_out_qty, group_actual_qty))
    if current_item:
        data.append(get_item_transaction_summary(current_item, item_transaction_count))
    
    return data

def get_group_summary(group_key, in_qty, out_qty, actual_qty):
    return {
        "posting_date": "จำนวนรวม",
        "name": "",
        "in_qty": in_qty,
        "out_qty": out_qty,
        "uom": "",
        "actual_qty": actual_qty,
        "warehouse": "",  # Display the group_key as the warehouse for summary
        "remarks": ""
    }

def get_group_name_row(group_key):
    # Create a row that shows the warehouse group name before listing the transactions
    return {
        "posting_date": "Warehouse : {}".format(group_key),
        "name": "",
        "in_qty": None,
        "out_qty": None,
        "uom": "",
        "actual_qty": None,
        "warehouse": "",
        "remarks": ""
    }

def get_item_name_row(item_name):
    # Create a row that shows the item name (from work order) before listing the transactions
    return {
        "posting_date": "ชื่อสินค้า/วัตถุดิบยอดยกมา",
        "name": "{}".format(item_name),  # Show item_name in the ID column
        "in_qty": None,
        "out_qty": None,
        "uom": "",
        "actual_qty": None,
        "warehouse": "",
        "remarks": ""
    }

def get_item_transaction_summary(item_name, transaction_count):
    # Create a summary row for the item group, showing the number of transactions
    return {
        "posting_date": "จำนวนรายการ : {}".format(transaction_count),  # Show count of transactions in the item group
        "name": "",
        "in_qty": None,
        "out_qty": None,
        "uom": "",
        "actual_qty": None,
        "warehouse": "",
        "remarks": ""
    }

def count_transactions(data):
    # นับจำนวนรายการทั้งหมด ยกเว้นแถวที่เป็นชื่อกลุ่มหรือสรุปกลุ่ม
    return len([row for row in data if row.get('warehouse')])

def get_total_summary(total_transactions):
    # Create a total summary row that shows the number of transactions
    return {
        "posting_date": "จำนวนรายการทั้งหมด {}".format(total_transactions),  # Show the total number of rows in Posting Date column
        "name": "",
        "in_qty": None,
        "out_qty": None,
        "uom": "",
        "actual_qty": None,
        "warehouse": "",
        "remarks": ""
    }
