frappe.ui.form.on("Item", {
    refresh: function (frm) {
        frm.set_df_property('item_code', 'reqd', 0);
        frm.set_df_property('item_code', 'hidden', 1);
    },
    item_group(frm) {
        if (frm.doc.item_group) {
            if (frm.doc.item_group == "Sales Products" || frm.doc.item_group == "Products") {
                frm.set_value("has_batch_no", 1);
            }
            else if (frm.doc.item_group == "Raw Material" || frm.doc.item_group == "Raw Materials") {
                frm.set_value("has_batch_no", 1);
            } else {
                frm.set_value("has_batch_no", 0);
            }
        }

        // default warehouse in table item_defaults
        if (['Raw Material', 'Raw Materials'].includes(frm.doc.item_group)) {
            frm.doc.item_defaults.forEach(row => {
                row.default_warehouse = frm.doc.item_group
            });
            frm.refresh_field("item_defaults");
        }
    },

    custom_item_group_2: function (frm) {
        frm.events.reset_specifications_tolerance(frm);
    },

    reset_specifications_tolerance: function(frm) {
        const fieldsToReset = {
            'thermoformed_tray': [
                'custom_thickness_thermoformed_tray', 'custom_thickness_max_thermoformed_tray', 'custom_thickness_min_thermoformed_tray',
                'custom_width_in_thermoformed_tray', 'custom_width_in_max_thermoformed_tray', 'custom_width_in_min_thermoformed_tray',
                'custom_a_basic', 'custom_a_basic_max', 'custom_a_basic_min',
                'custom_b_thermoformed_tray', 'custom_b_max_thermoformed_tray', 'custom_b_min_thermoformed_tray',
                'custom_c_basic', 'custom_c_basic_max', 'custom_c_basic_min',
                'custom_d_basic', 'custom_d_basic_max', 'custom_d_basic_min',
                'custom_e_thermoformed_tray', 'custom_e_max_thermoformed_tray', 'custom_e_min_thermoformed_tray',
                'custom_f_thermoformed_tray', 'custom_f_max_thermoformed_tray', 'custom_f_min_thermoformed_tray',
                'custom_g_tolerance', 'custom_g_max', 'custom_g_min',
                'custom_h_tolerance', 'custom_h_max', 'custom_h_min',
                'custom_i_tolerance', 'custom_i_max', 'custom_i_min',
                'custom_j_tolerance', 'custom_j_max', 'custom_j_min',
                'custom_k_tolerance', 'custom_k_max', 'custom_k_min',
                'custom_surface_resistance_ohms_thermoformed_tray', 'custom_surface_resistance_ohms_thermoformed_tray_max', 'custom_surface_resistance_ohms_thermoformed_tray_min'
            ],
            'carrier_tape': [
                "custom_a0_tolerance", "custom_a0_max", "custom_a0_min",
                "custom_b0_tolerance", "custom_b0_max", "custom_b0_min",
                "custom_k0_tolerance", "custom_k0_max", "custom_k0_min",
                "custom_p1_tolerance", "custom_p1_max", "custom_p1_min",
                "custom_thickness_tolerance_carrier_tape", "custom_thickness_max_carrier_tape", "custom_thickness_min_carrier_tape",
                "custom_width_in_carrier_tape", "custom_width_in_max_carrier_tape", "custom_width_in_min_carrier_tape",
                "custom_length__reel_tolerance", "custom_length__reel_max", "custom_length__reel_min",
                "custom_surface_resistance_ohms_carrier_tape", "custom_surface_resistance_ohms_carrier_tape_max", "custom_surface_resistance_ohms_carrier_tape_min",
                "custom_step_in_pocket"
            ],
            'plastic_reel': [
                "custom_a_tolerance", "custom_a_max", "custom_a_min",
                "custom_n_tolerance", "custom_n_max", "custom_n_min",
                "custom_b_plastic_reel", "custom_b_max_plastic_reel", "custom_b_min_plastic_reel",
                "custom_c_tolerance", "custom_c_max", "custom_c_min",
                "custom_d_tolerance", "custom_d_max", "custom_d_min",
                "custom_e_plastic_reel", "custom_e_max_plastic_reel", "custom_e_min_plastic_reel",
                "custom_f_plastic_reel", "custom_f_max_plastic_reel", "custom_f_min_plastic_reel",
                "custom_t1_tolerance", "custom_t1_max", "custom_t1_min",
                "custom_t2_tolerance", "custom_t2_max", "custom_t2_min",
                "custom_w1_tolerance", "custom_w1_max", "custom_w1_min",
                "custom_w2_tolerance", "custom_w2_max", "custom_w2_min",
                "custom_delta_e_tolerance", "custom_delta_e_max", "custom_delta_e_min",
                "custom_surface_resistance_ohms_plastic_reel", "custom_surface_resistance_ohms_plastic_reel_max", "custom_surface_resistance_ohms_plastic_reel_min"
            ],
            'engineering': [
                "custom_mold_base_width",
                "custom_mold_base_length",
                "custom_mold_base_height",
                "custom_mold_quantity",
                "custom_cavities"
            ],
            'text': [
                "custom_pockets_thermoformed_tray",
                "custom_pockets_carrier_tape",
                "custom_sample_color"
            ]
        };
    
        Object.values(fieldsToReset).flat().forEach(field => {
            const resetValue = fieldsToReset['text'].includes(field) ? null : 0;
            frm.set_value(field, resetValue);
        });
    
        frm.refresh();
    },
    // Add a helper function to generate mold_id
    generate_mold_ids: function(frm) {
        let child_table = frm.doc.custom_molds_items || [];
        if (child_table.length > 0) {
            let mold_count = 1;  // Initialize the running count for mold_id
            
            // Loop through each row in the child table
            child_table.forEach(function(row) {
                if (row.item_code) {
                    // Generate the mold_id for the current row
                    let mold_id = `MOLD-${frm.doc.item_code}-${String(mold_count).padStart(2, '0')}`;
                    
                    // Set the mold_id in the current row
                    frappe.model.set_value(row.doctype, row.name, 'mold_id', mold_id);
                    
                    mold_count++;  // Increment the mold count for the next row
                }
            });
        }
    }
});
frappe.ui.form.on('Item Customer Detail', {
    customer_name: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        
        // Fetch the customer_code based on the selected customer_name
        if (row.customer_name) {
            frappe.call({
                method: "frappe.client.get_value",
                args: {
                    doctype: "Customer",
                    filters: { name: row.customer_name },
                    fieldname: "name"
                },
                callback: function(response) {
                    if (response.message) {
                        // Set the ref_code based on the fetched customer_code
                        frappe.model.set_value(cdt, cdn, 'ref_code', response.message.name);
                    } else {
                        frappe.msgprint(__('No Customer Code found for the selected Customer.'));
                    }
                }
            });
        }
    }
});

frappe.ui.form.on('Item Molds Detail', {
    custom_molds_items_move: function(frm, cdt, cdn) {
        frm.events.generate_mold_ids(frm);
    },
    custom_molds_items_add: function(frm, cdt, cdn) {
        frm.events.generate_mold_ids(frm);
    },
    custom_molds_items_remove: function(frm, cdt, cdn) {
        frm.events.generate_mold_ids(frm);
    },
    item_code: function(frm, cdt, cdn) {
        frm.events.generate_mold_ids(frm);
    }
});

frappe.ui.form.on('Item Default', {
    item_defaults_add(frm, cdt, cdn) {
          // default warehouse in table item_defaults
        setDefaultWarehouse(frm, cdt, cdn);
    }
});

function setDefaultWarehouse(frm, cdt, cdn) {
    const itemGroup = frm.doc.item_group;
    if (['Raw Material', 'Raw Materials'].includes(itemGroup)) {
        frappe.model.set_value(cdt, cdn, 'default_warehouse', itemGroup);
    }
}