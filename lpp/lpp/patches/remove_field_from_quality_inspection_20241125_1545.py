import frappe

def delete_field_from_quality_inspection(fieldname):
    try:
        # Check if the column exists in the "Quality Inspection" table
        if frappe.db.has_column("Quality Inspection", fieldname):
            frappe.db.sql(f"""ALTER TABLE `tabQuality Inspection` DROP COLUMN `{fieldname}`;""")
            frappe.db.commit()
            print(f"Successfully dropped column: {fieldname}")
        
        # Delete the Custom Field document if it exists
        if frappe.db.exists('Custom Field', f'Quality Inspection-{fieldname}'):
            frappe.delete_doc('Custom Field', f'Quality Inspection-{fieldname}')
            frappe.db.commit()
            print(f"Successfully deleted Custom Field: Quality Inspection-{fieldname}")
    except frappe.db.InternalError as db_err:
        print(f"InternalError: Failed to drop column {fieldname} - {str(db_err)}")
    except Exception as e:
        print(f"Error: An unexpected error occurred while deleting field {fieldname} - {str(e)}")

def execute():
    # List of fields to delete
    fields_to_delete = [
        "custom_thickness_min_range",
        "custom_column_break_qquir",
        "custom_column_break_sehup",
        "custom_column_break_rpz4z",
        "custom_column_break_lfchv",
        "custom_column_break_l7gls",
        "custom_column_break_gqmnu"
    ]
    
    for field in fields_to_delete:
        delete_field_from_quality_inspection(field)


