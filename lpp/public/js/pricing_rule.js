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
