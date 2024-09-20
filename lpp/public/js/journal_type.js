frappe.ui.form.on('Journal Type', {
    onload: function(frm) {
        frappe.call({
            method: "lpp.custom.journal_entry.get_journal_entry_naming_series",
            callback: function(r) {
                if (r.message) {
                    frm.set_df_property('naming_series', 'options', r.message);
                }
            }
        });
    }
});
