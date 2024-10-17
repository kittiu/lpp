import frappe

def delete_field_from_quality_inspection(fieldname):
    try:
        # Check if the column exists and drop it if present
        if frappe.db.has_column("Quality Inspection", fieldname):
            frappe.db.sql(f"""ALTER TABLE `tabQuality Inspection` DROP COLUMN `{fieldname}`;""")
            # Log field deletion
            frappe.logger().info(f"Field '{fieldname}' successfully dropped from Quality Inspection table.")
        else:
            frappe.logger().info(f"Field '{fieldname}' does not exist in Quality Inspection table.")
        
        # Delete the Custom Field document if it exists
        frappe.delete_doc_if_exists('Custom Field', f'Quality Inspection-{fieldname}')
        frappe.logger().info(f"Custom Field '{fieldname}' successfully deleted from Quality Inspection Doctype.")
    
    except Exception as e:
        # Log any errors during the process
        frappe.logger().error(f"Error while deleting field '{fieldname}': {str(e)}")

def execute():
    # ลบฟิลด์ที่ต้องการ
    fields_to_delete = [
        "custom_material_lot_no",
        "custom_inspection_result"
    ]
    
    for field in fields_to_delete:
        delete_field_from_quality_inspection(field)
