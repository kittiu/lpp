frappe.ui.form.on("Delivery Note", {
    refresh: function (frm) {
        const doc = frm.doc;
        // check items is not empty
        if (doc.items.length == 0) {
            // set payment schedule to delivery note
            frm.set_value("custom_payment_schedule", "");
            return;
        }
        // get sales order from items
        const sales_order = doc.items[0].against_sales_order;
        // get sales order data
        const sales_order_doc = frappe.get_doc("Sales Order", sales_order);
        // coppy payment schedule of sales order to delivery note
        const payment_schedule = sales_order_doc.payment_schedule;
        // set payment schedule to delivery note
        frm.set_value("custom_payment_schedule", payment_schedule);

        
    }
});
