frappe.ui.form.on("Quotation", {
    refresh: function (frm) {
        frm.set_value("valid_till", frappe.datetime.add_months(frm.doc.transaction_date, 3));
    },
});