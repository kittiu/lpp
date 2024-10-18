import frappe

def execute():
    # Check if the field exists in the Work Order doctype
    if frappe.db.exists('Custom Field', {'dt': 'Work Order', 'fieldname': 'custom_item_molds'}):
        # Delete the custom field from the Work Order doctype
        frappe.delete_doc('Custom Field', {'dt': 'Work Order', 'fieldname': 'custom_item_molds'}, force=1)
        
        # Commit changes to the database
        frappe.db.commit()
