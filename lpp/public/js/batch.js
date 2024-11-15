frappe.ui.form.on("Batch", {
    // On form refresh
    refresh(frm) {
        setup_batch_form(frm);
        add_generate_lot_no_button(frm);
    },
    // Triggered when 'custom_lot_type' field changes
    custom_lot_type(frm) {
        setup_batch_form(frm);
        frm.set_value("batch_id", "");  // Reset batch ID
    },
    // Triggered when 'custom_rescreen' field changes
    custom_rescreen(frm) {
        frm.set_value("batch_id", "");  // Reset batch ID on custom_rescreen change
    },
    // Triggered when 'item' field changes
    item(frm) {
        frm.set_value("batch_id", "");  // Reset batch ID on item change
    },
    // Triggered when 'customer_customer' field changes
    customer_customer(frm) {
        const isBuying = frm.doc.custom_lot_type === "Buying";
        frm.set_value("item", null);  // Reset item selection
        set_item_filter(frm, isBuying);  // Update item filter based on custom_lot_type
    }
});

// Main setup function to configure form based on custom_lot_type
function setup_batch_form(frm) {
    const isBuying = frm.doc.custom_lot_type === "Buying";

    // Configure supplier and custom_rescreen fields based on lot type
    frm.set_df_property("supplier", "read_only", 0);
    frm.set_df_property("supplier", "hidden", !isBuying);
    frm.set_df_property("custom_rescreen", "read_only", isBuying);

    // Set custom_rescreen and expiry_date values conditionally
    const custom_rescreen = isBuying ? 0 : frm.doc.custom_rescreen;
    const expiry_date = frappe.datetime.add_months(frm.doc.transaction_date, isBuying ? 12 : 24);

    if (custom_rescreen !== frm.doc.custom_rescreen) {
        frm.set_value("custom_rescreen", custom_rescreen);
    }
    if (expiry_date !== frm.doc.expiry_date) {
        frm.set_value("expiry_date", expiry_date);
    }

    // Set item filter
    set_item_filter(frm, isBuying);
}

// Function to set item filter based on custom_lot_type
function set_item_filter(frm, isBuying) {
    frm.set_query("item", !isBuying ? () => ({
        filters: [["Item", "customer_name", "=", frm.doc.custom_customer]]
    }) : null);  // Clear filter if not Buying
}

// Adds a custom button to generate batch number if lot_no is not set
function add_generate_lot_no_button(frm) {
    setTimeout(() => {
        if (!frm.doc.lot_no) {
            frm.add_custom_button("Generate Batch No.", () => {
                if (!frm.doc.item) {
                    frappe.msgprint("Please Select Item First");
                    return;
                }
                // Call the 'gen_lot_no' method to generate lot number
                frm.call({
                    method: "gen_lot_no",
                    doc: frm.doc,
                    callback(r) {
                        frm.set_value("batch_id", r.message);
                    }
                });
            });
        }
    }, 10);
}
