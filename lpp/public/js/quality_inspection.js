frappe.ui.form.on("Quality Inspection", {
    onload: function (frm) {
        if (!frm.doc.custom_date_inspected_by) {
            frm.set_value('custom_date_inspected_by', frappe.datetime.now_datetime());
        }
        if (!frm.doc.custom_date_approved_by) {
            frm.set_value('custom_date_approved_by', frappe.datetime.now_datetime());
        }

        if (frm.doc.custom_inspection_progress) {
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
            frm.set_df_property('custom_type', 'options', type_options.join('\n'));


        }

    },
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
    sample_size: function (frm) {
        const custom_quality_inspection_order_table_1 = frm.doc.custom_quality_inspection_order_table_1;
        const custom_quality_inspection_order_table_2 = frm.doc.custom_quality_inspection_order_table_2;
        const custom_quality_inspection_order_table_3 = frm.doc.custom_quality_inspection_order_table_3;

        if (frm.doc.sample_size < 1 || frm.doc.sample_size > 32) {
            frappe.msgprint({
                title: __('Validation Error'),
                message: __('Sample size  must be between 1 and 32.'),
                indicator: 'red'
            });
            frm.doc.sample_size = 1
            frm.refresh_field("sample_size");
            return false;
        }



        for (let i = 0; i < custom_quality_inspection_order_table_1.length; i++) {
            const row = custom_quality_inspection_order_table_1[i];
            calculate_average_value(frm, "Quality Inspection Order", row.name);
            count_accepted_rejected(frm, "Quality Inspection Order", row.name);
        }

        for (let i = 0; i < custom_quality_inspection_order_table_2.length; i++) {
            const row = custom_quality_inspection_order_table_2[i];
            calculate_average_value(frm, "Quality Inspection Order", row.name);
            count_accepted_rejected(frm, "Quality Inspection Order", row.name);
        }

        for (let i = 0; i < custom_quality_inspection_order_table_3.length; i++) {
            const row = custom_quality_inspection_order_table_3[i];
            calculate_average_value(frm, "Quality Inspection Order", row.name);
            count_accepted_rejected(frm, "Quality Inspection Order", row.name);
        }

    },
    custom_inspection_progress: function (frm) {
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
    custom_type: async function (frm) {
        if (!frm.doc.custom_type) return;

        // Define configurations for different types
        const config = {
            'IMQA - Plastic Sheet': [
                ["custom_quality_inspection_template_link_1", "IMQA - Plastic Sheet - (1) Visual Inspection", "custom_quality_inspection_order_table_1"],
                ["custom_quality_inspection_template_link_2", "IMQA - Plastic Sheet - (2) Specification Inspection", "custom_quality_inspection_order_table_2"],
                ["custom_quality_inspection_template_link_3", "IMQA - Plastic Sheet - (3) Functional Testing", "custom_quality_inspection_order_table_3"]
            ],
            'IMQA - Plastic Pellets': [
                ["custom_quality_inspection_template_link_1", "IMQA - Plastic Pellets - (1) Visual Inspection", "custom_quality_inspection_order_table_1"],
                ["custom_quality_inspection_template_link_2", "IMQA - Plastic Pellets - (2) Specification Inspection", "custom_quality_inspection_order_table_2"]
            ],
            'IMQA - Agent & Others': [
                ["custom_quality_inspection_template_link_1", "IMQA - Agent & Others - (1) Visual Inspection", "custom_quality_inspection_order_table_1"]
            ],
            'Buyoff - Tray (VAC)': [
                ["custom_quality_inspection_template_link_1", "Buyoff - Tray (VAC) - (1) Visual Inspection", "custom_quality_inspection_order_table_1"],
                ["custom_quality_inspection_template_link_2", "Buyoff - Tray (VAC) - (2) Specification Inspection", "custom_quality_inspection_order_table_2"]
            ],
            'Buyoff - Tray (CUT)': [
                ["custom_quality_inspection_template_link_1", "Buyoff - Tray (CUT) - (1) Visual Inspection", "custom_quality_inspection_order_table_1"],
                ["custom_quality_inspection_template_link_2", "Buyoff - Tray (CUT) - (2) Specification Inspection", "custom_quality_inspection_order_table_2"]
            ],
            'Buyoff - Reel': [
                ["custom_quality_inspection_template_link_1", "Buyoff - Reel - (1) Visual Inspection", "custom_quality_inspection_order_table_1"],
                ["custom_quality_inspection_template_link_2", "Buyoff - Reel - (2) Specification Inspection", "custom_quality_inspection_order_table_2"],
                ["custom_quality_inspection_template_link_3", "Buyoff - Reel - (3) Functional Testing", "custom_quality_inspection_order_table_3"]
            ],
            'Roving - Tray': [
                ["custom_quality_inspection_template_link_1", "Roving - Tray - (1) Visual Inspection", "custom_quality_inspection_order_table_1"],
                ["custom_quality_inspection_template_link_2", "Roving - Tray - (2) Specification Inspection", "custom_quality_inspection_order_table_2"]
            ],
            'Roving - Reel': [
                ["custom_quality_inspection_template_link_1", "Roving - Reel - (1) Visual Inspection", "custom_quality_inspection_order_table_1"],
                ["custom_quality_inspection_template_link_2", "Roving - Reel - (2) Specification Inspection", "custom_quality_inspection_order_table_2"]
            ],
            'Final Inspection - Tray': [
                ["custom_quality_inspection_template_link_1", "Final Inspection - Tray - (1) Visual Inspection", "custom_quality_inspection_order_table_1"],
                ["custom_quality_inspection_template_link_2", "Final Inspection - Tray - (2) Specification Inspection", "custom_quality_inspection_order_table_2"]
            ],
            'Final Inspection - Reel': [
                ["custom_quality_inspection_template_link_1", "Final Inspection - Reel - (1) Visual Inspection", "custom_quality_inspection_order_table_1"],
                ["custom_quality_inspection_template_link_2", "Final Inspection - Reel - (2) Specification Inspection", "custom_quality_inspection_order_table_2"]
            ]
        };

        // Clear all values and tables first
        await Promise.all([
            frm.set_value('custom_quality_inspection_template_link_1', ""),
            frm.set_value('custom_quality_inspection_template_link_2', ""),
            frm.set_value('custom_quality_inspection_template_link_3', ""),
            frm.toggle_display('custom_quality_inspection_order_table_1', false),
            frm.toggle_display('custom_quality_inspection_order_table_2', false),
            frm.toggle_display('custom_quality_inspection_order_table_3', false)
        ]);

        await Promise.all([
            frm.clear_table('custom_quality_inspection_order_table_1'),
            frm.clear_table('custom_quality_inspection_order_table_2'),
            frm.clear_table('custom_quality_inspection_order_table_3')
        ]);

        // Set values based on type
        const settings = config[frm.doc.custom_type];
        if (settings) {
            for (const [linkField, linkValue, tableField] of settings) {
                await frm.set_value(linkField, linkValue);
                frm.toggle_display(tableField, true);
            }
        }

        // Refresh fields
        ['custom_quality_inspection_order_table_1', 'custom_quality_inspection_order_table_2', 'custom_quality_inspection_order_table_3'].forEach(field => frm.refresh_field(field));
    },
    reference_type: function (frm) {
        if (frm.doc.reference_type && frm.doc.reference_name && !frm.doc.custom_supplier) {
            frm.events.get_supplier(frm);
        }
    },
    reference_name: async function (frm) {
        if (frm.doc.reference_type === 'Job Card' && frm.doc.reference_name) {
            try {
                const { message } = await frappe.db.get_value('Job Card', frm.doc.reference_name, ['production_item', 'custom_lot_no','custom_production_item_name']);
                if (message) {
                    frm.set_value({
                        item_code: message.production_item,
                        batch_no: message.custom_lot_no,
                        item_name : message.custom_production_item_name,
                    });
                }
            } catch (err) {
                console.error('Error fetching production item:', err);
            }
        }
        else if (frm.doc.reference_type === 'Purchase Receipt' && frm.doc.reference_name) {
            try {
                // Use frappe.get_doc to fetch the full document, including child tables
                const doc = await frappe.db.get_doc('Purchase Receipt', frm.doc.reference_name);
                if (doc && doc.items && doc.items.length > 0) {
                    const item = doc.items[0];
                    frm.set_value({
                        item_code: item.item_code,
                        item_name : item.item_name,
                        batch_no: item.batch_no
                    });
                }
            } catch (err) {
                console.error('Error fetching Purchase Receipt items:', err);
            }
        }
        else if (frm.doc.reference_type && frm.doc.reference_name && !frm.doc.custom_supplier) {
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
            frm.clear_table("custom_quality_inspection_order_table_1");
            frm.set_value('custom_quality_inspection_order_table_1', []);
            frappe.model.clear_table(frm.doc, 'custom_quality_inspection_order_table_1');

            // Call the server-side method and populate the child table


            frappe.call({
                method: "custom_get_item_specification_details",
                doc: frm.doc,
                args: {
                    item_code: frm.doc.item_code,
                    template_key: "custom_quality_inspection_template_link_1",
                    table_key: "custom_quality_inspection_order_table_1"
                },
                callback: function (response) {
                    const table_data = response.message;
                    // Populate the child table with returned data
                    if (table_data && Array.isArray(table_data)) {
                        table_data.forEach(row => {

                            const child = frm.add_child("custom_quality_inspection_order_table_1"); 
                            frappe.model.set_value(child.doctype, child.name, "defects", row.defects);
                            frappe.model.set_value(child.doctype, child.name, "status", row.status);
                            frappe.model.set_value(child.doctype, child.name, "nominal_value", row.nominal_value);
                            frappe.model.set_value(child.doctype, child.name, "tolerance_max", row.tolerance_max);
                            frappe.model.set_value(child.doctype, child.name, "tolerance_min", row.tolerance_min);
                            frm.refresh_field("custom_quality_inspection_order_table_1");

                        });

                    }
                }
            })



        }
    },
    custom_quality_inspection_template_link_2: function (frm) {
        if (frm.doc.custom_quality_inspection_template_link_2) {
            frm.clear_table("custom_quality_inspection_order_table_2");
            frm.set_value('custom_quality_inspection_order_table_2', []);
            frappe.model.clear_table(frm.doc, 'custom_quality_inspection_order_table_2');
            // Call the server-side method and populate the child table
            frappe.call({
                method: "custom_get_item_specification_details",
                doc: frm.doc,
                args: {
                    item_code: frm.doc.item_code,
                    template_key: "custom_quality_inspection_template_link_2",
                    table_key: "custom_quality_inspection_order_table_2"
                },
                callback: function (response) {
                    const table_data = response.message;
                    // Populate the child table with returned data
                    if (table_data && Array.isArray(table_data)) {
                        table_data.forEach(row => {

                            const child = frm.add_child("custom_quality_inspection_order_table_2"); 
                            frappe.model.set_value(child.doctype, child.name, "defects", row.defects);
                            frappe.model.set_value(child.doctype, child.name, "status", row.status);
                            frappe.model.set_value(child.doctype, child.name, "nominal_value", row.nominal_value);
                            frappe.model.set_value(child.doctype, child.name, "tolerance_max", row.tolerance_max);
                            frappe.model.set_value(child.doctype, child.name, "tolerance_min", row.tolerance_min);
                            frm.refresh_field("custom_quality_inspection_order_table_2");

                        });
                    }
                }
            });
        }
    },
    custom_quality_inspection_template_link_3: function (frm) {
        if (frm.doc.custom_quality_inspection_template_link_3) {
            frm.clear_table("custom_quality_inspection_order_table_3");
            frm.set_value('custom_quality_inspection_order_table_3', []);
            frappe.model.clear_table(frm.doc, 'custom_quality_inspection_order_table_3');
            // Call the server-side method and populate the child table
            frappe.call({
                method: "custom_get_item_specification_details",
                doc: frm.doc,
                args: {
                    item_code: frm.doc.item_code,
                    template_key: "custom_quality_inspection_template_link_3",
                    table_key: "custom_quality_inspection_order_table_3"
                },
                callback: function (response) {
                    const table_data = response.message;
                    // Populate the child table with returned data
                    if (table_data && Array.isArray(table_data)) {
                        table_data.forEach(row => {

                            const child = frm.add_child("custom_quality_inspection_order_table_3"); 
                            frappe.model.set_value(child.doctype, child.name, "defects", row.defects);
                            frappe.model.set_value(child.doctype, child.name, "status", row.status);
                            frappe.model.set_value(child.doctype, child.name, "nominal_value", row.nominal_value);
                            frappe.model.set_value(child.doctype, child.name, "tolerance_max", row.tolerance_max);
                            frappe.model.set_value(child.doctype, child.name, "tolerance_min", row.tolerance_min);
                            frm.refresh_field("custom_quality_inspection_order_table_3");

                        });
                    }
                }
            });
        }
    },

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
        validate_inspected_value(frm, cdt, cdn, "inspected_value_" + i)
        calculate_average_value(frm, cdt, cdn);
    });

    frappe.ui.form.on("Quality Inspection Order", "approval_" + i, function (frm, cdt, cdn) {
        count_accepted_rejected(frm, cdt, cdn);
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

function validate_inspected_value(frm, cdt, cdn, inspected_value_name) {

    const row = locals[cdt][cdn];
    let nominal_value = row.nominal_value;
    let tolerance_max = Number(row.tolerance_max);
    let tolerance_min = Number(row.tolerance_min);
    let inspected_value = row[inspected_value_name];

    // ตรวจสอบว่ามีการระบุ tolerance_max และ tolerance_min หรือไม่
    if (row.tolerance_max != "") {
        // คำนวณช่วงค่าที่อนุญาต
        let max_value = nominal_value + tolerance_max;        
        // ตรวจสอบว่า Inspected Value  อยู่ในช่วงที่กำหนดหรือไม่
        if (inspected_value > max_value) {
            frappe.show_alert({
                message: __('Inspected Value should be less than {0} ', [max_value]),
                indicator: 'orange'
            }, 60);
            row[inspected_value_name] = inspected_value
        }
    }

    if (row.tolerance_min != "") {
        // คำนวณช่วงค่าที่อนุญาต
        let min_value = nominal_value - tolerance_min;
        // ตรวจสอบว่า Inspected Value  อยู่ในช่วงที่กำหนดหรือไม่
        if (inspected_value < min_value) {
            frappe.show_alert({
                message: __('Inspected Value should be more than {0}', [min_value]),
                indicator: 'orange'
            }, 60);
            row[inspected_value_name] = inspected_value
        }
    }

}