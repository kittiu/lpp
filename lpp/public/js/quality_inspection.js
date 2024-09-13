frappe.ui.form.on("Quality Inspection", {
    refresh(frm) {
        // Get today's date
        let today = frappe.datetime.nowdate();

        // Set 'custom_date_inspected_by' field to today's date by default
        frm.set_value("custom_date_inspected_by", today);

        // Set 'custom_date_approved_by' field to today's date by default
        frm.set_value("custom_date_approved_by", today);
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
    }
});
