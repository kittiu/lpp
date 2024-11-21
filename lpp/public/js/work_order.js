frappe.ui.form.on("Work Order", {
    refresh(frm) {        
        frm.set_df_property('status', 'hidden', 0);
        frm.set_df_property('company', 'hidden', 0);

        // Get today's date
        let today = frappe.datetime.nowdate();
        if (frm.is_new()) {
            // Set 'custom_mfg_date' field to today's date by default
            if(!frm.doc.custom_mfg_date){
                frm.set_value("custom_mfg_date", today);
            }

            // Add 12 months to today's date and set the 'custom_exp_date' field
            if(!frm.doc.custom_exp_date){
                frm.set_value("custom_exp_date", frappe.datetime.add_months(today, 12));
            }
        }
     

        // Calculate total run cards
        calculate_total_run_cards(frm);

        set_custom_item_molds_query(frm)

        update_custom_jobcard_remaining(frm)

        update_invoice_portion(frm);

        setup_custom_fields(frm);

        setTimeout(() => {
            if (frm.custom_buttons && frm.custom_buttons[('Create Job Card')]) {
                // Remove Original Button
                frm.remove_custom_button(__('Create Job Card'))
                frm.add_custom_button(__("Create Job Card"), () => {
                    frm.trigger("make_job_card_custom");
                }).addClass("btn-primary");
            }
        }, 10);

        set_item_code_query(frm);
        frm.refresh_field("items"); // รีเฟรช child table เมื่อ customer_name เปลี่ยน
    },
    
    custom_customer(frm) {
        // Check if custom_customer exists, then fetch customer_name
        if (frm.doc.custom_customer) {
            frappe.db.get_value("Customer", frm.doc.custom_customer, "customer_name")
                .then(({ message }) => {
                    if (message) {
                        frm.set_value("custom_customer_on_label", message.customer_name);
                        set_item_code_query(frm);
                        frm.refresh_field("items"); // รีเฟรช child table เมื่อ customer_name เปลี่ยน
                    }
                })
                .catch(err => {
                    console.error("Error fetching customer name:", err);
                    frappe.msgprint({
                        title: __('Error'),
                        indicator: 'red',
                        message: __('Unable to fetch customer name.')
                    });
                });
        }
    },
    custom_ordered_quantity(frm) {
        if(frm.doc.custom_ordered_quantity != frm.doc.qty){
            frm.set_value("qty", frm.doc.custom_ordered_quantity);
        }
        calculate_total_run_cards(frm);
    },
    custom_quantity__run_card(frm) {
        calculate_total_run_cards(frm);  // Call the function to calculate when custom_quantity__run_card changes
    },
    production_item(frm) {
        set_custom_item_molds_query(frm)
    },

    make_job_card_custom: async function (frm) {
        let operations_data = [];
        const dialog = frappe.prompt(
            {
                fieldname: "operations",
                fieldtype: "Table",
                label: __("Operations"),
                fields: [
                    {
                        fieldtype: "Link",
                        fieldname: "operation",
                        label: __("Workstation"),
                        read_only: 1,
                        in_list_view: 1,
                    },
                    {
                        fieldtype: "Link",
                        fieldname: "workstation",
                        label: __("Machine"),
                        read_only: 1,
                        in_list_view: 1,
                    },
                    {
                        fieldtype: "Data",
                        fieldname: "name",
                        label: __("Operation Id"),
                    },
                    {
                        fieldtype: "Float",
                        fieldname: "pending_qty",
                        label: __("Pending Qty"),
                    },
                    {
                        fieldtype: "Float",
                        fieldname: "qty",
                        label: __("Quantity to Manufacture"),
                        read_only: 0,
                        in_list_view: 1,
                    },
                    {
                        fieldtype: "Float",
                        fieldname: "batch_size",
                        label: __("Batch Size"),
                        read_only: 1,
                    },
                    {
                        fieldtype: "Int",
                        fieldname: "sequence_id",
                        label: __("Sequence Id"),
                        read_only: 1,
                    },
                ],
                data: operations_data,
                in_place_edit: true,
                get_data: function () {
                    return operations_data;
                },
            },
            function (data) {
                frappe.call({
                    method: "lpp.custom.work_order.make_job_card",
                    freeze: true,
                    args: {
                        work_order: frm.doc,
                        operations: data.operations,
                    },
                    callback: function () {
                        frm.reload_doc();
                    },
                });
            },
            __("Job Card"),
            __("Create")
        );
    
        dialog.fields_dict["operations"].grid.wrapper.find(".grid-add-row").hide();
    
        let quantity__run_card = parseInt(frm.doc.custom_quantity__run_card);
    
        // Fetch all Job Card data upfront
        const job_cards_response = await frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Job Card",
                filters: { work_order: frm.doc.name },
                fields: ["operation", "custom_runcard_no", "for_quantity", "total_completed_qty"],
            },
        });

        const job_cards = job_cards_response.message || [];
        
        // Iterate through operations
        for (let index = 0; index < frm.doc.operations.length; index++) {
            const data = frm.doc.operations[index];
            let qty = 0;

            // Group job cards by operation
            const filter_operation_cards = job_cards.filter(card => card.operation === data.operation);
            const operation_cards = aggregateJobCards(filter_operation_cards);

            if (index > 0) {
                const prev_operation = frm.doc.operations[index - 1];
                const filter_prev_operation_cards = job_cards.filter(
                    (card) => card.operation === prev_operation.operation
                );
                const prev_operation_cards = aggregateJobCards(filter_prev_operation_cards);
                const prev_card_map = prev_operation_cards?.reduce((map, card) => {
                    map[card.custom_runcard_no] = card;
                    return map;
                }, {});

                if(prev_operation_cards?.length > operation_cards?.length){                    
                    qty = getSumOfMaxRuncard(prev_operation_cards, prev_operation.operation, "total_completed_qty")
                }

                else { 
                    operation_cards.forEach(runcard => {
                        const prev_card = prev_card_map[runcard.custom_runcard_no];
                            
                        if (prev_card) {
                            if (prev_card.total_completed_qty !== runcard.for_quantity) {                            
                                // Calculate sums
                                const prev_operation_completed_qty = getSumOfMaxRuncard(prev_operation_cards, prev_operation.operation, "total_completed_qty", runcard.custom_runcard_no);
                                const current_operation_for_qty = getSumOfMaxRuncard(operation_cards, data.operation, "for_quantity", runcard.custom_runcard_no);

                                // Calculate qty
                                qty = prev_operation_completed_qty == 0 ? current_operation_for_qty : prev_operation_completed_qty - current_operation_for_qty;
                                return
                            }
                        }
                    });
                }
            } else {
                // First operation logic
                const sum_operation = getSumOfMaxRuncard(operation_cards, data.operation, "for_quantity");
                qty = sum_operation !== quantity__run_card ? sum_operation > quantity__run_card ? 0 : quantity__run_card - sum_operation : quantity__run_card;
            }
            
            // Push operation data
            operations_data.push({
                name: data.name,
                operation: data.operation,
                workstation: data.workstation,
                batch_size: data.batch_size,
                qty: qty,
                pending_qty: qty,
                sequence_id: data.sequence_id,
            });
        }
    
        dialog.fields_dict.operations.grid.refresh();
    },
    
});


