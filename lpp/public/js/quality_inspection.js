const type_check_box = [
    "specification",
    "custom_item_1",
    "custom_item_2",
    "custom_item_3",
    "custom_item_4",
    "custom_item_5",
    "custom_item_6",
    "custom_item_7",
    "custom_item_8",
    "custom_item_9",
]

const type_reading = [
    "specification",
    "reading_1",
    "reading_2",
    "reading_3",
    "reading_4",
    "reading_5",
    "reading_6",
    "reading_7",
    "reading_8",
    "reading_9",
]

const type_accept_reject = [
    "specification",
    "custom_accept__reject",
    "custom_quantity",
    "custom_qty",
]

const type_dimension_report = [
    "specification",
    "reading_1",
    "reading_2",
    "reading_3",
    "reading_4",
    "reading_5",
    "custom_accept__reject",
]

const type_specifications_report = [
    "specification",
    "reading_1",
    "reading_2",
    "reading_3",
    "reading_4",
    "reading_5",
    "custom_average_",
    "custom_accept__reject",
]

// Reusable function to setup user-defined columns
function setupUserDefinedColumns(frm, tableField, typeArray) {
    frm.fields_dict[tableField].grid.setup_user_defined_columns = function () {
        if (typeArray && typeArray.length) {
            frm.fields_dict[tableField].grid.user_defined_columns = typeArray.map(fieldname => {
                let column = frappe.meta.get_docfield('Quality Inspection Reading', fieldname);
                if (column) {
                    column.in_list_view = 1;
                    column.columns = 1;
                    return column;
                }
            }).filter(Boolean);
        }
    };
    frm.fields_dict[tableField].grid.setup_user_defined_columns();
    frm.fields_dict[tableField].grid.refresh();
    frm.refresh_field(tableField);
}

