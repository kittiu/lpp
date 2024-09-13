frappe.ui.form.on("Quality Inspection", {
    refresh(frm) {
        // Get today's date
        let today = frappe.datetime.nowdate();

        // Set 'custom_date_inspected_by' field to today's date by default
        frm.set_value("custom_date_inspected_by", today);

        // Set 'custom_date_approved_by' field to today's date by default
        frm.set_value("custom_date_approved_by", today);
    }

})