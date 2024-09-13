frappe.ui.form.on("Purchase Invoice", {
    refresh(frm) {

        setTimeout(() => {
            // Remove Original Button
            frm.remove_custom_button('Purchase Order', 'Get Items From');
            if (frm.doc.docstatus === 0) {
                frm.add_custom_button('Purchase Order',function () {
                    erpnext.utils.map_current_doc({
                        method: "lpp.custom.purchase_order.custom_make_purchase_invoice",
                        source_doctype: "Purchase Order",
                        target: frm,
                        setters: {
                            supplier: frm.doc.supplier || undefined,
                            schedule_date: undefined,
                        },
                        get_query_filters: {
                            docstatus: 1,
                            status: ["not in", ["Closed", "On Hold"]],
                            per_billed: ["<", 99.99],
                            company: frm.doc.company,
                        },
                    });
                }, 'Get Items From');
            }
        }, 10);

    },

})

