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
    },

    refresh(frm, cdt, cdn) {
        get_address_title(frm, cdt, cdn)
    }

    
});


frappe.ui.form.on('Dynamic Link', {
    link_name: async function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
    
        // Proceed only if row index is 1
        if (row.idx !== 1) return;
    
        // Map of doctype to the corresponding field to fetch
        const doctype_to_map = {
            Customer: 'customer_name',
            Supplier: 'supplier_name',
        };
    
        // Check if the row's link_doctype has a corresponding field
        const doctype_field = doctype_to_map[row.link_doctype];
    
        if (doctype_field) {
            const { message } = await frappe.db.get_value(row.link_doctype, row.link_name, [doctype_field]);
            frm.set_value('address_title', message[doctype_field]);
        } else {
            frm.set_value('address_title', row.link_name);
        }
    
        frm.refresh_field('address_title');
    }
});


async function get_address_title (frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    
    if (row.links.length === 0) return;

    let link = row.links[0];
    const doctype_to_map = {
        Customer: 'customer_name',
        Supplier: 'supplier_name',
    };

    // Check if the row's link_doctype has a corresponding field
    const doctype_field = doctype_to_map[link.link_doctype];

    if (doctype_field) {
        const { message } = await frappe.db.get_value(link.link_doctype, link.link_name, [doctype_field]);
        frm.set_value('address_title', message[doctype_field]);
    } else {
        frm.set_value('address_title', link.link_name);
    }

    frm.refresh_field('address_title');
}