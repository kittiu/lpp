frappe.ui.form.on("Pricing Rule", {
    refresh(frm) {
        // Set the default value for 'valid_upto' if it's empty
        if (!frm.doc.valid_upto) {
            frm.set_value("valid_upto", frappe.datetime.add_months(frm.doc.transaction_date, 12));
        }

        // Hide the 'currency' field
        frm.set_df_property('currency', 'hidden', 1);

        // Update the title based on naming_series
        frm.trigger('update_title');
    },

    naming_series(frm) {
        frm.trigger('update_title');
    },

    update_title(frm) {
        frm.set_value("title", frm.doc.naming_series);
    }
});

frappe.ui.form.on("Pricing Rule Item Code", {
    item_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];  // Get the child table row
        if (row.item_code) {
            frappe.db.get_doc('Item', row.item_code)
            .then(doc => {
                if (doc.uoms && doc.uoms.length > 0) {
                    let first_uom = doc.uoms[0].uom;
                    console.log('First UOM:', first_uom);
                    frappe.model.set_value(cdt, cdn, 'uom', first_uom);  // Set the UOM field in the child table row
                } else {
                    console.log('No UOMs found for this item.');
                    frappe.model.set_value(cdt, cdn, 'uom', null);  // Clear UOM if none are found
                }
            })
            .catch(error => {
                console.error('Error fetching item document:', error);
            });
        }
    }
});
