import frappe

def delete_field_from_item(fieldname):
    """ลบฟิลด์จาก Item และลบ Custom Field ถ้ามี"""
    if frappe.db.has_column("Item", fieldname):
        frappe.db.sql(f"""ALTER TABLE `tabItem` DROP COLUMN `{fieldname}`;""")
    frappe.delete_doc_if_exists('Custom Field', f'Item-{fieldname}')

def execute():
    # ลบฟิลด์ที่ต้องการ
    fields_to_delete = ["custom_scrap_per_run_cards", "custom_scrap_item_per_run_cards"]
    
    for field in fields_to_delete:
        delete_field_from_item(field)