frappe.ui.form.on('Work Order Item', {
    item_code: async function (frm, cdt, cdn) {
        update_invoice_portion(frm);
    },
    required_qty: function (frm, cdt, cdn) {
        update_invoice_portion(frm);
    },
    custom_invoice_portion_: function (frm, cdt, cdn) {
        update_invoice_portion(frm);
    },
    required_items_remove(frm, cdt, cdn) {
        update_invoice_portion(frm);
    },
});

function set_custom_item_molds_query(frm) {
    if (frm.doc.production_item) {
        frappe.call({
            method: "lpp.custom.work_order.get_item_molds",  // The path to your Python method
            args: {
                item_code: frm.doc.production_item  // Pass the item code from the form
            },
            callback: function(r) {
                if (r.message) {
                    let options = r.message.map(mold => {
                        return {
                            label: `${mold.mold_id}, ${mold.item_name}`,  // Display both mold_name and mold_size
                            value: mold.mold_id  // You can use the mold_name or any unique field as the value
                        };
                    });
                    // Set the options for custom_item_mold field
                    frm.set_df_property('custom_item_mold', 'options', options || []);
                }
            }
        });
    }
}

// Helper function to clear 'custom_item_molds' filters
function clear_custom_item_molds_filter(frm) {
    frm.set_query('custom_item_molds', () => ({
        filters: [
            ['Molds', 'name_molds', '=', 'empty']
        ]
    }));
}


