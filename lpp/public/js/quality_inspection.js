frappe.ui.form.on("Quality Inspection", {

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
