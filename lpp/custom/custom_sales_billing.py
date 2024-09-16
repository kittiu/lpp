import frappe
from sales_billing.sales_billing.doctype.sales_billing.sales_billing import SalesBilling

class CustomSalesBilling(SalesBilling):      
    @frappe.whitelist()
    def make_journal_entry(self):
        # สร้าง Journal Entry 
        sales_billing = self
        journal_entry = frappe.new_doc("Journal Entry")
        journal_entry.bill_no = sales_billing.name
        journal_entry.bill_date = sales_billing.date
        journal_entry.custom_party_type = "Customer"
        journal_entry.custom_party = sales_billing.customer
        
        if sales_billing.threshold_type == "Due Date":
            journal_entry.due_date = sales_billing.threshold_date

        return journal_entry