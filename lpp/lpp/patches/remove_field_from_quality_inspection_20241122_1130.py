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
        "custom_thickness",
        "custom_thickness_plus_or_minus",
        "custom_thickness_max_range",
        "custom_width",
        "custom_width_plus_or_minus",
        "custom_width_min_range",
        "custom_width_max_range",
        "custom_sr_value",
        "custom_sr_value_plus_or_minus",
        "custom_sr_value_max_range",
        "custom_sr_value_min_range",

        "custom_a_reel_diameter_norminal",
        "custom_b_reel_diameter_norminal",
        "custom_c_diameter_norminal",
        "custom_d_diameter_norminal",
        "custom_e_norminal",
        "custom_f_norminal",
        "custom_n_hub_diameter_norminal",
        "custom_w1_norminal",
        "custom_w2_norminal",
        "custom_t_flange_thickness_norminal",
        "custom_sr_value_norminal",
        "custom_a_reel_diameter_plus_or_minus",
        "custom_b_reel_diameter_plus_or_minus",
        "custom_c_reel_diameter_plus_or_minus",
        "custom_d_reel_diameter_plus_or_minus",
        "custom_e_plus_or_minus",
        "custom_f_plus_or_minus",
        "custom_n_hub_diameter_plus_or_minus",
        "custom_w1_hub_diameter_plus_or_minus",
        "custom_w2_hub_diameter_plus_or_minus",
        "custom_t_flange_thickness_plus_or_minus",
        "custom_sr_value_plus_or_minus_2",


    ]
    
    for field in fields_to_delete:
        delete_field_from_quality_inspection(field)


