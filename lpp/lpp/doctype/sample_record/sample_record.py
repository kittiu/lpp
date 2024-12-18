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


@frappe.whitelist()
def get_filtered_work_orders(item_code, customer_name):
    # Query Work Order based on item_code and customer_name
    work_orders = frappe.get_all("Work Order", 
        filters={
            "production_item": item_code,
            "custom_customer": customer_name
        },
        fields=["name"]
    )
    
    # Return only the list of work order names
    return [wo["name"] for wo in work_orders]


@frappe.whitelist()
def get_job_cards_for_work_order(work_order):
    # Query Job Card records linked to the specified Work Order
    job_cards = frappe.get_all("Job Card", 
        filters={"work_order": work_order},
        fields="*",
        order_by="name asc"
    )

    scrap_items = {}

    # วนลูปผ่าน Job Cards เพื่อดึง Scrap Items
    for job_card in job_cards:
        job_card_items = frappe.get_all("Job Card Scrap Item", 
            filters={"parent": job_card.name}, 
            fields=["item_code", "item_name", "stock_qty"])

        for item in job_card_items:
            if item.stock_qty > 0:
                if item.item_code in scrap_items:
                    scrap_items[item.item_code]['stock_qty'] += item.stock_qty  # รวมค่า stock_qty
                else:
                    scrap_items[item.item_code] = {
                        "item_name": item.item_name,
                        "stock_qty": item.stock_qty
                    }

    # เปลี่ยน scrap_items เป็นรูปแบบที่ต้องการ
    result_scrap_items = [
        {
            "item_code": item_code,
            "item_name": details["item_name"],
            "stock_qty": details["stock_qty"]
        }
        for item_code, details in scrap_items.items()
    ]
    
    return { "job_cards": job_cards, "scrap_items": result_scrap_items }