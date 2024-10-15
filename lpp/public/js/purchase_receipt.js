frappe.ui.form.on("Purchase Receipt", {
    refresh(frm) {
        frm.set_df_property('posting_time', 'hidden', true);
    }
})

frappe.ui.form.on("Purchase Receipt Item", "rate", function(frm, cdt, cdn) {
    var item = frappe.get_doc(cdt, cdn);
    var has_margin_field = frappe.meta.has_field(cdt, 'margin_type');

    frappe.model.round_floats_in(item, ["rate", "price_list_rate"]);
    let prev_price_list_rate = item.price_list_rate; // เก็บค่า price_list_rate ก่อนหน้า
    if(item.price_list_rate && !item.blanket_order_rate) {
        if(item.rate > item.price_list_rate && has_margin_field) {
            // if rate is greater than price_list_rate, set margin
            // or set discount
            item.discount_percentage = 0;
            item.margin_type = 'Amount';
            item.margin_rate_or_amount = flt(item.rate - item.price_list_rate,
                precision("margin_rate_or_amount", item));
            item.rate_with_margin = item.rate;
        } else {
            item.discount_percentage = flt((1 - item.rate / item.price_list_rate) * 100.0,
                precision("discount_percentage", item));
            item.discount_amount = flt(item.price_list_rate) - flt(item.rate);
            item.margin_type = '';
            item.margin_rate_or_amount = 0;
            item.rate_with_margin = 0;
        }
    } else {
        item.discount_percentage = 0.0;
        item.margin_type = '';
        item.margin_rate_or_amount = 0;
        item.rate_with_margin = 0;
    }
    item.base_rate_with_margin = item.rate_with_margin * flt(frm.doc.conversion_rate);    
    cur_frm.cscript.set_gross_profit(item);
    cur_frm.cscript.calculate_taxes_and_totals();
    cur_frm.cscript.calculate_stock_uom_rate(frm, cdt, cdn);
    item.price_list_rate = prev_price_list_rate; // นำค่าเก่ามาใช้
    
});
