frappe.ui.form.on("Work Order", {
    onload_post_render: function(frm) {
        if (frappe.router.doctype === 'Work Order' && frappe.router.page === 'print') {
            // Hide the PDF button in the print format
            $('button[data-label="PDF"]').hide();
        }
    },
    refresh(frm) {
        // Get today's date
        let today = frappe.datetime.nowdate();

        // Set 'custom_mfg_date' field to today's date by default
        frm.set_value("custom_mfg_date", today);

        // Add 12 months to today's date and set the 'custom_exp_date' field
        if(!frm.doc.custom_exp_date){
            frm.set_value("custom_exp_date", frappe.datetime.add_months(today, 12));
        }

        // Calculate total run cards
        calculate_total_run_cards(frm);

        set_custom_item_molds_query(frm)

        update_custom_jobcard_remaining(frm)

        update_invoice_portion(frm);

        setTimeout(() => {
            if (frm.custom_buttons && frm.custom_buttons[('Create Job Card')]) {
                // Remove Original Button
                frm.remove_custom_button(__('Create Job Card'))
                frm.add_custom_button(__("Create Job Card"), () => {
                    frm.trigger("make_job_card_custom");
                }).addClass("btn-primary");
            }
        }, 10);
    },
    setup: async function(frm) {
        try {
            // เช็คว่า Sales Order มีค่าและฟิลด์ customer ยังไม่มีข้อมูล
            if (frm.doc.sales_order && !frm.doc.custom_customer) {
                const { message } = await frappe.db.get_value("Sales Order", frm.doc.sales_order, "customer");
                if (message && message.customer) {
                    frm.set_value("custom_customer", message.customer);
                }
            }
    
            // ตั้งค่า custom_required_quantity ถ้ายังไม่มีค่า แต่มีค่า custom_ordered_quantity และ Sales Order มีค่า
            if (frm.doc.sales_order && !frm.doc.custom_required_quantity && frm.doc.custom_ordered_quantity) {
                frm.set_value("custom_required_quantity", frm.doc.custom_ordered_quantity);
            }
        } catch (err) {
            console.error("Error fetching customer:", err);
            frappe.msgprint({
                title: __('Error'),
                indicator: 'red',
                message: __('Unable to fetch customer.')
            });
        }
    },
    
    custom_customer(frm) {
        // Check if custom_customer exists, then fetch customer_name
        if (frm.doc.custom_customer) {
            frappe.db.get_value("Customer", frm.doc.custom_customer, "customer_name")
                .then(({ message }) => {
                    if (message) {
                        frm.set_value("custom_customer_on_label", message.customer_name);
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
        calculate_total_run_cards(frm);
        frm.set_value("qty", frm.doc.custom_ordered_quantity);
    },
    custom_quantity__run_card(frm) {
        calculate_total_run_cards(frm);  // Call the function to calculate when custom_quantity__run_card changes
    },
    production_item(frm) {
        set_custom_item_molds_query(frm)
    },

    make_job_card_custom: function (frm) {
		let qty = 0;
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

		var pending_qty = 0;
		frm.doc.operations.forEach((data) => {
			if (data.completed_qty + data.process_loss_qty != frm.doc.qty) {
				pending_qty = frm.doc.qty - flt(data.completed_qty) - flt(data.process_loss_qty);

				if (pending_qty) {
					dialog.fields_dict.operations.df.data.push({
						name: data.name,
						operation: data.operation,
						workstation: data.workstation,
						batch_size: data.batch_size,
						qty: pending_qty,
						pending_qty: pending_qty,
						sequence_id: data.sequence_id,
					});
				}
			}
		});
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

    // Check if 'production_item' is present
    if (frm.doc.production_item) {
        // Fetch the 'Item' document corresponding to the 'production_item' field
        frappe.db.get_doc('Item', frm.doc.production_item)
            .then(doc => {
                // Check if the 'Item' document and its 'custom_molds_items' child table exist
                if (doc && doc.custom_molds_items) {
                    // Extract 'name_molds' from each row in the 'custom_molds_items' child table
                    let molds_items = doc.custom_molds_items.map(row => row.name_molds);

                    // Set a query on the 'custom_item_molds' field to filter options based on 'molds_items'
                    frm.set_query('custom_item_molds', () => ({
                        filters: [
                            ['Molds', 'name_molds', 'in', molds_items]
                        ]
                    }));
                } else {
                    // Clear the filter if no molds are found
                    clear_custom_item_molds_filter(frm);
                }
            })
            .catch(err => {
                // Log any errors to the console and notify the user
                console.error("Error fetching custom molds items:", err);
                frappe.msgprint({
                    title: __('Error'),
                    indicator: 'red',
                    message: __('Unable to fetch custom molds items.')
                });
                // Clear the filter on error
                clear_custom_item_molds_filter(frm);
            });
    } else {
        // Clear filter if 'production_item' is empty
        clear_custom_item_molds_filter(frm);
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

        frm.set_value("custom_total_run_cards", Math.ceil(total_run_cards));
    } else {
        frm.set_value("custom_total_run_cards", 0);  // Set total run cards to 0 if invalid division
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
                if (response.message) {
                    frm.set_value("custom_jobcard_remaining", response.message);
                }
            }
        });
    } else {
        frm.set_value("custom_jobcard_remaining", 0);
    }
}