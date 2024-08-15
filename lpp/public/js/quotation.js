frappe.ui.form.on("Quotation", {
    refresh: function (frm) {
        frm.set_value("valid_till", frappe.datetime.add_months(frm.doc.transaction_date, 12));
    },
});
/*
    frappe.ui.form.on('Payment Schedule', {
        payment_term(frm, cdt, cdn) {
            let row = frappe.get_doc(cdt, cdn);
            row.invoice_portion = 100;
            
            frm.refresh_field('payment_schedule');
        }
    })
*/