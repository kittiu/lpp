frappe.ui.form.on("Quotation", {
    onload: function(frm) {
        // ตรวจสอบว่าเอกสารเป็นเอกสารใหม่หรือไม่
        if (frm.is_new()) {
            // ถ้า custom_proposer ว่างอยู่ ให้เซ็ตเป็นผู้ใช้ที่สร้างเอกสาร
            if (!frm.doc.custom_proposer) {
                frm.set_value('custom_proposer', frappe.session.user);
            }
        }
    },
    refresh: function (frm) {
        // ตรวจสอบว่าเอกสารเป็นเอกสารใหม่หรือไม่
        if (frm.is_new()) {
            // ถ้า valid_till ว่าง ให้เซ็ตเป็นวันที่ 12 เดือนถัดจาก transaction_date
            if (!frm.doc.valid_till) {
                frm.set_value("valid_till", frappe.datetime.add_months(frm.doc.transaction_date, 12));
            }
        }
    },
    party_name(frm) {
        // ใช้ flag เพื่อป้องกันการทำงานซ้ำ
        if (frm.doc.party_name === frm.party_name_old) return;
        frm.party_name_old = frm.doc.party_name;

        resetAndAddRowInQuotationItems(frm); // เรียกฟังก์ชันจัดการตาราง items

        // ตรวจสอบว่า party_name มีข้อมูล และ quotation_to เป็น "Customer"
        if (frm.doc.party_name && frm.doc.quotation_to === "Customer") {
            // เรียกข้อมูลจาก Customer ว่ามี custom_sales_tax_and_charge หรือไม่
            frappe.db.get_value('Customer', frm.doc.party_name, 'custom_sales_tax_and_charge', (r) => {
                
                if (r && r.custom_sales_tax_and_charge) {
                    // ถ้ามี เซ็ตค่าที่ taxes_and_charges
                    frm.set_value('taxes_and_charges', r.custom_sales_tax_and_charge);
                } else {
                    frm.set_value('taxes_and_charges', null);
                }
            }).fail((error) => {
                // จัดการข้อผิดพลาดจากการดึงข้อมูล
                frappe.msgprint(__('Error fetching customer data: ') + error.message);
            });
        }
    },
    before_save: function(frm) {
        // Reset flag before saving to allow `party_name` to trigger on next change
        frm.party_name_executed = false;
    }
});

frappe.ui.form.on('Quotation Item', {
    items_add: function(frm, cdt, cdn) {
        // เมื่อเพิ่มรายการใหม่ในตาราง items ให้เซ็ต customer_item_code เป็น party_name
        frappe.model.set_value(cdt, cdn, 'customer_item_code', frm.doc.party_name);
    }
});

frappe.listview_settings['Quotation'] = {
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
        } else {
            // หากมีข้อผิดพลาดในข้อมูล listview
            frappe.msgprint(__('Unable to modify columns due to missing or invalid structure.'));
        }
    }
};

// ฟังก์ชันสำหรับล้างและเพิ่มแถวในตาราง 'items'
const resetAndAddRowInQuotationItems = (frm) => {
    try {
        frm.clear_table("items"); // ลบแถวทั้งหมดในตาราง 'items'
        
        let new_row = frm.add_child("items"); // เพิ่มแถวใหม่
        new_row.customer_item_code = ""; // ตั้งค่าเริ่มต้นที่แถวใหม่

        frm.refresh_field("items"); // รีเฟรชตารางให้แสดงผลการเปลี่ยนแปลง
    } catch (error) {
        // จัดการข้อผิดพลาดในกรณีที่เกิดข้อผิดพลาดในการล้างหรือเพิ่มแถว
        frappe.msgprint(__('Error resetting and adding rows in Quotation Items: ') + error.message);
    }
};

// ฟังก์ชันวนลูปเซ็ตฟิลด์ customer_item_code สำหรับแต่ละแถวในตาราง 'items'
const loopSetFieldQuotationItem = (frm) => {
    try {
        frm.doc.items.forEach(row => {
            row.customer_item_code = frm.doc.party_name; // ตั้งค่า customer_item_code สำหรับแต่ละแถว
        });
        frm.refresh_field("items"); // รีเฟรชตาราง 'items'
    } catch (error) {
        // จัดการข้อผิดพลาดที่เกิดจากการวนลูปเซ็ตฟิลด์
        frappe.msgprint(__('Error setting customer_item_code in Quotation Items: ') + error.message);
    }
};
