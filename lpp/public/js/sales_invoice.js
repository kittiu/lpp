frappe.ui.form.on("Sales Invoice", {
    onload: function(frm) {
        // Set the 'title' field as not mandatory
        frm.toggle_reqd('title', false); // Make 'title' not mandatory
        if(frm.doc.select_print_heading && frm.doc.select_print_heading === 'Credit Note'){
            frm.set_value('naming_series', 'CN.YY.MM.-.####');
        }
    },
    refresh_field: function(frm){
        set_item_code_query(frm);
        frm.refresh_field("items"); // รีเฟรช child table เมื่อ customer_name เปลี่ยน
    },
    customer: function(frm) {
        // เคลียร์ตาราง items เมื่อเปลี่ยน Customer
        // clearSalesInvoiceItems(frm);

        // Loop through each row in the child table 'items'
        frm.doc.items.forEach(item => {
            setCustomerItemCode(frm, item.doctype, item.name);
        });

        set_item_code_query(frm);
        frm.refresh_field("items"); // รีเฟรช child table เมื่อ customer_name เปลี่ยน

    }
});

// Trigger events for the child table 'Sales Invoice Item'
frappe.ui.form.on("Sales Invoice Item", {
    items_add: function(frm, cdt, cdn) {
        // เมื่อเพิ่มรายการใหม่ในตาราง items ให้เซ็ต customer_item_code เป็น customer
        setCustomerItemCode(frm, cdt, cdn);
    }
});

// ฟังก์ชันสำหรับล้างตาราง 'items' และรีเฟรช
function clearSalesInvoiceItems(frm) {
    try {
        frm.clear_table("items"); // ลบแถวทั้งหมดในตาราง items
        frm.refresh_field("items"); // รีเฟรชตารางให้แสดงผลการเปลี่ยนแปลง
    } catch (error) {
        // จัดการข้อผิดพลาดกรณีล้างตารางไม่สำเร็จ
        frappe.msgprint(__('Error clearing Sales Invoice Items: ') + error.message);
    }
}

// ฟังก์ชันสำหรับเซ็ตค่า customer_item_code เมื่อเพิ่มแถวใหม่ในตาราง 'Sales Invoice Item'
function setCustomerItemCode(frm, cdt, cdn) {
    try {
        // เซ็ตค่า customer_item_code ให้เป็น customer จาก Sales Invoice
        frappe.model.set_value(cdt, cdn, 'customer_item_code', frm.doc.customer);
    } catch (error) {
        // จัดการข้อผิดพลาดกรณีเซ็ตค่าไม่สำเร็จ
        frappe.msgprint(__('Error setting customer_item_code in Sales Invoice Item: ') + error.message);
    }
}

function set_item_code_query(frm) {    
    frm.set_query("item_code", "items", function (doc, cdt, cdn) {
        const party_name = frm.doc.customer_name;
        return {
            query: "lpp.custom.custom_item.get_items_based_on_party_and_groups",
            filters: {
                party_name : party_name
            }
        };
    })
}