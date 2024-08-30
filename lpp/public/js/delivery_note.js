frappe.ui.form.on("Delivery Note", {
    "onload": function(frm) {
        /*
            frappe.model.with_doc("Sales Order", frm.doc.onload, function() {
                var tabletransfer= frappe.model.get_doc("Sales Order", frm.doc.onload)
                console.log('tabletransfer', tabletransfer);
                
                $.each(tabletransfer.items, function(index, row){
                    var d = frm.add_child("items");
                    d.business_unit = row.business_unit;
                    frm.refresh_field("items");
                });
            });
        */
    }
});
