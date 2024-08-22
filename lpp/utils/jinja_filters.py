import frappe
from datetime import datetime

def format_datetime_to_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
        return date_obj.strftime('%d/%m/%Y')
    except Exception as e:
        return date_str
def format_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%d/%m/%Y')
    except Exception as e:
        return date_str
def substring_if_longer(value, length):
    if value is None:
        return ""  # Handle the case where input is None
    
    if not isinstance(value, str):
        return ""  # Handle cases where value is not a string
    
    if len(value) > length:
        return value[:length] + '...'  # Adjust the length as needed
    
    return value
def format_currency(value, decimals=2):
    try:
        # Format the value with the specified number of decimal places
        return f"{float(value):,.{decimals}f}"
    except (ValueError, TypeError):
        # Handle cases where value is not a valid number
        return "Invalid value"
def sum_amounts(items):
    return sum(item.get('amount', 0) for item in items)
def get_user_full_name(owner):
    try:
        user = frappe.get_doc('User', owner)
        first_name = user.first_name or ''
        last_name = user.last_name or ''
        # Strip any extra whitespace and ensure a clean format
        return f"{first_name.strip()} {last_name.strip()}" if (first_name or last_name) else "Unknown User"
    except frappe.DoesNotExistError:
        return "Unknown User"