// Copyright (c) 2024, Ecosoft and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sample Record", {
	refresh(frm) {
        if (frm.is_new()) {
            frm.events.set_table_parameters(frm)
        }

        // Update Total Hours Setup
        if (frm.doc.start_date_setup_sample && frm.doc.end_date_setup_sample && !frm.doc.total_hours_setup_sample) {
            updateTotalHours(frm, 'start_date_setup_sample_sample', 'end_date_setup_sample', 'total_hours_setup_sample');
        }

        // Update Total Hours Production
        if (frm.doc.start_date_production_sample && frm.doc.end_date_production_sample && !frm.doc.total_hours_production_sample) {
            updateTotalHours(frm, 'start_date_production_sample', 'end_date_production_sample', 'total_hours_production_sample');
        }

        // Update Scrap
        updateScrap(frm);

        // Calculate units__hour if output and total hours are available
        updateUnitsPerHour(frm);

        // Calculate yield if input and output are available
        if (frm.doc.input_sample && frm.doc.output_sample && !frm.doc.yield_sample) {
            calculateYield(frm, 'yield_sample', 'output_sample', 'input_sample');
        }

        // Calculate yield_with_setup_sample if all required fields are available
        if (frm.doc.input_sample && frm.doc.output_sample && frm.doc.setup_quantity_setup_sample && frm.doc.setup_quantity_production_sample && !frm.doc.yield_with_setup_sample) {
            calculateYieldWithSetup(frm);
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
    start_date_setup_sample(frm) {
        updateTotalHours(frm, 'start_date_setup_sample', 'end_date_setup_sample', 'total_hours_setup_sample');
    },
    end_date_setup_sample(frm) {
        updateTotalHours(frm, 'start_date_setup_sample', 'end_date_setup_sample', 'total_hours_setup_sample');
    },
    start_date_production_sample(frm) {
        updateTotalHours(frm, 'start_date_production_sample', 'end_date_production_sample', 'total_hours_production_sample');
        updateUnitsPerHour(frm);
    },
    end_date_production_sample(frm) {
        updateTotalHours(frm, 'start_date_production_sample', 'end_date_production_sample', 'total_hours_production_sample');
        updateUnitsPerHour(frm);
    },
    setup_weight_setup_sample(frm) {
        calculateWeightOrUnit(frm, 'setup_weight_setup_sample', 'setup_quantity_setup_sample', true)
    },
    setup_quantity_setup_sample(frm) {
        calculateWeightOrUnit(frm, 'setup_quantity_setup_sample', 'setup_weight_setup_sample', false)
        calculateYieldWithSetup(frm);
    },
    setup_weight_production_sample(frm) {
        calculateWeightOrUnit(frm, 'setup_weight_production_sample', 'setup_quantity_production_sample', true)
    },
    setup_quantity_production_sample(frm) {
        calculateWeightOrUnit(frm, 'setup_quantity_production_sample', 'setup_weight_production_sample', false)
        calculateYieldWithSetup(frm);
    },
    input_sample(frm) {
        updateScrap(frm);
        calculateYieldWithSetup(frm);
    },
    output_sample(frm) {
        updateScrap(frm);
        calculateYieldWithSetup(frm);
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

function updateTotalHours(frm, start_field, end_field, output_field) {
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

function calculateWeightOrUnit(frm, source_field, target_field, is_unit_to_weight) {    
    if (frm.doc.weight__unit && frm.doc[source_field]) {
        let calculated_value = is_unit_to_weight
            ? (frm.doc[source_field] / frm.doc.weight__unit)
            : (frm.doc[source_field] * frm.doc.weight__unit)
        if (frm.doc[target_field] != calculated_value) {
            frm.set_value(target_field, calculated_value);
        }
    }
}

// Update units per hour
function updateUnitsPerHour(frm) {    
    if (frm.doc.output_sample && frm.doc.total_hours_production_sample) {
        frm.set_value(
            'units__hour_sample', 
            parseInt(frm.doc.total_hours_production_sample, 10) === 0 
                ? null 
                : frm.doc.output_sample / frm.doc.total_hours_production_sample
        );
    } else {
        frm.set_value('units__hour_sample', null);
    }
}

// Function to update Scrap
function updateScrap(frm) {
    if (!isNaN(frm.doc.input_sample) && !isNaN(frm.doc.output_sample)) {
        frm.set_value('scrap_sample', frm.doc.input_sample - frm.doc.output_sample);
    }
    updateTotalHours(frm, 'start_date_production_sample', 'end_date_production_sample', 'total_hours_production_sample');
    updateUnitsPerHour(frm);
    calculateYield(frm, 'yield_sample', 'output_sample', 'input_sample');
}

function calculateYield(frm, output_field, output_value_field, input_value_field) {
    if (frm.doc[output_value_field] && frm.doc[input_value_field]) {
        frm.set_value(output_field, (frm.doc[output_value_field] / frm.doc[input_value_field]) * 100);
    }
}

function calculateYieldWithSetup(frm) {
    if (frm.doc.input_sample && frm.doc.output_sample && frm.doc.setup_weight_setup_sample && frm.doc.setup_weight_production_sample) {
        let total_weight = Number(frm.doc.setup_weight_setup_sample) + Number(frm.doc.setup_weight_production_sample);
        frm.set_value('yield_with_setup_sample', (frm.doc.output_sample / (frm.doc.input_sample + total_weight)) * 100);
    }
}