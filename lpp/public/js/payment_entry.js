frappe.ui.form.on("Payment Entry", {
    validate(frm) {
        // วนลูปตรวจสอบแต่ละรายการใน frm.doc.references
        frm.doc.references.forEach(reference => {
            // ตรวจสอบว่า reference_doctype เป็น Purchase Invoice, Purchase Order, หรือ Journal Entry
            if (["Purchase Invoice", "Purchase Order", "Journal Entry"].includes(reference.reference_doctype)) {
                // เรียกใช้ฟังก์ชัน get_total_no_vat พร้อมกับ reference ที่ถูกเลือก
                get_total_no_vat(reference);
            }
        });
    }
})

function get_total_no_vat(frm) {
    // ดึงข้อมูล reference_doctype และ reference_name จาก reference ที่ถูกส่งมา
    let reference_doctype = frm.reference_doctype;
    let reference_name = frm.reference_name;
        
    // ทำการเรียก API ของ Frappe เพื่อดึงข้อมูลจาก doctype ที่อ้างอิง
    frappe.call({
        method: "frappe.client.get",
        args: {
            doctype: reference_doctype,
            name: reference_name
        },
        callback: function(r) {
            if(r.message) {
                let total = 0;

                // ตรวจสอบ Doctype เพื่อเลือกฟิลด์ total ที่เหมาะสม
                if (reference_doctype === "Journal Entry") {
                    // Journal Entry มีทั้ง total_debit และ total_credit
                    total = r.message.total_debit || r.message.total_credit || 0;
                } else if (reference_doctype === "Purchase Invoice" || reference_doctype === "Purchase Order") {
                    // ทั้ง Purchase Invoice และ Purchase Order ใช้ฟิลด์ total
                    total = r.message.total || 0;
                }
                // อัพเดตค่าฟิลด์ custom_total_no_vat ของ reference นี้
                frappe.model.set_value(frm.doctype, frm.name, "custom_total_no_vat", total);
            }
        }
    });
}