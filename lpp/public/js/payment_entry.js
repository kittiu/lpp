frappe.ui.form.on("Payment Entry", {
    onload(frm){
        if(frm.doc.custom_bill_no){
            frm.script_manager.trigger("payment_type");
            if(frm.doc.party && frm.is_new()){
                frm.script_manager.trigger("party");
            }
        }
    },
    after_save: function (frm) {
        // Fix the issue Advance Taxes and Charges not refreshed after saving
        frm.reload_doc();
    },
    refresh(frm) {
        frm.set_df_property('purchase_billing', 'read_only', 1);

        if (frm.is_new() && frm.doc.custom_bill_no && frm.doc.payment_type === "Pay") {
            frm.set_value('naming_series', 'BP.YY.MM.-.####.');
        }

        frm.set_query("reference_doctype", "references", function () {
            let doctypes = ["Journal Entry"];
            if (frm.doc.party_type == "Customer") {
                doctypes = ["Sales Billing","Sales Order", "Sales Invoice", "Journal Entry", "Dunning"];
            } else if (frm.doc.party_type == "Supplier") {
                doctypes = ["Purchase Billing","Purchase Order", "Purchase Invoice", "Journal Entry"];
            }
    
            return {
                filters: { name: ["in", doctypes] },
            };
        });
    },
    // Field change events to re-evaluate the condition
    docstatus: function(frm) { frm.trigger('set_field_visibility'); },
    payment_type: function(frm) { frm.trigger('set_field_visibility'); },
    party: function(frm) { frm.trigger('set_field_visibility'); },
    purchase_billing: function(frm) { frm.trigger('set_field_visibility'); },
    paid_from: function(frm) {
        retrieve_documents_based_on_payment_type(frm)
    },
    // Define the custom trigger for setting field visibility
    set_field_visibility: function(frm) {
        // Define the condition
        let condition = frm.doc.docstatus === 0 
                        && frm.doc.payment_type === "Pay" 
                        && frm.doc.party_type === "Supplier" 
                        && frm.doc.party;

        // Show or hide the field based on the condition
        frm.toggle_display('get_invoices_from_purchase_billing', condition);
        frm.toggle_display('purchase_billing', condition && frm.doc.purchase_billing);
    },
    validate(frm) {  
        if (frm.doc.references){              
        // วนลูปตรวจสอบแต่ละรายการใน frm.doc.references
        frm.doc.references.forEach(reference => {
            // ตรวจสอบว่า reference_doctype เป็น Purchase Invoice, Purchase Order, หรือ Journal Entry
            if (["Sales Billing","Sales Order", "Sales Invoice", "Dunning","Purchase Billing","Purchase Invoice", "Purchase Order", "Journal Entry"].includes(reference.reference_doctype)) {
                // เรียกใช้ฟังก์ชัน get_total_no_vat พร้อมกับ reference ที่ถูกเลือก
                get_total_no_vat(reference);
            }
        });
        }
    },
    payment_type(frm){
        frm.trigger('set_field_vis ibility');
        if (frm.doc.payment_type == "Pay") {
            frm.set_value('naming_series', 'PV.YY.MM.-.####');
        }
        else if (frm.doc.payment_type == "Receive"){
            frm.set_value('naming_series','RC.YY.MM.-.####');
        }else{
            frm.set_value('naming_series','')
        }
    }
});

frappe.ui.form.on("Payment Entry","setup", function(frm) {
    frm.set_query("paid_from", function () {
        frm.events.validate_company(frm);

        var account_types = ["Pay", "Internal Transfer"].includes(frm.doc.payment_type)
            ? ["Bank", "Cash"]
            : [frappe.boot.party_account_types[frm.doc.party_type]];

        if (frm.doc.party_type == "Shareholder") {
            account_types.push("Equity");
        }

        return {
            filters: {
                account_type: ["in", account_types],
                is_group: 0,
                company: frm.doc.company,
            },
        };
    });

    frm.set_query("party_type", function () {
        frm.events.validate_company(frm);
        return {
            filters: {
                name: ["in", Object.keys(frappe.boot.party_account_types)],
            },
        };
    });

    frm.set_query("party_bank_account", function () {
        return {
            filters: {
                is_company_account: 0,
                party_type: frm.doc.party_type,
                party: frm.doc.party,
            },
        };
    });

    frm.set_query("bank_account", function () {
        return {
            filters: {
                is_company_account: 1,
                company: frm.doc.company,
            },
        };
    });

    frm.set_query("contact_person", function () {
        if (frm.doc.party) {
            return {
                query: "frappe.contacts.doctype.contact.contact.contact_query",
                filters: {
                    link_doctype: frm.doc.party_type,
                    link_name: frm.doc.party,
                },
            };
        }
    });

    frm.set_query("paid_to", function () {
        frm.events.validate_company(frm);

        var account_types = ["Receive", "Internal Transfer"].includes(frm.doc.payment_type)
            ? ["Bank", "Cash"]
            : [frappe.boot.party_account_types[frm.doc.party_type]];
        if (frm.doc.party_type == "Shareholder") {
            account_types.push("Equity");
        }
        return {
            filters: {
                account_type: ["in", account_types],
                is_group: 0,
                company: frm.doc.company,
            },
        };
    });

    frm.set_query("account", "deductions", function () {
        return {
            filters: {
                is_group: 0,
                company: frm.doc.company,
            },
        };
    });

    frm.set_query("advance_tax_account", function () {
        return {
            filters: {
                company: frm.doc.company,
                root_type: ["in", ["Asset", "Liability"]],
                is_group: 0,
            },
        };
    });

    frm.set_query("reference_doctype", "references", function () {
        let doctypes = ["Journal Entry"];
        if (frm.doc.party_type == "Customer") {
            doctypes = ["Sales Billing","Sales Order", "Sales Invoice", "Journal Entry", "Dunning"];
        } else if (frm.doc.party_type == "Supplier") {
            doctypes = ["Purchase Billing","Purchase Order", "Purchase Invoice", "Journal Entry"];
        }

        return {
            filters: { name: ["in", doctypes] },
        };
    });

    frm.set_query("payment_term", "references", function (frm, cdt, cdn) {
        const child = locals[cdt][cdn];
        if (
            ["Purchase Invoice", "Sales Invoice"].includes(child.reference_doctype) &&
            child.reference_name
        ) {
            return {
                query: "erpnext.controllers.queries.get_payment_terms_for_references",
                filters: {
                    reference: child.reference_name,
                },
            };
        }
    });

    frm.set_query("reference_name", "references", function (doc, cdt, cdn) {
        const child = locals[cdt][cdn];
        const filters = { docstatus: 1, company: doc.company };
        const party_type_doctypes = [
            "Sales Invoice",
            "Sales Order",
            "Purchase Invoice",
            "Purchase Order",
            "Dunning",
        ];

        if (in_list(party_type_doctypes, child.reference_doctype)) {
            filters[doc.party_type.toLowerCase()] = doc.party;
        }

        return {
            filters: filters,
        };
    });

    frm.set_query("sales_taxes_and_charges_template", function () {
        return {
            filters: {
                company: frm.doc.company,
                disabled: false,
            },
        };
    });

    frm.set_query("purchase_taxes_and_charges_template", function () {
        return {
            filters: {
                company: frm.doc.company,
                disabled: false,
            },
        };
    });
})

