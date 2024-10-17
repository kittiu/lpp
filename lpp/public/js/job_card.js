
// Trigger events for the Job Card doctype
frappe.ui.form.on("Job Card", {
    refresh(frm) {
        console.log('frm', frm.doc);
        
        // Set 'item_code' and 'item_name' fields in 'scrap_items' child table to read-only
        frm.get_field("scrap_items").grid.toggle_enable("item_code", false);
        frm.get_field("scrap_items").grid.toggle_enable("item_name", false);

        // update total hours
        if (frm.doc.custom_start_date_setup && frm.doc.custom_end_date_setup) {
            update_custom_total_hours(frm, 'custom_start_date_setup', 'custom_end_date_setup', 'custom_total_hours_setup');
        }

        if (frm.doc.custom_start_date_production && frm.doc.custom_end_date_production) {
            update_custom_total_hours(frm, 'custom_start_date_production', 'custom_end_date_production', 'custom_total_hours_production');
        }

        setTimeout(() => {
            if (frm.custom_buttons && frm.custom_buttons[('Complete Job')]) {
                // Remove Original Button
                frm.remove_custom_button(__('Complete Job'))
                frm.add_custom_button(__("Complete Job"), () => {
                    var sub_operations = frm.doc.sub_operations;

                    let set_qty = true;
                    if (sub_operations && sub_operations.length > 1) {
                        set_qty = false;
                        let last_op_row = sub_operations[sub_operations.length - 2];
    
                        if (last_op_row.status == "Complete") {
                            set_qty = true;
                        }
                    }
    
                    if (set_qty) {
                        frappe.prompt(
                            {
                                fieldtype: "Float",
                                label: __("Completed Quantity"),
                                fieldname: "qty",
                                default: frm.doc.for_quantity,
                            },
                            (data) => {
                                frm.events.custom_complete_job(frm, "Complete", data.qty);
                            },
                            __("Enter Value")
                        );
                    } else {
                        frm.events.custom_complete_job(frm, "Complete", 0.0);
                    }
                }).addClass("btn-primary");
            }
        }, 10);
    },
    // Triggered when 'production_item' changes
    production_item(frm) {
        update_scrap_items(frm);
    },
    // Triggered when 'custom_production_item_name' changes
    custom_production_item_name(frm) {
        update_scrap_items(frm);
    },
    custom_complete_job: async function (frm, status, completed_qty) {
		const args = {
			job_card_id: frm.doc.name,
			complete_time: frappe.datetime.now_datetime(),
			status: status,
			completed_qty: completed_qty,
		};

        const current_operation_no = frm.doc.custom_operation_no;
        const total_operations = frm.doc.custom_total_operation;

        // Check if custom_operation_no is neither the first nor the last
        if (current_operation_no !== '1' && current_operation_no !== total_operations) {
            const previous_operation_no = current_operation_no - 1;

            const filters = {
                work_order: frm.doc.work_order,
                custom_runcard_no: frm.doc.custom_runcard_no,
                status: "Completed",
                custom_operation_no: previous_operation_no
            };

            // Fetch Job Card entries that match the filter criteria
            const result = await frappe.db.get_list('Job Card', {
                fields: ['total_completed_qty'],
                filters: filters
            });
            
            if (result.length > 0) {
                const previous_total_completed_qty = result[0].total_completed_qty;
                // Check if current completed quantity exceeds the previous operation's total completed quantity
                if ((frm.doc.total_completed_qty + completed_qty) > previous_total_completed_qty) {
                    return frappe.msgprint({
                        title: __('Error'),
                        message: __('ไม่สามารถระบุจำนวน FG ได้เกินกว่าจำนวน FG ของ Operation ก่อนหน้า'),
                        indicator: 'red'
                    });
                }
            }
        }
        // If the operation passes the checks or is the first/last operation, make the time log
        frm.events.make_time_log(frm, args);
    },
    custom_start_date_setup(frm) {
        if (frm.doc.custom_start_date_setup && frm.doc.custom_end_date_setup) {
            update_custom_total_hours(frm, 'custom_start_date_setup', 'custom_end_date_setup', 'custom_total_hours_setup');
        }
    },
    custom_end_date_setup(frm) {
        if (frm.doc.custom_start_date_setup && frm.doc.custom_end_date_setup) {
            update_custom_total_hours(frm, 'custom_start_date_setup', 'custom_end_date_setup', 'custom_total_hours_setup');
        }
    },
    custom_start_date_production(frm) {
        if (frm.doc.custom_start_date_production && frm.doc.custom_end_date_production) {
            update_custom_total_hours(frm, 'custom_start_date_production', 'custom_end_date_production', 'custom_total_hours_production');
        }
    },
    custom_end_date_production(frm) {
        if (frm.doc.custom_start_date_production && frm.doc.custom_end_date_production) {
            update_custom_total_hours(frm, 'custom_start_date_production', 'custom_end_date_production', 'custom_total_hours_production');
        }
    },

    custom_as_unit_quantity_setup: (frm) => {
        calculate_weight_or_unit(frm, 'custom_as_unit_quantity_setup', 'custom_as_weight_setup', true)}
    ,
    custom_as_weight_setup: (frm) => {
        calculate_weight_or_unit(frm, 'custom_as_weight_setup', 'custom_as_unit_quantity_setup', false)},
    
    custom_as_unit_quantity_production: (frm) => {
        calculate_weight_or_unit(frm, 'custom_as_unit_quantity_production', 'custom_as_weight_production', true)
    },
    custom_as_weight_production: (frm) => {
        calculate_weight_or_unit(frm, 'custom_as_weight_production', 'custom_as_unit_quantity_production', false)
    }
});

