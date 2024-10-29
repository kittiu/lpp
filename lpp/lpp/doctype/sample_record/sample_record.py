# Copyright (c) 2024, Ecosoft and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SampleRecord(Document):
	pass

@frappe.whitelist()
def get_customer_items(customer_name):
    # Fetch item codes based on customer_name in customer_items
    items = frappe.get_all('Item Customer Detail', 
        filters={'customer_name': customer_name},
        fields=['parent']  # parent is the Item linked to this child entry
    )
    
    # Return a list of item codes (parent field)
    return [item['parent'] for item in items]
