frappe.listview_settings['Stock Entry'] = {
    onload: function(listview) {
        // เพิ่มปุ่มที่กำหนดเองด้านบนขวา
        listview.page.add_action_item(__('Already Printed'), async function() {
            let selected_docs = listview.get_checked_items();  // ดึงรายการที่เลือกทั้งหมด

            // กรองเฉพาะ Stock Entries ที่มีสถานะเป็น "Draft"
            selected_docs = selected_docs.filter(doc => doc.docstatus === 0 && doc.purpose === 'Manufacture');
            if (selected_docs.length === 0) {
                return frappe.msgprint(__('Please select at least one Draft Stock Entry.'));
            }

            // ยืนยันการอัพเดตรายการที่เลือก
            frappe.confirm(__('Mark the selected draft entries as Already Printed?'), async function() {
                let total_docs = selected_docs.length;
                let completed_docs = 0;
                let update_success = [];  // Array to store successfully updated Stock Entries

                // แสดง popup progress bar
                frappe.show_progress(__('Updating Stock Entries'), completed_docs, total_docs, __('Please wait...'));

                // ใช้ async/await เพื่อลดซับซ้อนของ promises
                for (const doc of selected_docs) {
                    try {
                        // อัพเดต custom field สำหรับแต่ละ Stock Entry
                        await frappe.call({
                            method: 'frappe.client.set_value',
                            args: {
                                doctype: 'Stock Entry',
                                name: doc.name,
                                fieldname: 'custom_already_printed',  // ชื่อฟิลด์ที่ต้องการอัพเดต
                                value: 1  // เซ็ตค่า (1 สำหรับ Already Printed)
                            }
                        });

                        // แสดงแจ้งเตือนเมื่ออัพเดตสำเร็จ
                        frappe.show_alert({
                            message: __('Stock Entry {0} marked as Already Printed', [doc.name]),
                            indicator: 'green'
                        });

                        // Add successfully updated document to the array
                        update_success.push(doc.name);

                    } catch (error) {
                        frappe.msgprint({
                            title: __('Error'),
                            indicator: 'red',
                            message: __('An error occurred while updating Stock Entry {0}.', [doc.name])
                        });
                    }

                    // อัพเดต progress popup ทุกครั้งที่รายการสำเร็จ
                    completed_docs++;
                    frappe.show_progress(__('Updating Stock Entries'), completed_docs, total_docs, __(`Updated ${completed_docs} out of ${total_docs} draft entries`));
                }

                // เมื่ออัพเดตทั้งหมดเสร็จสิ้น
                setTimeout(function() {
                    frappe.hide_progress();
                    // After the process is complete, redirect to a report or custom page with the update_success array
                    if (update_success.length > 0) {
                        frappe.msgprint({
                            title: __('Success'),
                            indicator: 'green',
                            message: __('Successfully updated Stock Entries: {0}', [update_success.join(', ')])
                        });

                        // Redirect to the "Material Transfer from Manufacture" report
                        frappe.set_route('query-report', 'Material Transfer from Manufacture', {
                            stock_entry_id: update_success
                        });
                    }
                }, 2000); // 2000 milliseconds = 2 seconds

            });
        });
    }
};
