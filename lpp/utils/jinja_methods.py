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

def group_and_sum_by_po(docname):
    try:
        # Get the Sales Invoice document
        doc = frappe.get_doc("Sales Invoice", docname)
        
        # Safely get the taxes and default rate to 0 if not available
        taxes = doc.get("taxes", [])
        tax_rate = taxes[0].rate if taxes and hasattr(taxes[0], 'rate') else 0

        grouped_amounts = {}

        # Iterate through the child table (items)
        for item in doc.items:
            # Check if the custom_po_no exists in the grouped_amounts dictionary
            if item.custom_po_no not in grouped_amounts:
                grouped_amounts[item.custom_po_no] = 0  # Initialize if not present

            # Add the amount to the corresponding custom_po_no
            grouped_amounts[item.custom_po_no] += item.amount

        # Convert the result into an array of objects for Jinja
        result = []
        for po_no, amount in grouped_amounts.items():
            grand_total = (amount * tax_rate) / 100 + amount
            result.append({
                "po_no": po_no,
                "total_amount": amount,
                "grand_total": grand_total
            })

        return result
    
    except Exception as e:
        frappe.log_error(message=f"Error in group_and_sum_by_po: {str(e)}", title="Jinja Method Error")
        return []