frappe.ui.form.on("Payment Entry","validate_reference_document",function (frm, row) {
    var _validate = function (i, row) {
        if (!row.reference_doctype) {
            return;
        }

        if (
            frm.doc.party_type == "Customer" &&
            !["Sales Billing","Sales Order", "Sales Invoice", "Journal Entry", "Dunning"].includes(row.reference_doctype)
        ) {
            frappe.model.set_value(row.doctype, row.name, "reference_doctype", null);
            frappe.msgprint(
                __(
                    "Row #{0}: Reference Document Type must be one of Sales Billing, Sales Order, Sales Invoice, Journal Entry or Dunning",
                    [row.idx]
                )
            );
            return false;
        }

        if (
            frm.doc.party_type == "Supplier" &&
            !["Purchase Billing","Purchase Order", "Purchase Invoice", "Journal Entry"].includes(row.reference_doctype)
        ) {
            frappe.model.set_value(row.doctype, row.name, "against_voucher_type", null);
            frappe.msgprint(
                __(
                    "Row #{0}: Reference Document Type must be one of Purchase Billing, Purchase Order, Purchase Invoice or Journal Entry",
                    [row.idx]
                )
            );
            return false;
        }
    };

    if (row) {
        _validate(0, row);
    } else {
        $.each(frm.doc.vouchers || [], _validate);
    }
})
function retrieve_documents_based_on_payment_type(frm) {
    try {
        // Check if the form is new and required fields are set
        if (frm.is_new() && frm.doc.custom_bill_no ) {
                // Determine billing type based on payment_type
                const billing_type = frm.doc.payment_type === "Pay" ? "purchase" : "sales";

                // Dynamically call the appropriate function
                const event_name = `get_documents_from_${billing_type}_billing`;
                if (typeof frm.events[event_name] === "function") {
                    frm.events[event_name](frm, { [`${billing_type}_billing`]: frm.doc.custom_bill_no, allocate_payment_amount: 1 });
                } else {
                    console.warn(`Event method '${event_name}' not found.`);
                }
        }
    } catch (error) {
        frappe.msgprint(__("An error occurred while retrieving documents. Please try again."));
    }
}


function get_total_no_vat(frm) {
    // ดึงข้อมูล reference_doctype และ reference_name จาก reference ที่ถูกส่งมา
    let reference_doctype = frm.reference_doctype;
    let reference_name = frm.reference_name;
        
    // ทำการเรียก API ของ Frappe เพื่อดึงข้อมูลจาก doctype ที่อ้างอิง
    frappe.call({
        method: "frappe.client.get",
        args: {
            doctype: reference_doctype,
            name: reference_name
        },
        callback: function(r) {
            if(r.message) {
                let total = 0;

                // ตรวจสอบ Doctype เพื่อเลือกฟิลด์ total ที่เหมาะสม
                if (reference_doctype === "Journal Entry") {
                    // Journal Entry มีทั้ง total_debit และ total_credit
                    total = r.message.total_debit || r.message.total_credit || 0;
                } else if (reference_doctype === "Purchase Invoice" || reference_doctype === "Purchase Order" || reference_doctype === "Sales Invoice" || reference_doctype === "Sales Order") {
                    // ทั้ง Purchase Invoice, Purchase Order, Sales Invoice, Sales Order ใช้ฟิลด์ total
                    total = r.message.total || 0;
                } else if (reference_doctype === "Sales Billing" || reference_doctype === "Dunning" || reference_doctype === "Purchase Billing") {
                    // ทั้ง Sales Billing, Dunning, Purchase Billing ใช้ฟิลด์ total_outstanding_amount
                    total = r.message.total_outstanding_amount || 0;
                }

                total = parseFloat(total).toFixed(2);
                
                // อัพเดตค่าฟิลด์ custom_total_no_vat ของ reference นี้
                frappe.model.set_value(frm.doctype, frm.name, "custom_total_no_vat", total);
            }
        }
    });
}