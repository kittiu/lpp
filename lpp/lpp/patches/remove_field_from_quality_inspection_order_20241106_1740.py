import frappe

def delete_field_from_quality_inspection_order(fieldname):
    try:
        # Check if the column exists and drop it if present
        if frappe.db.has_column("Quality Inspection Order", fieldname):
            frappe.db.sql(f"""ALTER TABLE `tabQuality Inspection Order` DROP COLUMN `{fieldname}`;""")
            # Log field deletion
            frappe.logger().info(f"Field '{fieldname}' successfully dropped from Quality Inspection Order table.")
        else:
            frappe.logger().info(f"Field '{fieldname}' does not exist in Quality Inspection Order table.")
        
        # Delete the Custom Field document if it exists
        frappe.delete_doc_if_exists('Custom Field', f'Quality Inspection Order-{fieldname}')
        frappe.logger().info(f"Custom Field '{fieldname}' successfully deleted from Quality Inspection Order Doctype.")
    
    except Exception as e:
        # Log any errors during the process
        frappe.logger().error(f"Error while deleting field '{fieldname}': {str(e)}")

def execute():
    # ลบฟิลด์ที่ต้องการ
    fields_to_delete = [
        "tolerance_max",
        "tolerance_min"
    ]
    
    for field in fields_to_delete:
        delete_field_from_quality_inspection_order(field)
