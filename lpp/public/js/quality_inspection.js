frappe.ui.form.on("Quality Inspection", {
    setup: function (frm) {

    },
    refresh: function (frm) {
        // Set ค่า default ของ inspection_type เป็น In Process
        if (!frm.doc.inspection_type) {
            frm.set_value('inspection_type', 'In Process');
        }

        // ซ่อนฟิลด์ inspection_type
        frm.set_df_property('inspection_type', 'hidden', true);
        frm.events.get_supplier(frm);


    },
    custom_inspection_progress: function (frm) {
        if (frm.doc.custom_inspection_progress === 'Buyoff') {
            frm.set_value('custom_buyoff_inspect_date', frappe.datetime.now_datetime());
            frm.set_value('custom_roving_inspect_date', null);
            frm.set_value('custom_final_inspection_inspect_date', null);
        } else if (frm.doc.custom_inspection_progress === 'Roving') {
            frm.set_value('custom_buyoff_inspect_date', null);
            frm.set_value('custom_roving_inspect_date', frappe.datetime.now_datetime());
            frm.set_value('custom_final_inspection_inspect_date', null);
        } else if (frm.doc.custom_inspection_progress === 'Final Inspection') {
            frm.set_value('custom_buyoff_inspect_date', null);
            frm.set_value('custom_roving_inspect_date', null);
            frm.set_value('custom_final_inspection_inspect_date', frappe.datetime.now_datetime());
        } else {
            frm.set_value('custom_buyoff_inspect_date', null);
            frm.set_value('custom_roving_inspect_date', null);
            frm.set_value('custom_final_inspection_inspect_date', null);
        }


        // Get the selected value of Inspection Progress
        let inspection_progress_value = frm.doc.custom_inspection_progress;

        // Define the options based on the selected Inspection Progress value
        let type_options = [];

        if (inspection_progress_value === 'IMQA') {
            type_options = ['IMQA - Plastic Sheet', 'IMQA - Plastic Pellets', 'IMQA - Agent & Others'];
        } else if (inspection_progress_value === 'Buyoff') {
            type_options = ['Buyoff - Tray (VAC)', 'Buyoff - Tray (CUT)', 'Buyoff - Reel'];
        } else if (inspection_progress_value === 'Roving') {
            type_options = ['Roving - Tray', 'Roving - Reel'];
        } else if (inspection_progress_value === 'Final Inspection') {
            type_options = ['Final Inspection - Tray', 'Final Inspection - Reel'];
        }

        // Set the options dynamically for the Type field
        frm.set_df_property('custom_type', 'options', type_options.join('\n'));

        // Optionally, you can clear the value of the Type field
        frm.set_value('custom_type', '');

    },
    custom_type: function (frm) {
        if (frm.doc.custom_type) {
            // ** IMQA
            frm.set_value('custom_quality_inspection_template_link_1', "");
            frm.toggle_display('custom_quality_inspection_order_table_1', false);
            frm.set_value('custom_quality_inspection_template_link_2', "");
            frm.toggle_display('custom_quality_inspection_order_table_2', false);
            frm.set_value('custom_quality_inspection_template_link_3', "");
            frm.toggle_display('custom_quality_inspection_order_table_3', false);

            if (frm.doc.custom_type === 'IMQA - Plastic Sheet') {
                frm.set_value('custom_quality_inspection_template_link_1', "IMQA - Plastic Sheet - (1) Visual Inspection");
                frm.toggle_display('custom_quality_inspection_order_table_1', true);
                frm.set_value('custom_quality_inspection_template_link_2', "IMQA - Plastic Sheet - (2) Specification Inspection");
                frm.toggle_display('custom_quality_inspection_order_table_2', true);
                frm.set_value('custom_quality_inspection_template_link_3', "IMQA - Plastic Sheet - (3) Functional Testing");
                frm.toggle_display('custom_quality_inspection_order_table_3', true);

            }
            else if (frm.doc.custom_type === 'IMQA - Plastic Pellets') {
                frm.set_value('custom_quality_inspection_template_link_1', "IMQA - Plastic Pellets - (1) Visual Inspection");
                frm.toggle_display('custom_quality_inspection_order_table_1', true);
                frm.set_value('custom_quality_inspection_template_link_2', "IMQA - Plastic Pellets - (2) Specification Inspection");
                frm.toggle_display('custom_quality_inspection_order_table_2', true);
            }
            else if (frm.doc.custom_type === 'IMQA - Agent & Others') {
                frm.set_value('custom_quality_inspection_template_link_1', "IMQA - Agent & Others - (1) Visual Inspection");
                frm.toggle_display('custom_quality_inspection_order_table_1', true);
            }
            // ** Buyoff
            else if (frm.doc.custom_type === 'Buyoff - Tray (VAC)') {
                frm.set_value('custom_quality_inspection_template_link_1', "Buyoff - Tray (VAC) - (1) Visual Inspection");
                frm.toggle_display('custom_quality_inspection_order_table_1', true);
                frm.set_value('custom_quality_inspection_template_link_2', "Buyoff - Tray (VAC) - (2) Specification Inspection");
                frm.toggle_display('custom_quality_inspection_order_table_2', true);
            }
            else if (frm.doc.custom_type === 'Buyoff - Tray (CUT)') {
                frm.set_value('custom_quality_inspection_template_link_1', "Buyoff - Tray (CUT) - (1) Visual Inspection");
                frm.toggle_display('custom_quality_inspection_order_table_1', true);
                frm.set_value('custom_quality_inspection_template_link_2', "Buyoff - Tray (CUT) - (2) Specification Inspection");
                frm.toggle_display('custom_quality_inspection_order_table_2', true);
            }
            else if (frm.doc.custom_type === 'Buyoff - Reel') {
                frm.set_value('custom_quality_inspection_template_link_1', "Buyoff - Reel - (1) Visual Inspection");
                frm.toggle_display('custom_quality_inspection_order_table_1', true);
                frm.set_value('custom_quality_inspection_template_link_2', "Buyoff - Reel - (2) Specification Inspection");
                frm.toggle_display('custom_quality_inspection_order_table_2', true);
                frm.set_value('custom_quality_inspection_template_link_3', "Buyoff - Reel - (3) Functional Testing");
                frm.toggle_display('custom_quality_inspection_order_table_3', true);
            }
            // ** Roving
            else if (frm.doc.custom_type === 'Roving - Tray') {
                frm.set_value('custom_quality_inspection_template_link_1', "Roving - Tray - (1) Visual Inspection");
                frm.toggle_display('custom_quality_inspection_order_table_1', true);
                frm.set_value('custom_quality_inspection_template_link_2', "Roving - Tray - (2) Specification Inspection");
                frm.toggle_display('custom_quality_inspection_order_table_2', true);
            }
            else if (frm.doc.custom_type === 'Roving - Reel') {
                frm.set_value('custom_quality_inspection_template_link_1', "Roving - Reel - (1) Visual Inspection");
                frm.toggle_display('custom_quality_inspection_order_table_1', true);
                frm.set_value('custom_quality_inspection_template_link_2', "Roving - Reel - (2) Specification Inspection");
                frm.toggle_display('custom_quality_inspection_order_table_2', true);
            }
            // ** Final Inspection
            else if (frm.doc.custom_type === 'Final Inspection - Tray') {
                frm.set_value('custom_quality_inspection_template_link_1', "Final Inspection - Tray - (1) Visual Inspection");
                frm.toggle_display('custom_quality_inspection_order_table_1', true);
                frm.set_value('custom_quality_inspection_template_link_2', "Final Inspection - Tray - (2) Specification Inspection");
                frm.toggle_display('custom_quality_inspection_order_table_2', true);
            }
            else if (frm.doc.custom_type === 'Final Inspection - Reel') {
                frm.set_value('custom_quality_inspection_template_link_1', "Final Inspection - Reel - (1) Visual Inspection");
                frm.toggle_display('custom_quality_inspection_order_table_1', true);
                frm.set_value('custom_quality_inspection_template_link_2', "Final Inspection - Reel - (2) Specification Inspection");
                frm.toggle_display('custom_quality_inspection_order_table_2', true);
            }


        }
    },
    reference_type: function (frm) {
        if (frm.doc.reference_type && frm.doc.reference_name && !frm.doc.custom_supplier) {
            frm.events.get_supplier(frm);
        }
    },
    reference_name: async function (frm) {
        if (frm.doc.reference_type === 'Job Card' && frm.doc.reference_name) {
            try {
                const { message } = await frappe.db.get_value('Job Card', frm.doc.reference_name, ['production_item', 'custom_lot_no']);
                if (message) {
                    frm.set_value({
                        item_code: message.production_item,
                        batch_no: message.custom_lot_no
                    });
                }
            } catch (err) {
                console.error('Error fetching production item:', err);
            }
        } else if (frm.doc.reference_type && frm.doc.reference_name && !frm.doc.custom_supplier) {
            frm.events.get_supplier(frm);
        }
    },
    get_supplier: function (frm) {
        if (frm.doc.reference_type === 'Purchase Receipt' && frm.doc.reference_name && !frm.doc.custom_supplier) {
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
    custom_quality_inspection_template_link_1: function (frm) {
        if (frm.doc.custom_quality_inspection_template_link_1) {

            return frm.call({
                method: "custom_get_item_specification_details",
                doc: frm.doc,
                args: {
                    template_key: "custom_quality_inspection_template_link_1",
                    table_key: "custom_quality_inspection_order_table_1"
                },
                callback: function () {
                    refresh_field("custom_quality_inspection_order_table_1");
                },
            });
        }
    },
    custom_quality_inspection_template_link_2: function (frm) {
        if (frm.doc.custom_quality_inspection_template_link_2) {

            return frm.call({
                method: "custom_get_item_specification_details",
                doc: frm.doc,
                args: {
                    template_key: "custom_quality_inspection_template_link_2",
                    table_key: "custom_quality_inspection_order_table_2"
                },
                callback: function () {
                    refresh_field("custom_quality_inspection_order_table_2");
                },
            });
        }
    },
    custom_quality_inspection_template_link_3: function (frm) {
        if (frm.doc.custom_quality_inspection_template_link_3) {

            return frm.call({
                method: "custom_get_item_specification_details",
                doc: frm.doc,
                args: {
                    template_key: "custom_quality_inspection_template_link_3",
                    table_key: "custom_quality_inspection_order_table_3"
                },
                callback: function () {
                    refresh_field("custom_quality_inspection_order_table_3");
                },
            });
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

frappe.ui.form.on("Quality Inspection Order", {
    form_render(frm, cdt, cdn) {
        const sample_size = frm.doc.sample_size;

        for (let i = 1; i <= 32; i++) {
            let hidden = i > sample_size ? 1 : 0;

            ["custom_quality_inspection_order_table_1", "custom_quality_inspection_order_table_2", "custom_quality_inspection_order_table_3"].forEach((table) => {
                frm.fields_dict[table].grid.update_docfield_property('inspected_value_' + i, "hidden", hidden);
                frm.fields_dict[table].grid.update_docfield_property('approval_' + i, "hidden", hidden);
                frm.fields_dict[table].grid.update_docfield_property('remark_' + i, "hidden", hidden);
            });
        }
        calculate_average_value(frm, cdt, cdn);
        count_accepted_rejected(frm, cdt, cdn);

    }, 
});

for (let i = 1; i <= 32; i++) {
    frappe.ui.form.on("Quality Inspection Order", "inspected_value_" + i, function (frm, cdt, cdn) {
        validate_inspected_value(frm, cdt, cdn , "inspected_value_" + i)
        calculate_average_value(frm, cdt, cdn );
    });

    frappe.ui.form.on("Quality Inspection Order", "approval_" + i, function (frm, cdt, cdn) {
        count_accepted_rejected(frm, cdt, cdn );
    });
}



// function for count Accepted / Rejected
function count_accepted_rejected(frm, cdt, cdn) {
    const sample_size = frm.doc.sample_size;
    const row = locals[cdt][cdn];
    let count_accepted = 0;
    let count_rejected = 0;
    for (let i = 1; i <= sample_size; i++) {
        const field_name = `approval_${i}`;
        const value = row[field_name];

        if (value === "Accepted") {
            count_accepted++;
        } else if (value === "Rejected") {
            count_rejected++;
        }
    }
    frappe.model.set_value(cdt, cdn, 'accepted', count_accepted);
    frappe.model.set_value(cdt, cdn, 'rejected', count_rejected);

}


function calculate_average_value(frm, cdt, cdn) {
    const sample_size = frm.doc.sample_size;
    const row = locals[cdt][cdn];

    const count = sample_size;
    let total = 0;

    for (let i = 1; i <= sample_size; i++) {
        const field_name = `inspected_value_${i}`;
        const value = row[field_name];
        if (value) {
            total += parseFloat(value);
        }
    }

    const average = total / count;
    frappe.model.set_value(cdt, cdn, 'average_value', average.toFixed(2));

}

function validate_inspected_value(frm, cdt, cdn , inspected_value_name) {

        const row = locals[cdt][cdn];
        let nominal_value = row.nominal_value;
        let tolerance_max = Number(row.tolerance_max);
        let tolerance_min = Number(row.tolerance_min);
        let inspected_value = row[inspected_value_name];

        // ตรวจสอบว่ามีการระบุ tolerance_max และ tolerance_min หรือไม่
        if (!!tolerance_max) {
            // คำนวณช่วงค่าที่อนุญาต
            let max_value = nominal_value + tolerance_max;
            
            // ตรวจสอบว่า Inspected Value  อยู่ในช่วงที่กำหนดหรือไม่
            if (inspected_value > max_value) {
                frappe.msgprint({
                    title: __('Warning'),
                    message: __('Inspected Value should be less than {0} ', [max_value]),
                    indicator: 'orange',
                    primary_action: {
                        label: __('Close'),
                        action: function () {
                            // This will close the modal
                            frappe.msg_dialog.hide();
                            row[inspected_value_name] = inspected_value

                        }
                    }
                });
            }
        }

        if (!!tolerance_min) {
            // คำนวณช่วงค่าที่อนุญาต
            let min_value = nominal_value - tolerance_min;

            // ตรวจสอบว่า Inspected Value  อยู่ในช่วงที่กำหนดหรือไม่
            if (inspected_value < min_value) {
                frappe.msgprint({
                    title: __('Warning'),
                    message: __('Inspected Value should be more than {0}', [min_value]),
                    indicator: 'orange',
                    primary_action: {
                        label: __('Close'),
                        action: function () {
                            // This will close the modal
                            frappe.msg_dialog.hide();
                            row[inspected_value_name] = inspected_value
                        }
                    }
                });     
            }
        }
    
}