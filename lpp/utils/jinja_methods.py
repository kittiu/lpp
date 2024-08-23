import frappe
def get_company_info():
    try:
        # Get the Company Info data
        return frappe.get_doc('Company Info')
    except frappe.DoesNotExistError:
        # Log error if needed and return None
        # frappe.log_error("Company Info DocType does not exist", "get_company_info")
        return None
    except Exception as e:
        # Handle any other unexpected exceptions
        # frappe.log_error(f"Error retrieving Company Info: {e}", "get_company_info")
        return None