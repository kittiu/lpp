import frappe

def delete_field_from_payment_entry(fieldname):
    try:
        # Check if the column exists in the "Payment Entry" table
        if frappe.db.has_column("Payment Entry", fieldname):
            frappe.db.sql(f"""ALTER TABLE `tabPayment Entry` DROP COLUMN `{fieldname}`;""")
            frappe.db.commit()
            print(f"Successfully dropped column: {fieldname}")
        
        # Delete the Custom Field document if it exists
        if frappe.db.exists('Custom Field', f'Payment Entry-{fieldname}'):
            frappe.delete_doc('Custom Field', f'Payment Entry-{fieldname}')
            frappe.db.commit()
            print(f"Successfully deleted Custom Field: Payment Entry-{fieldname}")
    except frappe.db.DatabaseError as db_err:
        print(f"DatabaseError: Failed to drop column {fieldname} - {str(db_err)}")
    except Exception as e:
        print(f"Error: An unexpected error occurred while deleting field {fieldname} - {str(e)}")

def execute():
    # List of fields to delete
    fields_to_delete = [
                        "custom_no_chequereference_transaction", 
    ]
    
    for field in fields_to_delete:
        delete_field_from_payment_entry(field)

