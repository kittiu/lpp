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
    party_name(frm) {
        // ตรวจสอบว่า party_name มีข้อมูล และ quotation_to เป็น Customer
        if (frm.doc.party_name && frm.doc.quotation_to === "Customer") {
            // เรียกข้อมูลจาก DocType Customer
            frappe.db.get_value('Customer', frm.doc.party_name, 'custom_sales_tax_and_charge', (r) => {
                if (r && r.custom_sales_tax_and_charge) {
                    // เซ็ตค่าที่ taxes_and_charges
                    frm.set_value('taxes_and_charges', r.custom_sales_tax_and_charge);
                }
            });
        }
    }
});
frappe.listview_settings['Quotation'] = {
    onload: function(listview) {
        // Check if 'columns' is accessible and iterable
        if (listview && listview.columns && Array.isArray(listview.columns)) {
            listview.columns.forEach(field => {
                if (field.df && field.df.label === "Progress") {
                    field.df.fieldname = 'status';
                }
            });

            listview.refresh(); // Refresh the list to apply changes
        }
    }
};