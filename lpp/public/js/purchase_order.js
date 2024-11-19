const showButtonSendToMD = false
frappe.ui.form.on("Purchase Order", {
    refresh: function (frm) {
        // ตรวจสอบว่าผู้ใช้มีบทบาท "Managing Director" หรือไม่
        if (!frappe.user.has_role('Managing Director') && !frm.is_new() && showButtonSendToMD) {
            // เพิ่มปุ่มที่กำหนดเองชื่อว่า "Send to MD"
            frm.add_custom_button(__('Send to MD'), function () {
                // เรียกใช้เมธอดเซิร์ฟเวอร์
                frappe.call({
                    method: 'lpp.custom.purchase_order.trigger_notification', // ปรับปรุงเส้นทางเมธอดตามต้องการ
                    args: {
                        docname: frm.doc.name // ส่งชื่อเอกสารหรือพารามิเตอร์อื่น ๆ ที่จำเป็น
                    },
                    callback: function (r) {
                        if (!r.exc) {
                            // จัดการผลลัพธ์ (ถ้าต้องการ)
                            frappe.msgprint(__('Notification sent to MD successfully.'));
                        } else {
                            // หากมีข้อผิดพลาดในเซิร์ฟเวอร์
                            frappe.msgprint(__('Error sending notification to MD: ') + r.exc);
                        }
                    }
                });
            });
        }
    },

    supplier(frm) {
        // เคลียร์ตาราง items เมื่อเปลี่ยน Supplier
        // clearPurchaseOrderItems(frm);
    }
});

// Trigger events for the child table 'Purchase Order Item'
frappe.ui.form.on("Purchase Order Item", {
    items_add: function(frm, cdt, cdn) {
        // เมื่อเพิ่มรายการใหม่ในตาราง items ให้เซ็ต custom_supplier_item_code เป็น supplier
        setCustomSupplierItemCode(frm, cdt, cdn);
    }
});

// ฟังก์ชันสำหรับล้างตาราง 'items' และรีเฟรช
function clearPurchaseOrderItems(frm) {
    try {
        frm.clear_table("items"); // ลบแถวทั้งหมดในตาราง items
        frm.refresh_field("items"); // รีเฟรชตารางให้แสดงผลการเปลี่ยนแปลง
    } catch (error) {
        // จัดการข้อผิดพลาดกรณีล้างตารางไม่สำเร็จ
        frappe.msgprint(__('Error clearing Purchase Order Items: ') + error.message);
    }
}

// ฟังก์ชันสำหรับเซ็ตค่า custom_supplier_item_code เมื่อเพิ่มแถวใหม่ในตาราง 'Purchase Order Item'
function setCustomSupplierItemCode(frm, cdt, cdn) {
    try {
        // เซ็ตค่า custom_supplier_item_code ให้เป็น supplier จาก Purchase Order
        frappe.model.set_value(cdt, cdn, 'custom_supplier_item_code', frm.doc.supplier);
    } catch (error) {
        // จัดการข้อผิดพลาดกรณีเซ็ตค่าไม่สำเร็จ
        frappe.msgprint(__('Error setting custom_supplier_item_code in Purchase Order Item: ') + error.message);
    }
}

// การตั้งค่ารายการใน List View สำหรับ Purchase Order
frappe.listview_settings['Purchase Order'] = {
    onload: function(listview) {
        // ตรวจสอบว่ามีคอลัมน์และสามารถวนลูปได้
        if (listview && listview.columns && Array.isArray(listview.columns)) {
            listview.columns.forEach(field => {
                if (field.df && field.df.label === "Progress") {
                    // เปลี่ยน fieldname จาก 'Progress' เป็น 'status'
                    field.df.fieldname = 'status';
                }
            });

            listview.refresh(); // รีเฟรช listview เพื่อใช้การเปลี่ยนแปลง
        }
    }
};
