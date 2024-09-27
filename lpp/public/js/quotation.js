frappe.ui.form.on("Quotation", {
    onload: function(frm) {
        // Set proposer field to the user who created the document if the field is empty
        if (!frm.doc.custom_proposer) {
            frm.set_value('custom_proposer', frappe.session.user);
        }
    },
    refresh: function (frm) {
        if(!frm.doc.valid_till){
            frm.set_value("valid_till", frappe.datetime.add_months(frm.doc.transaction_date, 12));
        }
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