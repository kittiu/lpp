frappe.ui.form.on('Journal Entry', {
    onload: function(frm) {
        frm.set_query('custom_party_type', function() {
            return {
                filters: [
                    ['DocType', 'name', 'in', ['Customer', 'Supplier']]
                ]
            };
        });
    }
});

frappe.ui.form.on('Journal Entry Tax Invoice Detail', {
    custom_party_code(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        
        if (["Customer", "Supplier"].includes(row.custom_type) && row.custom_party_code) {
            get_name_for_tax_invoice(row);
        }
    },
    custom_type(frm, cdt, cdn) {
        // เมื่อ custom_type เปลี่ยนแปลง เคลียร์ค่าของ custom_party_code และ custom_party_name_custom
        let row = locals[cdt][cdn];
        if (row.custom_party_code || row.custom_party_name_custom) {  
            frappe.model.set_value(cdt, cdn, "custom_party_code", "");
            frappe.model.set_value(cdt, cdn, "custom_party_name_custom", "");
        }
    },
    custom_tax_amount_custom(frm) {
        calculate_custom_total(frm)
    }
});

frappe.ui.form.on('Journal Entry Account', {
    account(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (frm.doc.custom_type) {
            if (frm.doc.custom_type.includes('ภาษีซื้อ') && row.account.includes('ภาษีซื้อ')) {
                frappe.model.set_value(cdt, cdn, 'debit_in_account_currency', frm.doc.custom_total);
                frappe.model.set_value(cdt, cdn, 'credit_in_account_currency', 0); 
            } else if (frm.doc.custom_type.includes('ภาษีขาย') && row.account.includes('ภาษีขาย')) {
                frappe.model.set_value(cdt, cdn, 'credit_in_account_currency', frm.doc.custom_total);
                frappe.model.set_value(cdt, cdn, 'debit_in_account_currency', 0);
            } else {
                console.log('No matching account or custom_type found');
            }
        } else {
            console.log('custom_type is missing');
        }
    }
});

function get_name_for_tax_invoice(frm) {
    let doctype = frm.custom_type === "Customer" ? "Customer" : "Supplier";
    let custom_party_code = frm.custom_party_code

    frappe.db.get_doc(doctype, custom_party_code)
        .then(doc => {
            frappe.model.set_value(frm.doctype, frm.name, "custom_party_name_custom", doc.customer_name || doc.supplier_name);
        })
        .catch(err => {
            console.error("Error fetching custom molds items:", err);
                frappe.msgprint({
                    title: __('Error'),
                    indicator: 'red',
                    message: __('Unable to fetch custom molds items.')
                });
        })
}

function calculate_custom_total(frm) {
    let total = 0;

    // วนลูปเช็คค่า custom_tax_amount_custom ในแต่ละ row
    frm.doc.tax_invoice_details.forEach(row => {
        if (row.custom_tax_amount_custom) {
            total += flt(row.custom_tax_amount_custom);
        }
    });
    // // อัพเดตค่าในฟิลด์ custom_total ด้วยผลรวม
    frm.set_value('custom_total', total);
}