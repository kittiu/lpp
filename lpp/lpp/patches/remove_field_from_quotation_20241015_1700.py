import frappe

def execute():
    # ระบุชื่อของ Custom Field ที่ต้องการลบ
    field_name = "custom_customer_groups"
    doctype = "Quotation"
    # ตรวจสอบว่าฟิลด์มีอยู่หรือไม่
    if frappe.db.exists("Custom Field", {"fieldname": field_name, "dt": doctype}):
        frappe.delete_doc("Custom Field", f"{doctype}-{field_name}", force=True)
        frappe.db.commit()  # บันทึกการเปลี่ยนแปลง
    else:
        frappe.log(f"Field '{field_name}' not found in Doctype '{doctype}'")