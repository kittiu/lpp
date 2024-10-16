frappe.ui.form.on("Batch", {
    refresh(frm) {
        frm.set_df_property("supplier", "read_only", 0);
        if(frm.doc.custom_lot_type === 'Buying'){
            frm.set_df_property("supplier", "hidden", 0);
        }else{
            frm.set_df_property("supplier", "hidden", 1);
        }
        add_generate_lot_no_button(frm);
        if (frm.doc.custom_lot_type == "Buying") {
            frm.set_df_property("custom_rescreen", "read_only", 1);
            frm.set_value("expiry_date", frappe.datetime.add_months(frm.doc.transaction_date, 12));
        }else if (frm.doc.custom_lot_type == "Selling") {
            frm.set_value("expiry_date", frappe.datetime.add_months(frm.doc.transaction_date, 24));
        }
    },
    custom_lot_type(frm) {
        if (frm.doc.custom_lot_type == "Buying") {
            frm.set_df_property("supplier", "hidden", 0);
            frm.set_value("custom_rescreen", 0);
            frm.set_df_property("custom_rescreen", "read_only", 1);
            frm.set_value("expiry_date", frappe.datetime.add_months(frm.doc.transaction_date, 12));
        } else if (frm.doc.custom_lot_type == "Selling") {
            frm.set_df_property("supplier", "hidden", 1);
            frm.set_value("expiry_date", frappe.datetime.add_months(frm.doc.transaction_date, 24));
            frm.set_value("custom_rescreen", 0);
            frm.set_df_property("custom_rescreen", "read_only", 0);
        }
        frm.set_value("batch_id", "");
    },
    custom_rescreen(frm) {
        frm.set_value("batch_id", "");  
    },
    item(frm) {
        frm.set_value("batch_id", "");
    }
});

function add_generate_lot_no_button(frm) {
    setTimeout(() => {
        if (!frm.doc.lot_no) {
            frm.add_custom_button('Generate Batch No.', function () {
                if (!frm.doc.item) {
                    frappe.msgprint("Please Select Item First");
                    return;
                }
                return frm.call({
                    method: "gen_lot_no",
                    doc: frm.doc,
                    callback: function (r) {
                        const next_lot_no = r.message;
                        frm.set_value("batch_id", next_lot_no);
                    },
                });
            });
        }
    }, 10);
}
