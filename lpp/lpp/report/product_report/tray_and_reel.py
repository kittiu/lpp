import frappe
from frappe.query_builder import DocType, Field


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
        {"label": "Workstation", "fieldname": "workstation", "fieldtype": "Link", "options": "Workstation", "width": 150},
        {"label": "Runcard No.", "fieldname": "custom_runcard_no", "fieldtype": "Data", "width": 120},
        {"label": "Work Order", "fieldname": "work_order", "fieldtype": "Link", "options": "Work Order", "width": 150},
        {"label": "Shift", "fieldname": "custom_shift", "fieldtype": "Link", "options": "Shift", "width": 120, "align": "left"},
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
    columns = get_dynamic_columns()

    # สร้างเงื่อนไขการกรอง
    filter_conditions = []
    if filters.get("start_date"):
        filter_conditions.append(["custom_start_date_production", ">=", filters["start_date"]])
    if filters.get("end_date"):
        filter_conditions.append(["custom_end_date_production", "<=", filters["end_date"]])
    if filters.get("workstation"):
        filter_conditions.append(["workstation", "=", filters["workstation"]])
    if filters.get("work_order"):
        filter_conditions.append(["work_order", "=", filters["work_order"]])
    if filters.get("custom_shift"):
        filter_conditions.append(["custom_shift", "=", filters["custom_shift"]])
    if filters.get("production_item"):
        filter_conditions.append(["production_item", "=", filters["production_item"]])
    if filters.get("production_name"):
        filter_conditions.append(["custom_production_item_name", "=", filters["production_name"]])

    # ใช้ Query Builder เพื่อเพิ่มเงื่อนไขแบบ OR สำหรับ custom_item_group_2
    JobCard = DocType("Job Card")
    query = (
        frappe.qb.from_(JobCard)
        .select(
            JobCard.name,
            JobCard.custom_start_date_production,
            JobCard.custom_end_date_production,
            JobCard.workstation,
            JobCard.custom_runcard_no,
            JobCard.work_order,
            JobCard.custom_production_item_name,
            JobCard.custom_input_production,
            JobCard.custom_output_production,
            JobCard.custom_scrap_production,
            JobCard.custom_yield_production,
            JobCard.custom_total_hours_production,
            JobCard.custom_shift,
            JobCard.custom_item_group_2
        )
        .where(
            (Field("custom_item_group_2").not_like("%Carrier%")) &
            (Field("custom_item_group_2").not_like("%Band%"))
        )
    )

    # เพิ่มเงื่อนไขจาก filters อื่น ๆ
    for condition in filter_conditions:
        query = query.where(Field(condition[0]) == condition[2])

    items = query.run(as_dict=True)

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
