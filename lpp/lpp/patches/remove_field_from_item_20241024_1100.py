import frappe

def delete_field_from_item(fieldname):
    try:
        # Check if the column exists and drop it if present
        if frappe.db.has_column("Item", fieldname):
            frappe.db.sql(f"""ALTER TABLE `tabItem` DROP COLUMN `{fieldname}`;""")
            # Log field deletion
            frappe.logger().info(f"Field '{fieldname}' successfully dropped from Item table.")
        else:
            frappe.logger().info(f"Field '{fieldname}' does not exist in Item table.")
        
        # Delete the Custom Field document if it exists
        frappe.delete_doc_if_exists('Custom Field', f'Item-{fieldname}')
        frappe.logger().info(f"Custom Field '{fieldname}' successfully deleted from Item Doctype.")
    
    except Exception as e:
        # Log any errors during the process
        frappe.logger().error(f"Error while deleting field '{fieldname}': {str(e)}")

def execute():
    # ลบฟิลด์ที่ต้องการ
    fields_to_delete = ["custom_length_tolerance", 
                        "custom_length_max",
                        "custom_length_min",
                        "custom_height_tolerance",
                        "custom_height_max",
                        "custom_height_min",
                        "custom_step_in_cavity",
                    ]
    
    for field in fields_to_delete:
        delete_field_from_item(field)
