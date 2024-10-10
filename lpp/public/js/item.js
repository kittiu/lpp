frappe.ui.form.on("Item", {
    item_group(frm) {
        if (frm.doc.item_group) {
            if (frm.doc.item_group == "Sales Products") {
                frm.set_value("has_batch_no", 1);
            }
            else if (frm.doc.item_group == "Raw Material" || frm.doc.item_group == "Raw Materials") {
                frm.set_value("has_batch_no", 1);
                // วนลูปผ่านทุกแถวใน item_defaults
                (frm.doc.item_defaults || []).forEach(function (row) {
                    // แทนค่าทุกฟิลด์ default_warehouse ใน item_defaults
                    frappe.model.set_value(row.doctype, row.name, "default_warehouse", "Raw Materials - LPP");
                });
            } else {
                frm.set_value("has_batch_no", 0);
            }
        }
    },

    custom_item_group_2: function (frm) {
        frm.events.reset_specifications_tolerance(frm);
    },

    reset_specifications_tolerance: function (frm) {

        const fields_to_reset = [
            'custom_height_tolerance', 'custom_height_max', 'custom_height_min',
            'custom_length_tolerance', 'custom_length_max', 'custom_length_min',
            'custom_thickness_tolerance', 'custom_thickness_max', 'custom_thickness_min',
            'custom_width_tolerance', 'custom_width_max', 'custom_width_min',
            'custom_a0_tolerance', 'custom_a0_max', 'custom_a0_min',
            'custom_b0_tolerance', 'custom_b0_max', 'custom_b0_min',
            'custom_k0_tolerance', 'custom_k0_max', 'custom_k0_min',
            'custom_p1_tolerance', 'custom_p1_max', 'custom_p1_min',
            'custom_length__reel_tolerance', 'custom_length__reel_max', 'custom_length__reel_min',
            'custom_cavities', 'custom_step_in_cavity',
            'custom_a_tolerance', 'custom_a_max', 'custom_a_min',
            'custom_n_tolerance', 'custom_n_max', 'custom_n_min',
            'custom_b_tolerance', 'custom_b_max', 'custom_b_min',
            'custom_c_tolerance', 'custom_c_max', 'custom_c_min',
            'custom_d_tolerance', 'custom_d_max', 'custom_d_min',
            'custom_e_tolerance', 'custom_e_max', 'custom_e_min',
            'custom_f_tolerance', 'custom_f_max', 'custom_f_min',
            'custom_t1_tolerance', 'custom_t1_max', 'custom_t1_min',
            'custom_t2_tolerance', 'custom_t2_max', 'custom_t2_min',
            'custom_w1_tolerance', 'custom_w1_max', 'custom_w1_min',
            'custom_w2_tolerance', 'custom_w2_max', 'custom_w2_min',
            'custom_surface_resistivity_ohmssq', 'custom_surface_resistivity_ohmssq_max', 'custom_surface_resistivity_ohmssq_min'
        ];
    
        // Loop through each field and reset its value to 0
        fields_to_reset.forEach(function(field) {
            frm.set_value(field, 0);
        });
    
        // Optionally, update the form after all values are set
        frm.refresh();

    },
});
