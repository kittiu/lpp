import frappe # type: ignore
import json

@frappe.whitelist()
def get_jobcard_remaining(data): 
    # Check if data is a string (which it seems to be based on the error)
    if isinstance(data, str):
        # Parse the string as JSON
        data = json.loads(data)
        
    count_amount = data['custom_total_run_cards']
    count_jobcard = frappe.db.count('Job Card', {'work_order': data['name']})
    count_operation = frappe.db.count('Work Order Operation', {'parent': data['name']})
    result = count_amount - (count_jobcard / count_operation)

    return result