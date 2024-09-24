frappe.ui.form.on("Asset", {

    asset_category: function (frm) {
        switch (frm.doc.asset_category) {
            case 'Land':
                frm.set_value('naming_series', 'FLAN.YY.MM.####.');
                break;
            case 'Building':
                frm.set_value('naming_series', 'FBUD.YY.MM.####.');
                break;
            case 'Vehicle':
                frm.set_value('naming_series', 'FVEH.YY.MM.####.');
                break;
            case 'Machine & Mold':
                frm.set_value('naming_series', 'FMAC.YY.MM.####.');
                break;
            case 'Tools & Equipment':
                frm.set_value('naming_series', 'FEQU.YY.MM.####.');
                break;
            case 'Interior & Furniture':
                frm.set_value('naming_series', 'FFUR.YY.MM.####.');
                break;
            case 'Electrical Appliances':
                frm.set_value('naming_series', 'FELC.YY.MM.####.');
                break;
            case 'Computer Equipment':
                frm.set_value('naming_series', 'FCOM.YY.MM.####.');
                break;
            case 'Build Insurance':
                frm.set_value('naming_series', 'FBIN.YY.MM.####.');
                break;
            case 'Vehicle Insurance':
                frm.set_value('naming_series', 'FVIN.YY.MM.####.');
                break;
            default:
                frm.set_value('naming_series', '');
        }
    }
});
