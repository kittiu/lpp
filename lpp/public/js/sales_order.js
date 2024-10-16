
// Trigger events for the Job Card doctype
frappe.ui.form.on("Sales Order", {
    refresh(frm) {
        
    },
    po_no(frm){
        update_items(frm)
    },
    po_date(frm){
        update_items(frm)
    },
    delivery_date(frm){
        update_items(frm)
    }
});

// Function to update 'item_code' and 'item_name' in all rows of 'scrap_items' child table
function update_items(frm) {
    const po_no = frm.doc.po_no; 
    const po_date = frm.doc.po_date; 
    const delivery_date = frm.doc.delivery_date;

    if (po_no || po_date || delivery_date) {
        // Loop through each row in the 'scrap_items' child table
        frm.doc.items.forEach(row => {
            // Set the 'item_code' and 'item_name' to match the Production Item
            row.custom_po_no = po_no;
            row.custom_po_date = po_date;
            row.delivery_date = delivery_date;
        });
        // Refresh the child table to reflect changes
        frm.refresh_field("items");
    }
}

// Trigger events for the child table 'Job Card Scrap Item'
frappe.ui.form.on("Sales Order Item", {
    // Triggered when a new row is added to the Scrap Items table
    items_add(frm, cdt, cdn) {
        set_value_item(frm, cdt, cdn);
    }
});

// Function to set the Scrap Item Code and Name to the Production Item value when a new row is added
function set_value_item(frm, cdt, cdn) {
    const po_no = frm.doc.po_no; 
    const po_date = frm.doc.po_date; 
    const delivery_date = frm.doc.delivery_date;

    console.log(po_no, po_date, delivery_date);
    
    if (po_no || po_date || delivery_date) {
        frappe.model.set_value(cdt, cdn, 'custom_po_no', po_no);
        frappe.model.set_value(cdt, cdn, 'custom_po_date', po_date);
        frappe.model.set_value(cdt, cdn, 'delivery_date', delivery_date);
    }
}
