frappe.ui.form.on("Work Order", {
    refresh(frm) {
        // Get today's date
        let today = frappe.datetime.nowdate();
        
        // Set 'custom_mfg_date' field to today's date by default
        frm.set_value("custom_mfg_date", today);
        
        // Add 12 months to today's date and set the 'custom_exp_date' field
        frm.set_value("custom_exp_date", frappe.datetime.add_months(today, 12));

        // Calculate total run cards
        calculate_total_run_cards(frm);
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
    custom_ordered_quantity(frm){
        calculate_total_run_cards(frm);
        frm.set_value("qty", frm.doc.custom_ordered_quantity);
    },
    custom_quantity__run_card(frm) {
        calculate_total_run_cards(frm);  // Call the function to calculate when custom_quantity__run_card changes
    },
    production_item(frm) {
        // Check if production_item exists, then fetch batch details
        if (frm.doc.production_item) {
            frappe.db.get_value("Batch", { item: frm.doc.production_item }, "batch_id")
                .then(({ message }) => {
                    if (message) {
                        frm.set_value("custom_lot_no", message.batch_id);
                    }
                })
                .catch(err => {
                    console.error("Error fetching batch details:", err);
                    frappe.msgprint({
                        title: __('Error'),
                        indicator: 'red',
                        message: __('Unable to fetch batch details.')
                    });
                });
        }
    }
});


frappe.ui.form.on('Work Order Item', {
    item_code: async function(frm, cdt, cdn) {
        update_invoice_portion(frm);
    },
    required_qty: function(frm, cdt, cdn) {
        update_invoice_portion(frm);
    },
    custom_invoice_portion_ : function(frm, cdt, cdn) {
        update_invoice_portion(frm);
    },
    required_items_remove(frm, cdt, cdn) {
        update_invoice_portion(frm);
    },
});


function update_invoice_portion (frm) {
    
    let total_qty = 0;

    // คำนวณ total cost ของวัตถุดิบทั้งหมด
    frm.doc.required_items.forEach(i => {        
        total_qty += i.required_qty;
    });

    // คำนวณและอัพเดต Invoice Portion % สำหรับแต่ละวัตถุดิบ
    frm.doc.required_items.forEach(item => {
        if (total_qty > 0) {
            
            invoice_portion = (item.required_qty/ total_qty) * 100;
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
    console.log(qty, custom_quantity_run_card);
    
    // Handle division safely: Check if custom_quantity_run_card is greater than 0 to avoid division by zero
    if (custom_quantity_run_card > 0) {
        // Calculate and round to 2 decimal places using toFixed(2)
        let total_run_cards = (qty / custom_quantity_run_card).toFixed(2);
        
        frm.set_value("custom_total_run_cards", Math.ceil(total_run_cards));
    } else {
        frm.set_value("custom_total_run_cards", 0);  // Set total run cards to 0 if invalid division
    }
}