// Function to update 'item_code' and 'item_name' in all rows of 'scrap_items' child table
function update_scrap_items(frm) {
    const production_item = frm.doc.production_item; // Get the Production Item from the parent Job Card
    const production_item_name = frm.doc.custom_production_item_name; // Get the Production Item Name

    if (production_item) {
        // Loop through each row in the 'scrap_items' child table
        frm.doc.scrap_items.forEach(row => {
            // Set the 'item_code' and 'item_name' to match the Production Item
            row.item_code = production_item;
            row.item_name = production_item_name;
        });
        // Refresh the child table to reflect changes
        frm.refresh_field("scrap_items");
    }
}

// Trigger events for the child table 'Job Card Scrap Item'
frappe.ui.form.on("Job Card Scrap Item", {
    // Triggered when a new row is added to the Scrap Items table
    scrap_items_add(frm, cdt, cdn) {
        set_scrap_item_code(frm, cdt, cdn);
    }
});

// Function to set the Scrap Item Code and Name to the Production Item value when a new row is added
function set_scrap_item_code(frm, cdt, cdn) {
    const production_item = frm.doc.production_item; // Get the Production Item from the parent Job Card
    const production_item_name = frm.doc.custom_production_item_name; // Get the Production Item Name

    if (production_item) {
        // Set the 'item_code' and 'item_name' for the new row
        frappe.model.set_value(cdt, cdn, 'item_code', production_item);
        frappe.model.set_value(cdt, cdn, 'item_name', production_item_name);
    }
}

function update_custom_total_hours(frm, start_field, end_field, output_field) {
    let start_date = frm.doc[start_field], end_date = frm.doc[end_field];
    
    if (start_date && end_date) {
        let total_seconds = Math.floor((new Date(end_date) - new Date(start_date)) / 1000);
        let hours = String(Math.floor(total_seconds / 3600)).padStart(2, '0');
        let minutes = String(Math.floor((total_seconds % 3600) / 60)).padStart(2, '0');
        let seconds = String(total_seconds % 60).padStart(2, '0');
        
        frm.set_value(output_field, `${hours}:${minutes}:${seconds}`);
    } else {
        frm.set_value(output_field, null);
    }
}

function calculate_weight_or_unit(frm, source_field, target_field, is_unit_to_weight) {
    if (frm.doc.production_item && frm.doc[source_field]) {
        frappe.db.get_value('Item', { 'item_code': frm.doc.production_item }, 'weight_per_unit', ({ weight_per_unit }) => {
            if (weight_per_unit) {
                console.log('weight_per_unit', weight_per_unit);
                console.log('source_field', source_field, frm.doc[source_field]);
                console.log('target_field', target_field, frm.doc[target_field]);

                let calculated_value = is_unit_to_weight
                    ? (frm.doc[source_field] / weight_per_unit).toFixed(2)
                    : (frm.doc[source_field] * weight_per_unit).toFixed(2);
                
                console.log('calculated_value', calculated_value);

                if (frm.doc[target_field] != calculated_value) {
                    frm.set_value(target_field, calculated_value);
                }
            }
        });
    }
}
