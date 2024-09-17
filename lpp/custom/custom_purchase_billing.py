import frappe
from purchase_billing.purchase_billing.doctype.purchase_billing.purchase_billing import PurchaseBilling

class CustomSalesBilling(PurchaseBilling):      
    @frappe.whitelist()
    def make_journal_entry(self):
        # สร้าง Journal Entry 
        purchase_billing = self
        journal_entry = frappe.new_doc("Journal Entry")
        journal_entry.bill_no = purchase_billing.name
        journal_entry.bill_date = purchase_billing.date
        journal_entry.custom_party_type = "Supplier"
        journal_entry.custom_party = purchase_billing.supplier
        
        if purchase_billing.threshold_type == "Due Date":
            journal_entry.due_date = purchase_billing.threshold_date

        return journal_entry