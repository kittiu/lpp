frappe.ui.form.on("Quality Inspection", {
    refresh(frm) {
        // Get today's date
        let today = frappe.datetime.nowdate();

        // Set 'custom_date_inspected_by' field to today's date by default
        frm.set_value("custom_date_inspected_by", today);

        // Set 'custom_date_approved_by' field to today's date by default
        frm.set_value("custom_date_approved_by", today);

        // Set ค่า default ของ inspection_type เป็น In Process
        if (!frm.doc.inspection_type) {
            frm.set_value('inspection_type', 'In Process');
        }

        // ซ่อนฟิลด์ inspection_type
        frm.set_df_property('inspection_type', 'hidden', true);
    },
	quality_inspection_template: function (frm) {        
		if (frm.doc.quality_inspection_template) {
			return frm.call({
				method: "get_item_specification_details",
				doc: frm.doc,
				callback: function () {
					refresh_field("readings");
				},
			});
		}
	},
    custom_quality_inspection_template_2 : function (frm) {
        if (frm.doc.custom_quality_inspection_template_2) {
            return frm.call({
                method: "custom_get_item_specification_details",
                doc: frm.doc,
                args: {
                    template_key: "custom_quality_inspection_template_2",
                    table_key: "custom_quality_inspection_template_2_table"
                },
                callback: function () {
                    refresh_field("custom_quality_inspection_template_2_table");
                },
            });
        }   
    },
    custom_quality_inspection_template_3 : function (frm) {
        if (frm.doc.custom_quality_inspection_template_3) {
            return frm.call({
                method: "custom_get_item_specification_details",
                doc: frm.doc,
                args: {
                    template_key: "custom_quality_inspection_template_3",
                    table_key: "custom_quality_inspection_template_3_table"
                },
                callback: function () {
                    refresh_field("custom_quality_inspection_template_3_table");
                },
            });
        }
    },
    custom_quality_inspection_checkbox_1_template_ : function (frm) {
        if (frm.doc.custom_quality_inspection_checkbox_1_template_) {
            return frm.call({
                method: "custom_get_item_specification_details",
                doc: frm.doc,
                args: {
                    template_key : "custom_quality_inspection_checkbox_1_template_",
                    table_key : "custom_quality_inspection_checkbox_1_table"
                },
                callback: function () {
                    refresh_field("custom_quality_inspection_checkbox_1_table");
                },
            });
        }
    },
    custom_quality_inspection_freetext_1_template_ : function (frm) {
        if (frm.doc.custom_quality_inspection_freetext_1_template_) {
            return frm.call({
                method: "custom_get_item_specification_details",
                doc: frm.doc,
                args: {
                    template_key : "custom_quality_inspection_freetext_1_template_",
                    table_key : "custom_quality_inspection_freetext_1_template_table"
                },
                callback: function () {
                    refresh_field("custom_quality_inspection_freetext_1_template_table");
                },
            });
        }
    },
    custom_quality_inspection_checkbox_2 : function (frm) {
        if (frm.doc.custom_quality_inspection_checkbox_2) {
            return frm.call({
                method: "custom_get_item_specification_details",
                doc: frm.doc,
                args: {
                    template_key : "custom_quality_inspection_checkbox_2",
                    table_key : "custom_quality_inspection_checkbox_2_table"
                },
                callback: function () {
                    refresh_field("custom_quality_inspection_checkbox_2_table");
                },
            });
        }
    },
    custom_quality_inspection_template_1 : function (frm) {
        if (frm.doc.custom_quality_inspection_template_1) {
            return frm.call({
                method: "custom_get_item_specification_details",
                doc: frm.doc,
                args: {
                    template_key : "custom_quality_inspection_template_1",
                    table_key : "custom_quality_inspection_template_table_1"
                },
                callback: function () {
                    refresh_field("custom_quality_inspection_template_table_1");
                },
            });
        }
    }
});

frappe.ui.form.on('Quality Inspection Reading', {
    reading_value: function(frm, cdt, cdn) {
        // Get the current row
        let row = locals[cdt][cdn];
    
        frappe.db.get_doc('Item', frm.doc.item_code)?.then((doc) => {
            const specs = [
                { name: 'A (reel diameter)', valueField: 'custom_a_reel_diameter', toleranceField: 'custom_a_reel_diameter_plus_or_minus' },
                { name: 'B (width)', valueField: 'custom_b_width', toleranceField: 'custom_b_width_plus_or_minus' },
                { name: 'C (diameter)', valueField: 'custom_c_diameter', toleranceField: 'custom_c_diameter_plus_or_minus' },
                { name: 'D (diameter)', valueField: 'custom_d_diameter', toleranceField: 'custom_d_diameter_plus_or_minus' },
                { name: 'E', valueField: 'custom_e', toleranceField: 'custom_e_plus_or_minus' },
                { name: 'F', valueField: 'custom_f', toleranceField: 'custom_f_plus_or_minus' },
                { name: 'N (hub diameter)', valueField: 'custom_n_hub_diameter', toleranceField: 'custom_n_hub_diameter_plus_or_minus' },
                { name: 'W1', valueField: 'custom_w1', toleranceField: 'custom_w1_plus_or_minus' },
                { name: 'W2', valueField: 'custom_w2', toleranceField: 'custom_w2_plus_or_minus' },
                { name: 'T (Flange thickness)', valueField: 'custom_t_flange_thickness', toleranceField: 'custom_t_flange_thickness_plus_or_minus' }
            ];
    
            const spec = specs.find(s => s.name === row.specification);
    
            if (spec) {
                let value = parseFloat(doc[spec.valueField]) || 0;
                let tolerance = parseFloat(doc[spec.toleranceField]) || 0;
    
                let min = value - tolerance;
                let max = value + tolerance;
    
                if (!(row.reading_value >= min && row.reading_value <= max)) {
                    frappe.msgprint({
                        title: __('Warning'),
                        message: `${row.specification} = <span style="font-weight: bold;">${row.reading_value}</span> is out of the acceptable range.<br><br>(Acceptable range is between <span style="font-weight: bold;">${min}</span> and <span style="font-weight: bold;">${max}</span>)`,
                        indicator: 'orange',
                        primary_action: {
                            label: __('Close'),
                            action: function() {
                                // This will close the modal
                                frappe.msg_dialog.hide();
                            }
                        }
                    });    
                }
            }
        });
    },
    reading_1: function(frm, cdt, cdn) {
        // Get the specific child row using cdt and cdn
        let child = locals[cdt][cdn];
        let reading_value = child.reading_1;
        
        // Initialize the parsed value to 0
        let parsed_value = '';
        
        // Ensure reading_value is a string before calling startsWith
        if (reading_value && typeof reading_value === 'string' && reading_value.startsWith('=')) {
            let number_after_equal = reading_value.substring(1).trim();
            parsed_value = number_after_equal
        } else {
            return;
        }
    
        
        // Update all readings in the child row
        for (let i = 1; i <= 32; i++) {
            let field_name = `reading_${i}`;
            if (i >= 11) {
                frappe.model.set_value(cdt, cdn, `custom_${field_name}`, parsed_value);
            } else {
                frappe.model.set_value(cdt, cdn, field_name, parsed_value);
            }
        }
    }
});

