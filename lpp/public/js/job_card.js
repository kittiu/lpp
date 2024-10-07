// Trigger events for the Job Card doctype
frappe.ui.form.on("Job Card", {
    refresh(frm) {
        // Set 'item_code' and 'item_name' fields in 'scrap_items' child table to read-only
        frm.get_field("scrap_items").grid.toggle_enable("item_code", false);
        frm.get_field("scrap_items").grid.toggle_enable("item_name", false);
    },
    // Triggered when 'production_item' changes
    production_item(frm) {
        update_scrap_items(frm);
    },
    // Triggered when 'custom_production_item_name' changes
    custom_production_item_name(frm) {
        update_scrap_items(frm);
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
