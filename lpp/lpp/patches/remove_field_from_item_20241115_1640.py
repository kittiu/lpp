import frappe

def delete_field_from_item(fieldname):
    try:
        # Check if the column exists in the "Item" table
        if frappe.db.has_column("Item", fieldname):
            frappe.db.sql(f"""ALTER TABLE `tabItem` DROP COLUMN `{fieldname}`;""")
            frappe.db.commit()
            print(f"Successfully dropped column: {fieldname}")
        
        # Delete the Custom Field document if it exists
        if frappe.db.exists('Custom Field', f'Item-{fieldname}'):
            frappe.delete_doc('Custom Field', f'Item-{fieldname}')
            frappe.db.commit()
            print(f"Successfully deleted Custom Field: Item-{fieldname}")
    except frappe.db.DatabaseError as db_err:
        print(f"DatabaseError: Failed to drop column {fieldname} - {str(db_err)}")
    except Exception as e:
        print(f"Error: An unexpected error occurred while deleting field {fieldname} - {str(e)}")

def execute():
    # List of fields to delete
    fields_to_delete = [
                        "custom_thickness_tolerance", 
                        "custom_thickness_max",
                        "custom_thickness_min",
                        "custom_width_tolerance",
                        "custom_width_max",
                        "custom_width_min",
                        "custom_surface_resistivity_ohmssq",
                        "custom_surface_resistivity_ohmssq_max", 
                        "custom_surface_resistivity_ohmssq_min",
                        "custom_pockets",
                        "custom_b_tolerance",
                        "custom_b_max",
                        "custom_b_min",
                        "custom_e_tolerance",
                        "custom_e_max",
                        "custom_e_min",
                        "custom_f_tolerance",
                        "custom_f_max",
                        "custom_f_min",    
                        "custom_length_tolerance", 
                        "custom_length_max",
                        "custom_length_min",
                        "custom_height_tolerance",
                        "custom_height_max",
                        "custom_height_min",
                        "custom_step_in_cavity",
                        "custom_scrap_item_per_run_cards", 
                        "custom_thickness",
                        "custom_thickness_range_plus_or_minus",
                        "custom_width",
                        "custom_width_plus_or_minus",
                        "custom_sr_value",
                        "custom_sr_value_plus_or_minus",
                        "custom_thickness_range_min",
                        "custom_thickness_range_max",
                        "custom_width_range_min",
                        "custom_width_range_max",
                        "custom_sr_value_min",
                        "custom_sr_value_max",
                        "custom_a_reel_diameter",
                        "custom_b_width",
                        "custom_c_diameter",
                        "custom_d_diameter",
                        "custom_e",
                        "custom_f",
                        "custom_n_hub_diameter",
                        "custom_w1",
                        "custom_w2",
                        "custom_t_flange_thickness",
                        "custom_a_reel_diameter_plus_or_minus",
                        "custom_b_width_plus_or_minus",
                        "custom_c_diameter_plus_or_minus",
                        "custom_d_diameter_plus_or_minus",
                        "custom_e_plus_or_minus",
                        "custom_f_plus_or_minus",
                        "custom_n_hub_diameter_plus_or_minus",
                        "custom_w1_plus_or_minus",
                        "custom_w2_plus_or_minus",
                        "custom_t_flange_thickness_plus_or_minus",
    ]
    
    for field in fields_to_delete:
        delete_field_from_item(field)

