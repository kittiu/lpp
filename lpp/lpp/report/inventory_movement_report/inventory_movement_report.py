import frappe
from frappe.utils import flt

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    total_transactions = count_transactions(data)  # นับจำนวนแถวรายการทั้งหมดที่ไม่ใช่แถวชื่อกลุ่มหรือสรุปกลุ่ม
    total_summary = get_total_summary(total_transactions)  # ส่งจำนวนรายการที่ไม่ใช่แถวชื่อกลุ่มไปยังฟังก์ชัน get_total_summary
    data.append(total_summary)  # เพิ่มแถวสรุปสุดท้ายที่สรุปจำนวนรายการทั้งหมด
    return columns, data

def get_columns():
    return [
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Data", "width": 180},
        {"label": "ID", "fieldname": "name", "fieldtype": "Link", "options": "Stock Entry", "width": 200},
        {"label": "In Qty", "fieldname": "in_qty", "fieldtype": "Float", "width": 120},
        {"label": "Out Qty", "fieldname": "out_qty", "fieldtype": "Float", "width": 120},
        {"label": "UOM", "fieldname": "uom", "fieldtype": "Data", "width": 90},
        {"label": "Actual Qty", "fieldname": "actual_qty", "fieldtype": "Float", "width": 100},
        {"label": "Remarks", "fieldname": "remarks", "fieldtype": "Data", "width": 200},
        {"label": "Warehouse", "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 200}
    ]

def get_data(filters):
    conditions = ""
    
    if filters.get("from_date"):
        conditions += " AND se.posting_date >= %(from_date)s"
    
    if filters.get("to_date"):
        conditions += " AND se.posting_date <= %(to_date)s"
    
    stock_entries = frappe.db.sql("""
        SELECT 
            se.name, se.posting_date, se.remarks,
            sed.qty, sed.uom, sed.actual_qty, sed.s_warehouse, sed.t_warehouse
        FROM 
            `tabStock Entry` se
        INNER JOIN 
            `tabStock Entry Detail` sed ON se.name = sed.parent
        WHERE 
            se.docstatus = 1 {conditions}
        ORDER BY 
            sed.s_warehouse ASC, sed.t_warehouse ASC, se.posting_date DESC
    """.format(conditions=conditions), filters, as_dict=True)
    
    data = []
    current_group = None
    group_in_qty = 0
    group_out_qty = 0
    group_actual_qty = 0

    for entry in stock_entries:
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
        
        # Check if we are in a new group
        if current_group is None or group_key != current_group:
            if current_group:
                # Add summary row for the previous group
                data.append(get_group_summary(current_group, group_in_qty, group_out_qty, group_actual_qty))

            # Reset the group totals
            current_group = group_key
            group_in_qty = 0
            group_out_qty = 0
            group_actual_qty = 0
            
            # Add row to display the group name
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

        # Update the group totals
        group_in_qty += in_qty
        group_out_qty += out_qty
        group_actual_qty = entry.actual_qty  # Keep the latest actual_qty for this group

    # Add the final group summary
    if current_group:
        data.append(get_group_summary(current_group, group_in_qty, group_out_qty, group_actual_qty))
    
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
    # Create a row that shows the group name (Warehouse name) before listing the transactions
    return {
        "posting_date": "Warehouse Group: {}".format(group_key),
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
    return len([row for row in data if row.get('name')])

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
