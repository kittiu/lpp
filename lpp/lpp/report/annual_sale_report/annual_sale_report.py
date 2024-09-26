from .quarter import quarter  # Optimized import for the current directory

def execute(filters=None):
    # Fetch columns and data from the quarter function
    try:
        columns, data = quarter(filters)
        return columns, data
    except Exception as e:
        # Handle potential errors and provide meaningful feedback
        frappe.log_error(message=str(e), title="Quarter Report Generation Error")
        return [], []