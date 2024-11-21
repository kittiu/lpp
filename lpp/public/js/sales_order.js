frappe.ui.form.on("Sales Order", {
    refresh: function(frm) {
        // แสดงฟิลด์ po_no และ po_date
        frm.set_df_property('po_no', 'hidden', 0);
        frm.set_df_property('po_date', 'hidden', 0);
        set_item_code_query(frm);
        frm.refresh_field("items"); 
    },
    onload: function(frm) {
        // ซ่อนฟิลด์ item_name ในตาราง items
        frm.fields_dict.items.grid.toggle_display("item_name", false);
        
            if (frm.doc.docstatus === 0 && frappe.model.can_read("Quotation")) {

                    frm.remove_custom_button(__('Quotation'))
                    frm.add_custom_button(
                        __("Quotation"),
                        function () {
                            let d = erpnext.utils.map_current_doc({
                                method: "lpp.custom.quotation.make_sales_order",
                                source_doctype: "Quotation",
                                target: frm,
                                setters: [
                                    {
                                        label: "Customer",
                                        fieldname: "party_name",
                                        fieldtype: "Link",
                                        options: "Customer",
                                        default: frm.doc.customer || undefined,
                                    },
                                ],
                                get_query_filters: {
                                    company: frm.doc.company,
                                    docstatus: 1,
                                    status: ["!=", "Lost"],
                                },
                            });
                            
                        },
                        __("Get Items From")
                    );


            }


    },
    // อัปเดตฟิลด์เมื่อมีการเปลี่ยนแปลงใน po_no, po_date, delivery_date
    po_no: update_items,
    po_date: update_items,
    delivery_date: update_items,
    customer: function(frm) {
        // เคลียร์ตาราง items เมื่อเปลี่ยน Customer
        // clearSalesOrderItems(frm);
        // Loop through each row in the child table 'items'
        frm.doc.items.forEach(item => {
            frappe.model.set_value(item.doctype, item.name, 'customer_item_code', frm.doc.customer);
        });
        // เคลียร์ตาราง Sales Taxes and Charges
        clearSalesTaxes(frm);
    },
    customer_name : function (frm){
        set_item_code_query(frm);
        frm.refresh_field("items"); 
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