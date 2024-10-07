frappe.ui.form.on("Item", {

    item_group(frm) {
        if(frm.doc.item_group){
            if(frm.doc.item_group == "Sales Products"){
                frm.set_value("has_batch_no", 1);
            }
            else if(frm.doc.item_group == "Raw Material" || frm.doc.item_group == "Raw Materials"){
                frm.set_value("has_batch_no", 1);
            }else{
                frm.set_value("has_batch_no", 0);
            }
        }
    },
});
