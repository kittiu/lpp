frappe.ui.form.on("Stock Entry", {

    refresh(frm) {
        if (frm.doc.work_order){
            frm.events.set_custom_lot_no(frm);
        }
    },
    stock_entry_type: function(frm) {
        
        switch(frm.doc.stock_entry_type) {
            case 'Manufacture':
                frm.set_value('naming_series', 'PT.YY..MM.-.####.');
                break;
            case 'Material Transfer for Manufacture':
                frm.set_value('naming_series', 'MP.YY..MM.-.####.');
                break;
            case 'Material Transfer':
                frm.set_value('naming_series', 'MT.YY..MM.-.####.');
                break;
            case 'Material Issue':
                frm.set_value('naming_series', 'MI.YY..MM.-.####.');
                break;
            case 'Material Receipt':
                frm.set_value('naming_series', 'MR.YY..MM.-.####.');
                break;
            default:
                frm.set_value('naming_series', '');
        }
    },
    set_custom_lot_no: function(frm) {
        return frappe.db.get_value("Work Order", frm.doc.work_order, "custom_lot_no")
            .then(({ message }) => {
                if (message) {
                    frm.set_value('custom_lot_no', message.custom_lot_no);
                }
            })
            .catch(err => {
                frm.set_value('custom_lot_no', null);
            });
    }
});

