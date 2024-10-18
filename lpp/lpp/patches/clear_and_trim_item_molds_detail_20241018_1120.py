import frappe

def execute():
    # Fetch all records from 'Item Molds Detail' doctype
    item_molds_details = frappe.get_all('Item Molds Detail', fields=['name'])

    # Loop through and delete each document
    for detail in item_molds_details:
        frappe.delete_doc('Item Molds Detail', detail.name, force=1)

    # Commit the changes to the database
    frappe.db.commit()

    # Optional: Trim the table to reset auto-increment and reclaim space
    frappe.db.sql("TRUNCATE TABLE `tabItem Molds Detail`")

    # Drop unnecessary columns from the 'Item Molds Detail' table
    # Replace 'unnecessary_column_name' with the actual column names you want to remove
    frappe.db.sql("ALTER TABLE `tabItem Molds Detail` DROP COLUMN `code_molds`")
    frappe.db.sql("ALTER TABLE `tabItem Molds Detail` DROP COLUMN `name_molds`")
    # Add more columns as needed
