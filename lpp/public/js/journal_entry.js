frappe.ui.form.on('Journal Entry', {
    onload: function(frm) {
        frm.set_query('custom_party_type', function() {
            return {
                filters: [
                    ['DocType', 'name', 'in', ['Customer', 'Supplier']]
                ]
            };
        });
    }
});