import frappe

def execute():
    try:
        # Check if the custom field with the specific name exists
        if frappe.db.exists('Custom Field', 'Work Order-custom_item_molds'):
            # Delete the custom field
            frappe.delete_doc('Custom Field', 'Work Order-custom_item_molds', force=1)
            frappe.db.commit()  # Commit the changes
            print("Custom Field 'Work Order-custom_item_molds' deleted successfully.")
        else:
            print("Custom Field 'Work Order-custom_item_molds' does not exist.")
        frappe.db.sql("ALTER TABLE `tabWork Order` DROP COLUMN IF EXISTS `custom_item_molds`")
        frappe.db.commit()  # Commit the changes
    except frappe.DoesNotExistError:
        # Handle the case where the custom field does not exist
        print("The custom field 'Work Order-custom_item_molds' does not exist or cannot be found.")
    except frappe.ValidationError as e:
        # Handle any validation errors during deletion
        print(f"Validation error during deletion: {e}")
    except Exception as e:
        # Handle any other unexpected errors
        print(f"An unexpected error occurred: {e}")
