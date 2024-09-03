frappe.ui.form.on('BOM', {

});


frappe.ui.form.on('BOM Item', {
	item_code : async function(frm, cdt, cdn) {
		var scrap_items = false;
		var child = locals[cdt][cdn];
		if (child.doctype == "BOM Scrap Item") {
			scrap_items = true;
		}

		if (child.bom_no) {
			child.bom_no = "";
		}

		await get_bom_material_detail(frm.doc, cdt, cdn, scrap_items);
        update_invoice_portion(frm);
        
	},
    qty: function(frm, cdt, cdn) {
        update_invoice_portion(frm);  
    },
    custom_invoice_portion_ : function(frm, cdt, cdn) {
        update_invoice_portion(frm);
    },
    items_remove(frm, cdt, cdn) {
        update_invoice_portion(frm);
    },
})

function update_invoice_portion (frm) {
    
    let total_qty = 0;

    // คำนวณ total cost ของวัตถุดิบทั้งหมด
    frm.doc.items.forEach(i => {        
        total_qty += i.qty;
    });

    // คำนวณและอัพเดต Invoice Portion % สำหรับแต่ละวัตถุดิบ
    frm.doc.items.forEach(item => {
        if (total_qty > 0) {
            
            invoice_portion = (item.qty/ total_qty) * 100;
            item.custom_invoice_portion_ = invoice_portion;
        } else {

            item.custom_invoice_portion_ = 0;
        }
    });

    // รีเฟรชฟิลด์ของรายการวัตถุดิบเพื่อแสดงผลลัพธ์
    frm.refresh_field('items');
}

