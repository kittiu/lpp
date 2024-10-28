# Copyright (c) 2024, Ecosoft and contributors
# For license information, please see license.txt

import frappe

@frappe.whitelist()
def get_dynamic_columns():
    # ดึงชื่อ custom_defect ทั้งหมดและกำจัดรายการซ้ำ
    custom_defects = frappe.db.sql("""
        SELECT DISTINCT custom_defect
        FROM `tabJob Card Scrap Item`
    """, as_dict=True)

    # สร้างคอลัมน์พื้นฐาน
    columns = [
        {"label": "Date", "fieldname": "custom_start_date_production", "fieldtype": "Date", "width": 120},
        {"label": "Workstation", "fieldname": "workstation", "fieldtype": "Link", "options": "Workstation", "width": 120},
        {"label": "Runcard No.", "fieldname": "custom_runcard_no", "fieldtype": "Data", "width": 120},
        {"label": "Work Order", "fieldname": "work_order", "fieldtype": "Link", "options": "Work Order", "width": 150},
        {"label": "Product Name", "fieldname": "custom_production_item_name", "fieldtype": "Data", "width": 250},
        {"label": "IN", "fieldname": "custom_input_production", "fieldtype": "Float", "width": 100},
        {"label": "OUT", "fieldname": "custom_output_production", "fieldtype": "Float", "width": 100},
        {"label": "NG", "fieldname": "custom_scrap_production", "fieldtype": "Float", "width": 100},
        {"label": "%YIELD", "fieldname": "custom_yield_production", "fieldtype": "Float", "width": 100},
        {"label": "Working Hours", "fieldname": "custom_total_hours_production", "fieldtype": "Float", "width": 130},
    ]

    # เพิ่มคอลัมน์ตาม custom_defect ที่มีอยู่
    for defect in custom_defects:
        columns.append({
            "label": defect["custom_defect"],
            "fieldname": f"defect_{defect['custom_defect']}",  # fieldname สร้างโดยใช้ custom_defect
            "fieldtype": "Float",
            "width": 150
        })

    return columns

def tray_and_reel(filters=None):
    if not filters:
        filters = {}

    columns = get_dynamic_columns()

    # ดึงข้อมูล Job Card
    items = frappe.db.get_all(
        "Job Card",
        fields=[
            "name",  # เพื่อใช้ในการเชื่อมกับ Job Card Scrap Item
            "custom_start_date_production",
            "custom_end_date_production",
            "workstation",
            "custom_runcard_no",
            "work_order",
            "custom_production_item_name",
            "custom_input_production",
            "custom_output_production",
            "custom_scrap_production",
            "custom_yield_production",
			"custom_total_hours_production"
        ],
        # filters=filters,
        order_by="custom_production_item_name"
    )

    # ดึงข้อมูล Defect จาก Job Card Scrap Item และจัดเก็บตาม Job Card แต่ละตัว
    scrap_items = frappe.db.get_all(
        "Job Card Scrap Item",
        fields=["parent", "custom_defect", "stock_qty"],
        filters={"parent": ["in", [item["name"] for item in items]]}
    )

    # จัดกลุ่ม defect data ตาม parent (Job Card)
    scrap_item_map = {}
    for scrap in scrap_items:
        if scrap["parent"] not in scrap_item_map:
            scrap_item_map[scrap["parent"]] = {}
        # เก็บค่า stock_qty ตาม custom_defect
        scrap_item_map[scrap["parent"]][scrap["custom_defect"]] = scrap["stock_qty"]

    # สร้างข้อมูลสำหรับแสดงในรายงาน
    data = []
    current_product_name = None
    group_totals = {}

    for item in items:
        row = item.copy()
        product_name = item["custom_production_item_name"]

        # ถ้าเริ่มกลุ่มใหม่และมีผลรวมของกลุ่มก่อนหน้า ให้เพิ่มแถวสรุปผลรวมของกลุ่มก่อนหน้า
        if current_product_name and current_product_name != product_name:
            summary_row = {
                "custom_production_item_name": f"Total for {current_product_name}",
                "custom_start_date_production": None,
                "workstation": None,
                "custom_runcard_no": None,
                "work_order": None,
                "custom_yield_production": group_totals.get("custom_yield_production", 0),  # เฉพาะแถวสรุป
            }
            summary_row.update(group_totals)
            data.append(summary_row)

            # รีเซ็ตผลรวมกลุ่มใหม่
            group_totals = {}

        # อัปเดตค่า current_product_name
        current_product_name = product_name

        # เพิ่มค่า defect ในคอลัมน์ที่เกี่ยวข้อง
        if item["name"] in scrap_item_map:
            for defect, qty in scrap_item_map[item["name"]].items():
                fieldname = f"defect_{defect}"  # ใช้ชื่อฟิลด์ที่ตรงกับคอลัมน์ defect ที่สร้าง
                row[fieldname] = qty
                group_totals[fieldname] = group_totals.get(fieldname, 0) + qty

        # บันทึกผลรวมตามฟิลด์อื่น ๆ สำหรับแต่ละกลุ่ม และกำหนด custom_yield_production เป็น None
        for field in ["custom_input_production", "custom_output_production", "custom_scrap_production", "custom_total_hours_production"]:
            group_totals[field] = group_totals.get(field, 0) + float(row[field] or 0)

        # ตั้งค่า custom_yield_production เป็น None สำหรับแถวปกติ
        row["custom_yield_production"] = None

        # เพิ่ม row ปัจจุบันใน data
        data.append(row)

    # เพิ่มแถวผลรวมสำหรับกลุ่มสุดท้าย
    if group_totals:
        summary_row = {
            "custom_production_item_name": f"Total for {current_product_name}",
            "custom_start_date_production": None,
            "workstation": None,
            "custom_runcard_no": None,
            "work_order": None,
            "custom_yield_production": group_totals.get("custom_yield_production", 0),  # เฉพาะแถวสรุป
        }
        summary_row.update(group_totals)
        data.append(summary_row)

    return columns, data









