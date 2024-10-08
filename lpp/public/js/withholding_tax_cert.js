frappe.ui.form.on("Withholding Tax Cert", {
    supplier(frm) {
        if (frm.doc.supplier) {
            frappe.db.get_list('Address', {
                filters: {
                    address_title: frm.doc.supplier_name
                },
                fields: ['name', 'address_line1', 'city', 'state', 'country', 'pincode'],
                limit: 1
            }).then(addresses => {
                if (addresses.length > 0) {
                    let address = addresses[0];
                    frm.set_value('supplier_address', address.name);
                } else {
                    frappe.msgprint(__('No address found for this supplier.'));
                }
            });
        }
    }
})