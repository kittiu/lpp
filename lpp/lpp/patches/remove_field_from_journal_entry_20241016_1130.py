import frappe

def delete_field_from_journal_entry(fieldname):
    try:
        # Check if the column exists and drop it if present
        if frappe.db.has_column("Journal Entry", fieldname):
            frappe.db.sql(f"""ALTER TABLE `tabJournal Entry` DROP COLUMN `{fieldname}`;""")
            # Log field deletion
            frappe.logger().info(f"Field '{fieldname}' successfully dropped from Journal Entry table.")
        else:
            frappe.logger().info(f"Field '{fieldname}' does not exist in Journal Entry table.")
        
        # Delete the Custom Field document if it exists
        frappe.delete_doc_if_exists('Custom Field', f'Journal Entry-{fieldname}')
        frappe.logger().info(f"Custom Field '{fieldname}' successfully deleted from Journal Entry Doctype.")
    
    except Exception as e:
        # Log any errors during the process
        frappe.logger().error(f"Error while deleting field '{fieldname}': {str(e)}")

def execute():
    # ลบฟิลด์ที่ต้องการ
    fields_to_delete = [
        "custom_party_type",
        "custom_party"
    ]
    
    for field in fields_to_delete:
        delete_field_from_journal_entry(field)
