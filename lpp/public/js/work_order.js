frappe.ui.form.on("Work Order", {
    refresh(frm) {
        // Code for refresh event (if needed)
    },

    custom_customer_item(frm) {
        // Check if custom_customer_item exists, then fetch customer_name
        if (frm.doc.custom_customer_item) {
            frappe.db.get_value("Customer", frm.doc.custom_customer_item, "customer_name")
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

