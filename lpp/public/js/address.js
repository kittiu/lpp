frappe.ui.form.on('Address', {
    before_save: function(frm) {
        try {
            if (frm.doc.address_title && Array.isArray(frm.doc.links)) {
                frm.doc.links.forEach(function(link) {
                    if (link && link.link_title !== frm.doc.address_title) {
                        link.link_title = frm.doc.address_title;
                    }
                });
            }
        } catch (error) {
            console.error('Error updating link title:', error);
            frappe.msgprint(__('There was an error updating the link title. Please try again.'));
        }
    }
});


frappe.ui.form.on('Dynamic Link', {
    link_name: async function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
    
        // Proceed only if row index is 1
        if (row.idx !== 1) return;
    
        // Map of doctype to the corresponding field to fetch
        const doctypeFieldMap = {
            Customer: 'customer_name',
            Supplier: 'supplier_name',
        };
    
        // Check if the row's link_doctype has a corresponding field
        const fieldToFetch = doctypeFieldMap[row.link_doctype];
    
        if (fieldToFetch) {
            const { message } = await frappe.db.get_value(row.link_doctype, row.link_name, [fieldToFetch]);
            frm.set_value('address_title', message[fieldToFetch]);
        } else {
            frm.set_value('address_title', row.link_name);
        }
    
        frm.refresh_field('address_title');
    }
});