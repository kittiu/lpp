
// Trigger events for the Job Card doctype
frappe.ui.form.on("Sales Order", {
    refresh(frm) {
        frm.set_df_property('po_no', 'hidden', 0);
        frm.set_df_property('po_date', 'hidden', 0);
    },
    onload: function(frm) {
        frm.fields_dict.items.grid.toggle_display("item_name", false);  // ซ่อนฟิลด์ item_name
    },
    po_no(frm){
        update_items(frm)
    },
    po_date(frm){
        update_items(frm)
    },
    delivery_date(frm){
        update_items(frm)
    },
    customer(frm){
        // เมื่อเลือก Customer ใหม่ ให้เคลียร์ตาราง Sales Taxes and Charges
        frm.clear_table('taxes');  // ชื่อตาราง Sales Taxes and Charges คือ 'taxes'
        frm.refresh_field('taxes');  // รีเฟรชฟิลด์เพื่อแสดงการเปลี่ยนแปลงบนหน้าจอ
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
