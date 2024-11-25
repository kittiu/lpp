import frappe

def delete_field_from_employee(fieldname):
    try:
        # Check if the column exists in the "Employee" table
        if frappe.db.has_column("Employee", fieldname):
            frappe.db.sql(f"""ALTER TABLE `tabEmployee` DROP COLUMN `{fieldname}`;""")
            frappe.db.commit()
            print(f"Successfully dropped column: {fieldname}")
        
        # Delete the Custom Field document if it exists
        if frappe.db.exists('Custom Field', f'Employee-{fieldname}'):
            frappe.delete_doc('Custom Field', f'Employee-{fieldname}')
            frappe.db.commit()
            print(f"Successfully deleted Custom Field: Employee-{fieldname}")
    except frappe.db.InternalError as db_err:
        print(f"InternalError: Failed to drop column {fieldname} - {str(db_err)}")
    except Exception as e:
        print(f"Error: An unexpected error occurred while deleting field {fieldname} - {str(e)}")

def execute():
    # List of fields to delete
    fields_to_delete = [
        "custom_column_break_fdtar",
    ]
    
    for field in fields_to_delete:
        delete_field_from_employee(field)