frappe.ui.form.on("Quality Inspection", {
    onload: function (frm) {

        // ** Tab IMQT
        // Setup for custom_quality_inspection_checkbox_1_table
        setupUserDefinedColumns(frm, 'custom_quality_inspection_checkbox_1_table', type_check_box);

        // Setup for custom_quality_inspection_freetext_1_template_table
        setupUserDefinedColumns(frm, 'custom_quality_inspection_freetext_1_template_table', type_reading);

        // Setup for custom_quality_inspection_freetext_1_template_table
        setupUserDefinedColumns(frm, 'custom_quality_inspection_checkbox_2_table', type_reading);

        // Setup for custom_quality_inspection_template_table_1
        setupUserDefinedColumns(frm, 'custom_quality_inspection_template_table_1', type_check_box);

        // ** Tab BuyOff
        // Setup for custom_buyoff_table_1
        setupUserDefinedColumns(frm, 'custom_buyoff_table_1', type_specifications_report);

        // Setup for custom_buyoff_table_2
        setupUserDefinedColumns(frm, 'custom_buyoff_table_2', type_accept_reject);

        // Setup for custom_buyoff_table_3
        setupUserDefinedColumns(frm, 'custom_buyoff_table_3', type_accept_reject);

        // Setup for custom_buyoff_table_4
        setupUserDefinedColumns(frm, 'custom_buyoff_table_4', type_dimension_report);




        // ** Tab Roving
        // Setup for custom_roving_table_1
        setupUserDefinedColumns(frm, 'custom_roving_table_1', type_accept_reject);

        // Setup for custom_roving_table_2
        setupUserDefinedColumns(frm, 'custom_roving_table_2', type_accept_reject);

        // Setup for custom_roving_table_3
        setupUserDefinedColumns(frm, 'custom_roving_table_3', type_accept_reject);


        // ** Tab Final Inspection
        // Setup for readings
        setupUserDefinedColumns(frm, 'readings', type_accept_reject);

        // Setup for readings
        setupUserDefinedColumns(frm, 'custom_quality_inspection_template_2_table', type_accept_reject);

        // Setup for custom_quality_inspection_template_3_table
        setupUserDefinedColumns(frm, 'custom_quality_inspection_template_3_table', type_reading);

    },
    refresh(frm) {
        // Set ค่า default ของ inspection_type เป็น In Process
        if (!frm.doc.inspection_type) {
            frm.set_value('inspection_type', 'In Process');
        }

        // ซ่อนฟิลด์ inspection_type
        frm.set_df_property('inspection_type', 'hidden', true);
        frm.events.get_supplier(frm);

    },
    custom_inspection_progress: function (frm) {
        if(frm.doc.custom_inspection_progress === 'Buyoff'){
            frm.set_value('custom_buyoff_inspect_date', frappe.datetime.now_datetime());
            frm.set_value('custom_roving_inspect_date', null);
            frm.set_value('custom_final_inspection_inspect_date', null);
        }else if(frm.doc.custom_inspection_progress === 'Roving'){
            frm.set_value('custom_buyoff_inspect_date', null);
            frm.set_value('custom_roving_inspect_date', frappe.datetime.now_datetime());
            frm.set_value('custom_final_inspection_inspect_date', null);
        }else if(frm.doc.custom_inspection_progress === 'Final Inspection'){
            frm.set_value('custom_buyoff_inspect_date', null);
            frm.set_value('custom_roving_inspect_date', null);
            frm.set_value('custom_final_inspection_inspect_date', frappe.datetime.now_datetime());
        }else{
            frm.set_value('custom_buyoff_inspect_date', null);
            frm.set_value('custom_roving_inspect_date', null);
            frm.set_value('custom_final_inspection_inspect_date', null);
        }
    },
    reference_type: function (frm) {
        if(frm.doc.reference_type && frm.doc.reference_name && !frm.doc.custom_supplier){
            frm.events.get_supplier(frm);
        }
    },
    reference_name: async function (frm) {
        if (frm.doc.reference_type === 'Job Card' && frm.doc.reference_name) {
            try {
                const { message } = await frappe.db.get_value('Job Card', frm.doc.reference_name, 'production_item');
                message && frm.set_value('item_code', message.production_item);
            } catch (err) {
                console.error('Error fetching production item:', err);
            }
        } else if (frm.doc.reference_type && frm.doc.reference_name && !frm.doc.custom_supplier) {
            frm.events.get_supplier(frm);
        }
    },    
    get_supplier:function (frm) {
        if(frm.doc.reference_type === 'Purchase Receipt' && frm.doc.reference_name && !frm.doc.custom_supplier){
            const pr_name = frm.doc.reference_name;
            frappe.db.get_value('Purchase Receipt', pr_name, "supplier", function (value) {
                frm.set_value('custom_supplier', value['supplier']);
                // frm.save();
                // frm.refresh();
            });
        }
    },
    report_date: function (frm) {
        frm.events.chk_back_date(frm, 'report_date');

    },
    custom_date_inspected_by: function (frm) {
        frm.events.chk_back_date(frm, 'custom_date_inspected_by');

    },
    custom_date_approved_by: function (frm) {
        frm.events.chk_back_date(frm, 'custom_date_approved_by');

    },
    chk_back_date: function (frm, fieldName) {
        // Getting the current date and stripping the time part
        let today = frappe.datetime.get_today();

        // Comparing the selected date from the specified field with today's date
        if (frm.doc[fieldName] < today) {
            // Show alert if the selected date is before today
            frappe.msgprint({
                title: 'วันที่ไม่ถูกต้อง',
                message: 'ไม่สามารถเลือกวันที่ย้อนหลังจากวันที่ปัจจุบันได้ กรุณาเลือกวันที่ปัจจุบันหรือวันที่ในอนาคต',
                indicator: 'red'
            });

            // Reset the specified date field to null or another appropriate value
            frm.set_value(fieldName, null); // Clears the field
        }
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
    custom_quality_inspection_template_2: function (frm) {
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
    custom_quality_inspection_template_3: function (frm) {
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
    custom_quality_inspection_checkbox_1_template_: function (frm) {
        if (frm.doc.custom_quality_inspection_checkbox_1_template_) {
            return frm.call({
                method: "custom_get_item_specification_details",
                doc: frm.doc,
                args: {
                    template_key: "custom_quality_inspection_checkbox_1_template_",
                    table_key: "custom_quality_inspection_checkbox_1_table"
                },
                callback: function () {
                    refresh_field("custom_quality_inspection_checkbox_1_table");
                },
            });
        }
    },
    custom_quality_inspection_freetext_1_template_: function (frm) {
        if (frm.doc.custom_quality_inspection_freetext_1_template_) {
            return frm.call({
                method: "custom_get_item_specification_details",
                doc: frm.doc,
                args: {
                    template_key: "custom_quality_inspection_freetext_1_template_",
                    table_key: "custom_quality_inspection_freetext_1_template_table"
                },
                callback: function () {
                    refresh_field("custom_quality_inspection_freetext_1_template_table");
                },
            });
        }
    },
    custom_quality_inspection_checkbox_2: function (frm) {
        if (frm.doc.custom_quality_inspection_checkbox_2) {
            return frm.call({
                method: "custom_get_item_specification_details",
                doc: frm.doc,
                args: {
                    template_key: "custom_quality_inspection_checkbox_2",
                    table_key: "custom_quality_inspection_checkbox_2_table"
                },
                callback: function () {
                    refresh_field("custom_quality_inspection_checkbox_2_table");
                },
            });
        }
    },
    custom_quality_inspection_template_1: function (frm) {
        if (frm.doc.custom_quality_inspection_template_1) {
            return frm.call({
                method: "custom_get_item_specification_details",
                doc: frm.doc,
                args: {
                    template_key: "custom_quality_inspection_template_1",
                    table_key: "custom_quality_inspection_template_table_1"
                },
                callback: function () {
                    refresh_field("custom_quality_inspection_template_table_1");
                },
            });
        }
    },
    custom_roving_1: function (frm) {
        if (frm.doc.custom_roving_1) {
            return frm.call({
                method: "custom_get_item_specification_details",
                doc: frm.doc,
                args: {
                    template_key: "custom_roving_1",
                    table_key: "custom_roving_table_1"
                },
                callback: function () {
                    refresh_field("custom_roving_table_1");
                },
            });
        }
    },
    custom_roving_2: function (frm) {
        if (frm.doc.custom_roving_2) {
            return frm.call({
                method: "custom_get_item_specification_details",
                doc: frm.doc,
                args: {
                    template_key: "custom_roving_2",
                    table_key: "custom_roving_table_2"
                },
                callback: function () {
                    refresh_field("custom_roving_table_2");
                },
            });
        }
    },
    custom_roving_3: function (frm) {
        if (frm.doc.custom_roving_3) {
            return frm.call({
                method: "custom_get_item_specification_details",
                doc: frm.doc,
                args: {
                    template_key: "custom_roving_3",
                    table_key: "custom_roving_table_3"
                },
                callback: function () {
                    refresh_field("custom_roving_table_3");
                },
            });
        }
    }

});

frappe.ui.form.on('Quality Inspection Reading', {
    reading_value: function (frm, cdt, cdn) {
        // Get the current row
        let row = locals[cdt][cdn];

        frappe.db.get_doc('Item', frm.doc.item_code)?.then((doc) => {
            const specs = [
                { name: 'Thickness (mm)', valueField: 'custom_thickness_tolerance', toleranceFieldMax: 'custom_thickness_max', toleranceFieldMin: 'custom_thickness_min' },
                { name: 'Length (mm)', valueField: 'custom_length_tolerance', toleranceFieldMax: 'custom_length_max', toleranceFieldMin: 'custom_length_min' },
                { name: 'Height (mm)', valueField: 'custom_height_tolerance', toleranceFieldMax: 'custom_height_max', toleranceFieldMin: 'custom_height_min' },
                { name: 'Surface Resistivity (ohms/sq)', valueField: 'custom_surface_resistivity_ohmssq', toleranceFieldMax: 'custom_surface_resistivity_ohmssq_max', toleranceFieldMin: 'custom_surface_resistivity_ohmssq_min' },
                { name: 'A0 (mm)', valueField: 'custom_a0_tolerance', toleranceFieldMax: 'custom_a0_max', toleranceFieldMin: 'custom_a0_min' },
                { name: 'B0 (mm)', valueField: 'custom_b0_tolerance', toleranceFieldMax: 'custom_b0_max', toleranceFieldMin: 'custom_b0_min' },
                { name: 'K0 (mm)', valueField: 'custom_k0_tolerance', toleranceFieldMax: 'custom_k0_max', toleranceFieldMin: 'custom_k0_min' },
                { name: 'P1 (mm)', valueField: 'custom_p1_tolerance', toleranceFieldMax: 'custom_p1_max', toleranceFieldMin: 'custom_p1_min' },
                { name: 'Width (mm)', valueField: 'custom_width_tolerance', toleranceFieldMax: 'custom_width_max', toleranceFieldMin: 'custom_width_min' },
                { name: 'Length / Reel (m)', valueField: 'custom_length__reel_tolerance', toleranceFieldMax: 'custom_length__reel_max', toleranceFieldMin: 'custom_length__reel_min' },
                { name: 'Surface Resistivity (ohms/sq)', valueField: 'custom_surface_resistivity_ohmssq', toleranceFieldMax: 'custom_surface_resistivity_ohmssq_max', toleranceFieldMin: 'custom_surface_resistivity_ohmssq_min' },
                { name: '\u00d8A (mm)', valueField: 'custom_a_tolerance', toleranceFieldMax: 'custom_a_max', toleranceFieldMin: 'custom_a_min' },
                { name: '\u00d8N (mm) (+)', valueField: 'custom_n_tolerance', toleranceFieldMax: 'custom_n_max', toleranceFieldMin: 'custom_n_min' },
                { name: 'B (mm)', valueField: 'custom_b_tolerance', toleranceFieldMax: 'custom_b_max', toleranceFieldMin: 'custom_b_min' },
                { name: '\u00d8C (mm)', valueField: 'custom_c_tolerance', toleranceFieldMax: 'custom_c_max', toleranceFieldMin: 'custom_c_min' },
                { name: '\u00d8D (mm)', valueField: 'custom_d_tolerance', toleranceFieldMax: 'custom_d_max', toleranceFieldMin: 'custom_d_min' },
                { name: 'E (mm)', valueField: 'custom_e_tolerance', toleranceFieldMax: 'custom_e_max', toleranceFieldMin: 'custom_e_min' },
                { name: 'F (mm)', valueField: 'custom_f_tolerance', toleranceFieldMax: 'custom_f_max', toleranceFieldMin: 'custom_f_min' },
                { name: 'T1 (mm)', valueField: 'custom_t1_tolerance', toleranceFieldMax: 'custom_t1_max', toleranceFieldMin: 'custom_t1_min' },
                { name: 'T2 (mm)', valueField: 'custom_t2_tolerance', toleranceFieldMax: 'custom_t2_max', toleranceFieldMin: 'custom_t2_min' },
                { name: 'W1 (mm)', valueField: 'custom_w1_tolerance', toleranceFieldMax: 'custom_w1_max', toleranceFieldMin: 'custom_w1_min' },
                { name: 'W2 (mm)', valueField: 'custom_w2_tolerance', toleranceFieldMax: 'custom_w2_max', toleranceFieldMin: 'custom_w2_min' }
            ];

            const spec = specs.find(s => s.name === row.specification);

            if (spec) {
                let value = parseFloat(doc[spec.valueField]) || 0;
                let toleranceMax = parseFloat(doc[spec.toleranceFieldMax]) || 0;
                let toleranceMin = parseFloat(doc[spec.toleranceFieldMin]) || 0;

                let max = value + toleranceMax;
                let min = value - toleranceMin;

                if (!(row.reading_value >= min && row.reading_value <= max)) {
                    frappe.msgprint({
                        title: __('Warning'),
                        message: `${row.specification} = <span style="font-weight: bold;">${row.reading_value}</span> is out of the acceptable range.<br><br>(Acceptable range is between <span style="font-weight: bold;">${min}</span> and <span style="font-weight: bold;">${max}</span>)`,
                        indicator: 'orange',
                        primary_action: {
                            label: __('Close'),
                            action: function () {
                                // This will close the modal
                                frappe.msg_dialog.hide();
                            }
                        }
                    });
                }
            }
        });
    },
    reading_1: function (frm, cdt, cdn) {
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

