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
    fields_to_delete = [
                        "custom_length_tolerance", 
                        "custom_length_max",
                        "custom_length_min",
                        "custom_height_tolerance",
                        "custom_height_max",
                        "custom_height_min",
                        "custom_step_in_cavity",
                        "custom_scrap_item_per_run_cards", 
                        "custom_height_tolerance",
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
