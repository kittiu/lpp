frappe.ui.form.on("Sales Order", {
    refresh: function(frm) {
        // แสดงฟิลด์ po_no และ po_date
        frm.set_df_property('po_no', 'hidden', 0);
        frm.set_df_property('po_date', 'hidden', 0);
    },
    onload: function(frm) {
        // ซ่อนฟิลด์ item_name ในตาราง items
        frm.fields_dict.items.grid.toggle_display("item_name", false);
    },
    // อัปเดตฟิลด์เมื่อมีการเปลี่ยนแปลงใน po_no, po_date, delivery_date
    po_no: update_items,
    po_date: update_items,
    delivery_date: update_items,
    customer: function(frm) {
        // เคลียร์ตาราง items เมื่อเปลี่ยน Customer
        clearSalesOrderItems(frm);
        
        // เคลียร์ตาราง Sales Taxes and Charges
        clearSalesTaxes(frm);
    }
});

// ฟังก์ชันอัปเดต 'custom_po_no', 'custom_po_date' และ 'delivery_date' ในตาราง items
function update_items(frm) {
    const { po_no, po_date, delivery_date } = frm.doc;

    if (po_no || po_date || delivery_date) {
        frm.doc.items.forEach(row => {
            // อัปเดตค่าฟิลด์ในแต่ละแถวของตาราง items
            frappe.model.set_value(row.doctype, row.name, {
                custom_po_no: po_no,
                custom_po_date: po_date,
                delivery_date: delivery_date
            });
        });
        frm.refresh_field("items"); // รีเฟรชตารางให้แสดงการเปลี่ยนแปลง
    }
}

// Trigger events for the child table 'Sales Order Item'
frappe.ui.form.on("Sales Order Item", {
    items_add: function(frm, cdt, cdn) {
        set_value_item(frm, cdt, cdn);
        // เมื่อเพิ่มรายการใหม่ในตาราง items ให้เซ็ต customer_item_code เป็น customer
        frappe.model.set_value(cdt, cdn, 'customer_item_code', frm.doc.customer);
    }
});

// ฟังก์ชันเซ็ตค่า po_no, po_date และ delivery_date เมื่อเพิ่มแถวใหม่ในตาราง items
function set_value_item(frm, cdt, cdn) {
    const { po_no, po_date, delivery_date } = frm.doc;

    if (po_no || po_date || delivery_date) {
        frappe.model.set_value(cdt, cdn, {
            custom_po_no: po_no,
            custom_po_date: po_date,
            delivery_date: delivery_date
        });
    }
}

// ฟังก์ชันสำหรับเคลียร์ตาราง Sales Taxes and Charges
function clearSalesTaxes(frm) {
    try {
        frm.clear_table('taxes'); // เคลียร์แถวทั้งหมดในตาราง taxes
        frm.refresh_field('taxes'); // รีเฟรชฟิลด์เพื่อแสดงผลการเปลี่ยนแปลง
    } catch (error) {
        // จัดการข้อผิดพลาดกรณีเคลียร์ตารางไม่สำเร็จ
        frappe.msgprint(__('Error clearing Sales Taxes and Charges: ') + error.message);
    }
}

// ฟังก์ชันสำหรับล้างตาราง 'items' และรีเฟรช
function clearSalesOrderItems(frm) {
    try {
        frm.clear_table("items"); // ลบแถวทั้งหมดในตาราง items
        frm.refresh_field("items"); // รีเฟรชตารางให้แสดงผลการเปลี่ยนแปลง
    } catch (error) {
        // จัดการข้อผิดพลาดกรณีล้างตารางไม่สำเร็จ
        frappe.msgprint(__('Error resetting and adding rows in Sales Items: ') + error.message);
    }
}
