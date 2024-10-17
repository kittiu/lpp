frappe.ui.form.on('Journal Entry', {
    // On load event of Journal Entry form
    onload: function(frm) {
        // If custom_journal_type is not set, clear the naming_series field
        if (!frm.doc.custom_journal_type) {
            frm.set_value('naming_series', '');  // Set naming_series to an empty string
        }

    },

    // Event triggered when the custom_journal_type field is updated
    custom_journal_type: function(frm) {
        if (frm.doc.custom_journal_type) {
            // Fetching the selected Journal Type document from the database
            frappe.db.get_doc('Journal Type', frm.doc.custom_journal_type)
            .then(doc => {
                // If naming_series exists in the Journal Type, set it in the Journal Entry
                if (doc.naming_series) {
                    frm.set_value('naming_series', doc.naming_series);
                } else {
                    frappe.msgprint(__('Naming series not found for this Journal Type'));  // Show message if no naming series
                }
            })
            .catch(error => {
                // Error handling for issues with fetching the Journal Type document
                frappe.msgprint(__('Error fetching Journal Type. Please check the selected Journal Type.'));
                console.error('Error fetching Journal Type:', error);
            });
        } else {
            // Clear naming_series if no Journal Type is selected
            frm.set_value('naming_series', '');  // Clear naming_series
            frappe.msgprint(__('Please select a valid Journal Type.'));  // Show message if Journal Type is not selected
        }
    },
    setup: async function (frm) {
        await update_custom_tax_amount_custom(frm);
        calculate_custom_total(frm);
    },
    custom_tax_charge_template: async function(frm) {
        await update_custom_tax_amount_custom(frm);
        calculate_custom_total(frm);
    }
});



frappe.ui.form.on('Journal Entry Tax Invoice Detail', {
    custom_party_code(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        
        if (["Customer", "Supplier"].includes(row.custom_type) && row.custom_party_code) {
            get_name_for_tax_invoice(row);
        }
        if(row.custom_party_code){
            if(row.custom_type === 'Supplier'){
                frappe.db.get_value('Supplier', row.custom_party_code, "tax_id", function (value) {
                    frappe.model.set_value(cdt, cdn, "custom_tax_id", value['tax_id']);
                });
            }else if(row.custom_type === 'Customer'){
                frappe.db.get_value('Customer', row.custom_party_code, "tax_id", function (value) {
                    frappe.model.set_value(cdt, cdn, "custom_tax_id", value['tax_id']);
                });
            }
       
        }
        
    },
    custom_type(frm, cdt, cdn) {
        // เมื่อ custom_type เปลี่ยนแปลง เคลียร์ค่าของ custom_party_code และ custom_party_name_custom
        let row = locals[cdt][cdn];
        if (row.custom_party_code || row.custom_party_name_custom) {  
            frappe.model.set_value(cdt, cdn, "custom_party_code", "");
            frappe.model.set_value(cdt, cdn, "custom_party_name_custom", "");
        }
        if (row.custom_tax_id ){
            frappe.model.set_value(cdt, cdn, "custom_tax_id", "");
        }
    },
    custom_tax_amount_custom(frm) {
        calculate_custom_total(frm)
    },
    custom_tax_base_amount_custom: async function(frm){
        await update_custom_tax_amount_custom(frm);
        calculate_custom_total(frm);
    }
});

frappe.ui.form.on('Journal Entry Account', {
    account(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (row.account) {
            if (row.account.includes('ภาษีซื้อ')) {
                frappe.model.set_value(cdt, cdn, 'debit_in_account_currency', frm.doc.custom_total);
                frappe.model.set_value(cdt, cdn, 'credit_in_account_currency', 0); 
            } else if (row.account.includes('ภาษีขาย')) {
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

async function update_custom_tax_amount_custom(frm) {
    try {        
        // Fetch rate from the linked Sales Taxes and Charges Template
        const [taxes_and_charges] = await frappe.db.get_list('Sales Taxes and Charges', {
            filters: {
                parent: frm.doc.custom_tax_charge_template,   // Link to the selected template
                parenttype: 'Sales Taxes and Charges Template' // Ensure correct parent type
            },
            fields: ['charge_type', 'rate'],  // Fetch only necessary fields
            limit: 1  // Fetch only one record, since you are using only the first rate
        });
        
        const tax_rate = taxes_and_charges.rate;

        // Update custom_tax_amount_custom for each row in tax_invoice_details
        frm.doc.tax_invoice_details.forEach(row => {
            if (row.custom_tax_base_amount_custom) {
                row.custom_tax_amount_custom = row.custom_tax_base_amount_custom * tax_rate;
            }
        });

        // Refresh the tax_invoice_details field after updates
        frm.refresh_field('tax_invoice_details');
        
    } catch (error) {
        console.error('Error fetching tax details:', error);
    }
}