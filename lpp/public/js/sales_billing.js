frappe.ui.form.on('Sales Billing', {
    refresh: function(frm) {
        frm.add_custom_button(__('Create Journal Entry'), function() {
            make_journal_entry(frm);
        });
    }
});

function make_journal_entry(frm) {    
    frappe.call({
        method: "make_journal_entry",
        doc: frm.doc,
        callback: function(r) {
            if (r.message) {
                var doclist = frappe.model.sync(r.message);                
                frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
            }
        }
    });
}