function update_invoice_portion(frm) {

    let total_qty = 0;

    // คำนวณ total cost ของวัตถุดิบทั้งหมด
    frm.doc.required_items.forEach(i => {
        total_qty += i.required_qty;
    });

    // คำนวณและอัพเดต Invoice Portion % สำหรับแต่ละวัตถุดิบ
    frm.doc.required_items.forEach(item => {
        if (total_qty > 0) {

            invoice_portion = (item.required_qty / total_qty) * 100;
            item.custom_invoice_portion_ = invoice_portion;
        } else {

            item.custom_invoice_portion_ = 0;
        }
    });

    // รีเฟรชฟิลด์ของรายการวัตถุดิบเพื่อแสดงผลลัพธ์
    frm.refresh_field('required_items');
}

function calculate_total_run_cards(frm) {
    // Get values of qty and custom_quantity__run_card safely with default to 0
    let qty = frm.doc.custom_ordered_quantity || 0;
    let custom_quantity_run_card = frm.doc.custom_quantity__run_card || 0;

    // Handle division safely: Check if custom_quantity_run_card is greater than 0 to avoid division by zero
    if (custom_quantity_run_card > 0) {
        // Perform the division
        let total_run_cards = qty / custom_quantity_run_card;

        // Check if the result has a remainder (not an integer)
        if (total_run_cards % 1 !== 0) {
            // If not an integer, round up
            total_run_cards = Math.ceil(total_run_cards);
        }
        if(frm.doc.custom_total_run_cards != total_run_cards){
            frm.set_value("custom_total_run_cards", Math.ceil(total_run_cards));
        }
    } else {
        if(frm.doc.custom_total_run_cards != 0){
            frm.set_value("custom_total_run_cards", 0);
        }
    }
}

function update_custom_jobcard_remaining(frm) {    
    if(frm.doc.custom_total_run_cards && frm.doc.name && frm.doc.operations.length) {
        frm.call({
            method: 'lpp.custom.work_order.get_jobcard_remaining',
            args: {
                data: frm.doc
            },
            callback: function (response) {
                if (frm.doc.custom_jobcard_remaining != response.message) {
                    frm.set_value("custom_jobcard_remaining", response.message);
                }
            }
        });
    } else {
        frm.set_value("custom_jobcard_remaining", 0);
    }
}

async function setup_custom_fields(frm) {
    // เช็คว่า Sales Order มีค่าและฟิลด์ customer ยังไม่มีข้อมูล
    if (frm.doc.sales_order && !frm.doc.custom_customer) {
        const { message } = await frappe.db.get_value("Sales Order", frm.doc.sales_order, "customer");
        if (message && message.customer) {
            frm.set_value("custom_customer", message.customer);
        }
    }

    // ตั้งค่า custom_required_quantity, custom_ordered_quantity ถ้ายังไม่มีค่า แต่มีค่า Sales Order
    if (frm.doc.sales_order && frm.doc.custom_required_quantity === 0 && frm.doc.custom_ordered_quantity === 1) {                
        frm.set_value("custom_required_quantity", frm.doc.qty);
        frm.set_value("custom_ordered_quantity", frm.doc.qty);
    }
}

function getSumOfMaxRuncard(jobCards, operation, key, maxRuncard) {
    if (!jobCards || !jobCards.length) {
        return 0; // Fallback value
    }

    // Group by custom_runcard_no and calculate sum of the given key
    const grouped = jobCards
        ?.filter(c => c.operation === operation)
        ?.reduce((acc, { custom_runcard_no, [key]: value }) => {
            if (!custom_runcard_no || value == null) return acc; // Handle invalid data
            acc[custom_runcard_no] = (acc[custom_runcard_no] || 0) + value;
            return acc;
        }, {}); // Provide an empty object as the initial value

    // If maxRuncard is provided, use it directly; otherwise, calculate it
    if (!maxRuncard) {
        maxRuncard = Object.keys(grouped)?.reduce((max, runcard) => {
            const current = parseInt(runcard.split("/")[0], 10);
            const maxVal = parseInt(max.split("/")[0], 10);
            return current > maxVal ? runcard : max;
        });
    }

    // Return the sum for the given maxRuncard
    return grouped[maxRuncard];
}

function aggregateJobCards(jobCards) {
    const aggregated = jobCards?.reduce((acc, card) => {
        const key = `${card.operation}_${card.custom_runcard_no}`;
        if (!acc[key]) {
            acc[key] = { ...card };
        } else {
            acc[key].for_quantity += card.for_quantity;
            acc[key].total_completed_qty += card.total_completed_qty;
        }
        return acc;
    }, {});

    return Object.values(aggregated);
}

function set_item_code_query(frm) {    
    frm.set_query("production_item", function () {
        const party_name = frm.doc.custom_customer_on_label;
        return {
            query: "lpp.custom.custom_item.get_items_based_on_party_and_groups",
            filters: {
                party_name : party_name
            }
        };
    })
}