frappe.ui.form.on("Purchase Invoice", {
    refresh(frm) {
        if(frm.doc.custom_supplier_invoice && frm.doc.custom_supplier_invoice !== frm.doc.tax_invoice_number){
            frm.set_value("tax_invoice_number", frm.doc.custom_supplier_invoice);
        }
        if(frm.doc.custom_supplier_delivery_date && frm.doc.custom_supplier_delivery_date !== frm.doc.tax_invoice_date){
            frm.set_value("tax_invoice_date", frm.doc.custom_supplier_delivery_date);
        }
        frm.set_df_property('custom_supplier_invoice', 'hidden', true);
        frm.set_df_property('custom_supplier_delivery_date', 'hidden', true);
        setTimeout(() => {
            // ลบปุ่ม "Get Items From" ถ้าเอกสารมีสถานะเอกสารเป็น 0 (ร่าง)
            frm.remove_custom_button('Purchase Order', 'Get Items From');
            if (frm.doc.docstatus === 0) {
                // เพิ่มปุ่มใหม่ "Get Items From"
                frm.add_custom_button('Purchase Order', function () {
                    erpnext.utils.map_current_doc({
                        method: "lpp.custom.purchase_order.custom_make_purchase_invoice",
                        source_doctype: "Purchase Order",
                        target: frm,
                        setters: {
                            supplier: frm.doc.supplier || undefined,
                            schedule_date: undefined,
                        },
                        get_query_filters: {
                            docstatus: 1, // ตรวจสอบให้แน่ใจว่าเอกสารมีสถานะ 1 (บันทึกแล้ว)
                            status: ["not in", ["Closed", "On Hold"]], // สถานะที่ไม่ใช่ "Closed" หรือ "On Hold"
                            per_billed: ["<", 99.99], // ตรวจสอบว่าการเรียกเก็บเงินยังไม่ถึง 100%
                            company: frm.doc.company, // กำหนดบริษัทที่ตรงกับเอกสาร
                        },
                    });
                }, 'Get Items From');
            }
        }, 10); // ใช้ setTimeout เพื่อให้แน่ใจว่าปุ่มจะถูกเพิ่มหลังจากการเรนเดอร์
    },
    supplier(frm) {
         // Loop through each row in the child table 'items'
         frm.doc.items.forEach(item => {
            setCustomSupplierItemCode(frm, item.doctype, item.name);
        });
        // เคลียร์ตาราง items เมื่อเปลี่ยน Supplier
        // clearPurchaseInvoiceItems(frm);
    },
    custom_supplier_invoice(frm){
        console.log('Hello');
        
        if(frm.doc.custom_supplier_invoice){
            frm.set_value("tax_invoice_number", frm.doc.custom_supplier_invoice);
        }
    },
    custom_supplier_delivery_date(frm){
        if(frm.doc.custom_supplier_delivery_date){
            frm.set_value("tax_invoice_date", frm.doc.custom_supplier_delivery_date);
        }
    }
});

// Trigger events for the child table 'Purchase Invoice Item'
frappe.ui.form.on("Purchase Invoice Item", {
    items_add: function(frm, cdt, cdn) {
        // เมื่อเพิ่มรายการใหม่ในตาราง items ให้เซ็ต custom_supplier_item_code เป็น supplier
        setCustomSupplierItemCode(frm, cdt, cdn);
    }
});

// ฟังก์ชันสำหรับล้างตาราง 'items' และรีเฟรช
function clearPurchaseInvoiceItems(frm) {
    try {
        frm.clear_table("items"); // ลบแถวทั้งหมดในตาราง items
        frm.refresh_field("items"); // รีเฟรชตารางให้แสดงผลการเปลี่ยนแปลง
    } catch (error) {
        // จัดการข้อผิดพลาดกรณีล้างตารางไม่สำเร็จ
        frappe.msgprint(__('Error clearing Purchase Invoice Items: ') + error.message);
    }
}

// ฟังก์ชันสำหรับเซ็ตค่า custom_supplier_item_code เมื่อเพิ่มแถวใหม่ในตาราง 'Purchase Invoice Item'
function setCustomSupplierItemCode(frm, cdt, cdn) {
    try {
        // เซ็ตค่า custom_supplier_item_code ให้เป็น supplier จาก Purchase Invoice
        frappe.model.set_value(cdt, cdn, 'custom_supplier_item_code', frm.doc.supplier);
    } catch (error) {
        // จัดการข้อผิดพลาดกรณีเซ็ตค่าไม่สำเร็จ
        frappe.msgprint(__('Error setting custom_supplier_item_code in Purchase Invoice Item: ') + error.message);
    }
}
