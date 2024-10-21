import frappe
import math

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
    
def chunk_list(lst : list, size):
    return [lst[i:i+size] for i in range(0, len(lst), size)]

def split_string(input_str, delimiter='-', index=None):
    # Split the input string by the specified delimiter and strip any leading/trailing whitespace from the parts
    parts = [part.strip() for part in input_str.split(delimiter)]
    
    # If index is provided, return the specific part, otherwise return the full list
    if index is not None and 0 <= index < len(parts):
        return parts[index]
    return parts
def calculate_qty(qty, custom_unit, per_page = 8):
    """
    Calculate qty based on custom_unit.
    If custom_unit is None or 0, return 0.
    If the result has a decimal part, round up to the nearest whole number.
    """
    try:
        custom_unit = float(custom_unit or 0)  # Handle None or 0 in a single line
        qty = float(qty or 0)  # Handle None or empty qty in a single line
        
        if custom_unit == 0:
            return 0
        
        result = (qty / custom_unit) / per_page
        
        # Round up if there is a decimal part
        return math.ceil(result)
        
    except (ValueError, TypeError):
        return 0

