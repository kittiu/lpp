frappe.ui.form.on("Purchase Receipt", {
    refresh(frm) {
        frm.set_df_property('posting_time', 'hidden', true);
    }
})