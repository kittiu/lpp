import frappe

def delete_field_from_delivery_note(fieldname):
    try:
        # Check if the column exists in the "Delivery Note" table
        if frappe.db.has_column("Delivery Note", fieldname):
            frappe.db.sql(f"""ALTER TABLE `tabDelivery Note` DROP COLUMN `{fieldname}`;""")
            frappe.db.commit()
            print(f"Successfully dropped column: {fieldname}")
        
        # Delete the Custom Field document if it exists
        if frappe.db.exists('Custom Field', f'Delivery Note-{fieldname}'):
            frappe.delete_doc('Custom Field', f'Delivery Note-{fieldname}')
            frappe.db.commit()
            print(f"Successfully deleted Custom Field: Delivery Note-{fieldname}")
    except frappe.db.InternalError as db_err:
        print(f"InternalError: Failed to drop column {fieldname} - {str(db_err)}")
    except Exception as e:
        print(f"Error: An unexpected error occurred while deleting field {fieldname} - {str(e)}")

def execute():
    # List of fields to delete
    fields_to_delete = [
        "custom_supplier_purchase_order",
    ]
    
    for field in fields_to_delete:
        delete_field_from_delivery_note(field)


