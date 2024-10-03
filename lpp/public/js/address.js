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
