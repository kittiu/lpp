frappe.ui.form.on("Pricing Rule", {
    refresh(frm) {
        if(!frm.doc.valid_upto){
            frm.set_value("valid_upto", frappe.datetime.add_months(frm.doc.transaction_date, 12));
        }
    }
})