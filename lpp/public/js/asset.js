const type_finance_books = [
    "finance_book",
    "depreciation_method",
    "rate_of_depreciation",
    "total_number_of_booked_depreciations",
    "frequency_of_depreciation",
    "depreciation_start_date",
    "value_after_depreciation",
    "salvage_value_percentage",
    "expected_value_after_useful_life"
]

// Reusable function to setup user-defined columns
function setupUserDefinedColumns(frm, tableField, typeArray) {
    frm.fields_dict[tableField].grid.setup_user_defined_columns = function () {
        if (typeArray && typeArray.length) {
            frm.fields_dict[tableField].grid.user_defined_columns = typeArray.map(fieldname => {
                let column = frappe.meta.get_docfield('Asset Finance Book', fieldname);
                if (column) {
                    column.in_list_view = 1;
                    column.columns = 1;
                    return column;
                }
            }).filter(Boolean);
        }
    };
    frm.fields_dict[tableField].grid.setup_user_defined_columns();
    frm.fields_dict[tableField].grid.refresh();
    frm.refresh_field(tableField);
}

frappe.ui.form.on("Asset", {
    setup: function(frm) {
        // Setup for finance_books
        setupUserDefinedColumns(frm, 'finance_books', type_finance_books);
    },

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
