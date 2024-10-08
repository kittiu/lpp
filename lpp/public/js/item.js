frappe.ui.form.on("Item", {

    item_group(frm) {
        if(frm.doc.item_group){
            if(frm.doc.item_group == "Sales Products"){
                frm.set_value("has_batch_no", 1);
            }
            else if(frm.doc.item_group == "Raw Material" || frm.doc.item_group == "Raw Materials"){
                frm.set_value("has_batch_no", 1);
                // วนลูปผ่านทุกแถวใน item_defaults
                (frm.doc.item_defaults || []).forEach(function(row) {
                    // แทนค่าทุกฟิลด์ default_warehouse ใน item_defaults
                    frappe.model.set_value(row.doctype, row.name, "default_warehouse", "Raw Materials - LPP");
                });
            }else{
                frm.set_value("has_batch_no", 0);
            }
        }
    },
});
