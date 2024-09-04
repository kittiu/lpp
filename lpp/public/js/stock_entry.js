frappe.ui.form.on("Stock Entry", {

    stock_entry_type: function(frm) {
        
        switch(frm.doc.stock_entry_type) {
            case 'Manufacture':
                console.log("Manufacture",frm.doc.stock_entry_type);
                frm.set_value('naming_series', 'PT.YY..MM.-####.');
                break;
            case 'Material Transfer for Manufacture':
                frm.set_value('naming_series', 'MP.YY..MM.-####.');
                break;
            case 'Material Transfer':
                frm.set_value('naming_series', 'MT.YY..MM.-####.');
                break;
            case 'Material Issue':
                frm.set_value('naming_series', 'MI.YY..MM.-####.');
                break;
            case 'Material Receipt':
                frm.set_value('naming_series', 'MR.YY..MM.-####.');
                break;
            default:
                frm.set_value('naming_series', '');
        }
    }
});
