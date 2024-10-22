import frappe

def delete_field_from_batch(fieldname):
    logger = frappe.logger("batch_cleanup")

    try:
        # 1. ล้างข้อมูลในฟิลด์ก่อน
        if frappe.db.has_column("Batch", fieldname):
            logger.info(f"Clearing data in field '{fieldname}' from Batch...")
            frappe.db.sql(f"""UPDATE `tabBatch` SET `{fieldname}` = NULL;""")
            frappe.db.commit()
            logger.info(f"Data in field '{fieldname}' cleared.")

            # 2. ลบฟิลด์ออกจากฐานข้อมูล (ถ้ามี)
            logger.info(f"Dropping field '{fieldname}' from Batch...")
            frappe.db.sql(f"""ALTER TABLE `tabBatch` DROP COLUMN `{fieldname}`;""")
            frappe.db.commit()
            logger.info(f"Field '{fieldname}' successfully dropped.")

        else:
            logger.info(f"Field '{fieldname}' does not exist in Batch table.")

        # 3. ลบ Custom Field document (หากมี)
        custom_field_name = f"Batch-{fieldname}"
        if frappe.db.exists('Custom Field', custom_field_name):
            logger.info(f"Deleting Custom Field '{custom_field_name}'...")
            frappe.delete_doc('Custom Field', custom_field_name, force=1)
            frappe.db.commit()
            logger.info(f"Custom Field '{custom_field_name}' deleted successfully.")

        # 4. ล้างข้อมูลในตารางลูก (Child Tables)
        remove_field_data_from_children("Batch", fieldname)

    except Exception as e:
        logger.error(f"Error while deleting field '{fieldname}': {str(e)}")

def remove_field_data_from_children(parent_doctype, fieldname):
    logger = frappe.logger("batch_cleanup")

    try:
        # ค้นหาตารางลูกที่เกี่ยวข้องกับ Doctype นี้
        child_tables = frappe.get_all(
            "DocField",
            filters={"parent": parent_doctype, "fieldtype": "Table"},
            fields=["options"]
        )

        # ล้างข้อมูลในฟิลด์จากตารางลูก
        for child in child_tables:
            child_table = child["options"]
            if frappe.db.has_column(child_table, fieldname):
                logger.info(f"Clearing data in field '{fieldname}' from child table '{child_table}'...")
                frappe.db.sql(f"""UPDATE `tab{child_table}` SET `{fieldname}` = NULL;""")
                frappe.db.commit()
                logger.info(f"Data cleared from child table '{child_table}'.")

    except Exception as e:
        logger.error(f"Error while cleaning child table data for '{fieldname}': {str(e)}")

def execute():
    # รายชื่อฟิลด์ที่ต้องการลบ
    fields_to_delete = [
        "custom_supplier_this_batch"
    ]

    for field in fields_to_delete:
        delete_field_from_batch(field)
