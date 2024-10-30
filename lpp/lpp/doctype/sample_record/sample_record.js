// Copyright (c) 2024, Ecosoft and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sample Record", {
	refresh(frm) {
        if (frm.is_new()) {
            frm.events.set_table_parameters(frm)
        }

        // Update Total Hours Setup
        if (frm.doc.start_date_setup && frm.doc.end_date_setup && !frm.doc.total_hours_setup) {
            update_total_hours(frm, 'start_date_setup', 'end_date_setup', 'total_hours_setup');
        }

        // Update Total Hours Production
        if (frm.doc.start_date_production && frm.doc.end_date_production && !frm.doc.total_hours_production) {
            update_total_hours(frm, 'start_date_production', 'end_date_production', 'total_hours_production');
        }

        // Update Scrap
        updateScrap(frm);

        // Calculate units__hour if output and total hours are available
        if (frm.doc.output && frm.doc.total_hours_production && !frm.doc.units__hour) {
            frm.set_value('units__hour', frm.doc.output / frm.doc.total_hours_production);
        }

        // Calculate yield if input and output are available
        if (frm.doc.input && frm.doc.output && !frm.doc.yield) {
            calculate_yield(frm, 'yield', 'output', 'input');
        }

	},
    customer: function(frm) {
        if (frm.doc.customer) {
            // Call server script to get filtered items based on selected customer
            frappe.call({
                method: "lpp.lpp.doctype.sample_record.sample_record.get_customer_items",
                args: {
                    customer_name: frm.doc.customer
                },
                callback: function(response) {
                    const items = response.message || [];

                    // Filter item_code field based on server response
                    frm.set_query('item_code', function() {
                        return {
                            filters: [
                                ['Item', 'name', 'in', items]  // Show only items in the list
                            ]
                        };
                    });

                    // Clear item_code, item_name if it does not match the filtered items
                    if (!items.includes(frm.doc.item_code)) {
                        frm.set_value({
                            'item_code': null,
                            'item_name': null
                        });
                    }
                }
            });
        } else {
            // Clear item_code, item_name if no customer is selected
            frm.set_value({
                'item_code': null,
                'item_name': null
            });

            // Remove filters to show all items in item_code
            frm.set_query('item_code', function() {
                return {};
            });
        }
    },
    set_table_parameters: function (frm) {
        // Clear existing rows
        frm.clear_table('sample_parameters');

        // Example data to add
        const set_parameters = [
            { sample_parameters: 'Planned Date' },
            { sample_parameters: 'Actual Date' }
        ];

        // Add new rows
        set_parameters.forEach(data => {
            const child = frm.add_child('sample_parameters');
            frappe.model.set_value(child.doctype, child.name, 'sample_parameters', data.sample_parameters);
        });
        // Refresh the child table to show changes
        frm.refresh_field('sample_parameters');
    },
    start_date_setup(frm) {
        update_total_hours(frm, 'start_date_setup', 'end_date_setup', 'total_hours_setup');
    },
    end_date_setup(frm) {
        update_total_hours(frm, 'start_date_setup', 'end_date_setup', 'total_hours_setup');
    },
    start_date_production(frm) {
        handle_production_date_update(frm);
    },
    end_date_production(frm) {
        handle_production_date_update(frm);
    },
    input(frm) {
        updateScrap(frm);
    },
    output(frm) {
        updateScrap(frm);
    }
});

frappe.ui.form.on('Sample Parameters', {
    mold_creation: function(frm, cdt, cdn) {
        updateStatus(frm, "mold_creation_status", "mold_creation");
    },
    sample_production: function(frm, cdt, cdn) {
        updateStatus(frm, "sample_production_status", "sample_production");
    },
    customer_delivery: function(frm, cdt, cdn) {
        updateStatus(frm, "customer_delivery_status", "customer_delivery");
    }
});

// ฟังก์ชันทั่วไปสำหรับคำนวณสถานะของฟิลด์ที่ต้องการ
function updateStatus(frm, targetField, dateField) {
    let plannedDate = null;
    let actualDate = null;

    // วนลูปผ่านแต่ละแถวใน sample_parameters เพื่อตรวจสอบวันที่
    (frm.doc.sample_parameters || []).forEach(row => {
        if (row.sample_parameters === "Planned Date" && row[dateField]) {
            plannedDate = new Date(row[dateField]);
        }
        if (row.sample_parameters === "Actual Date" && row[dateField]) {
            actualDate = new Date(row[dateField]);
        }
    });

    // ตั้งค่าสถานะตามการเปรียบเทียบวันที่
    let status = null;
    if (plannedDate && actualDate) {
        status = actualDate > plannedDate ? 'Late' : 'Ontime';
    } else {
        status = null; // กรณีที่ไม่มีค่าทั้งสองวันที่
    }

    // อัปเดตฟิลด์ targetField ตามสถานะ
    frm.set_value(targetField, status);
}

function update_total_hours(frm, start_field, end_field, output_field) {
    let start_date = frm.doc[start_field], end_date = frm.doc[end_field];
    
    if (start_date && end_date) {
        // คำนวณความต่างของเวลาจาก start_date และ end_date (เป็นมิลลิวินาที)
        let total_minutes = (new Date(end_date) - new Date(start_date)) / (1000 * 60);  // แปลงมิลลิวินาทีเป็นนาที
        let hours_decimal = (total_minutes / 60).toFixed(2);  // แปลงนาทีเป็นชั่วโมงทศนิยม

        // ตั้งค่าเป็นผลลัพธ์ในรูปแบบทศนิยม เช่น 2.20
        frm.set_value(output_field, hours_decimal);
    } else {
        frm.set_value(output_field, null);
    }
}

function handle_production_date_update(frm) {
    update_total_hours(frm, 'start_date_production', 'end_date_production', 'total_hours_production');
    if (frm.doc.output && frm.doc.total_hours_production) {
        frm.set_value('units__hour', frm.doc.output / frm.doc.total_hours_production);
    }
}

// Function to update Scrap
function updateScrap(frm) {
    if (!isNaN(frm.doc.input) && !isNaN(frm.doc.output)) {
        frm.set_value('scrap', frm.doc.input - frm.doc.output);
    }
    handle_production_date_update(frm);
    calculate_yield(frm, 'yield', 'output', 'input');
}

function calculate_yield(frm, output_field, output_value_field, input_value_field) {
    if (frm.doc[output_value_field] && frm.doc[input_value_field]) {
        frm.set_value(output_field, (frm.doc[output_value_field] / frm.doc[input_value_field]) * 100);
    }
}