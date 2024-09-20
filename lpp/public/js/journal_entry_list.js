frappe.listview_settings['Journal Entry'] = {
    onload: function(listview) {
        frappe.call({
            method: 'lpp.custom.journal_entry.get_journal_types_for_user',
            callback: function(r) {
                if (r.message) {
                    // สร้างอาเรย์ของ 'name' จากผลลัพธ์ที่ได้
                    let journal_type_names = r.message.map(jt => jt.name);
                    
                    // เพิ่มตัวกรองเพื่อแสดงเฉพาะ 'Journal Entry' ที่ 'journal_type' อยู่ใน 'journal_type_names'
                    listview.filter_area.add('Journal Entry', 'custom_journal_type', 'in', journal_type_names);
                    listview.refresh();  // รีเฟรชหน้ารายการด้วยตัวกรองใหม่
                }
            }
        });
    }
};
