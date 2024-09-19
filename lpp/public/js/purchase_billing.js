frappe.ui.form.on('Purchase Billing', {
    refresh: function (frm) {
        frm.add_custom_button(__('Create Journal Entry'), function () {
            make_journal_entry(frm);
        });
    },
    get_purchase_invoices: function (frm) {
        
        if (frm.doc.threshold_date) {
            return frm.call({
                method: "get_purchase_invoices_in_month",
                doc: frm.doc,
                args: {
                    supplier: frm.doc.supplier,
                    currency: frm.doc.currency,
                    tax_type: frm.doc.tax_type,
                    threshold_type: frm.doc.threshold_type,
                    threshold_date: frm.doc.threshold_date
                },
                callback: function (r) {
                    console.log("get_purchase_invoices_in_month", r);
                    let invoices = []
                    for (let i of r.message) {
                        invoices.push({ purchase_invoice: i })
                    }
                    frm.set_value("purchase_billing_line", invoices)
                    frm.set_value("invoice_count", invoices.length)
                    frm.refresh_field('purchase_billing_line');
                }
            });
        }
    }

});

function make_journal_entry(frm) {
    frappe.call({
        method: "make_journal_entry",
        doc: frm.doc,
        callback: function (r) {
            if (r.message) {
                var doclist = frappe.model.sync(r.message);
                frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
            }
        }
    });
}