import frappe
from sales_billing.sales_billing.doctype.sales_billing.sales_billing import SalesBilling
from frappe.utils import now

class CustomSalesBilling(SalesBilling):      
    @frappe.whitelist()
    def make_journal_entry(self):
        # สร้าง Journal Entry 
        sales_billing = self
        journal_entry = frappe.new_doc("Journal Entry")
        journal_entry.bill_no = sales_billing.name
        journal_entry.bill_date = sales_billing.date
        
        if sales_billing.threshold_type == "Due Date":
            journal_entry.due_date = sales_billing.threshold_date

        return journal_entry
    
    @frappe.whitelist()
    def make_payment_entry(self):
        # สร้าง Payment Entry
        purchase_billing = self
        payment_entry = frappe.new_doc("Payment Entry")
        payment_entry.payment_type = "Receive"
        payment_entry.posting_date = now()
        payment_entry.party_type = "Customer"
        payment_entry.party = purchase_billing.customer
        payment_entry.party_name = purchase_billing.customer_name
        payment_entry.paid_amount = purchase_billing.total_outstanding_amount
        payment_entry.received_amount = purchase_billing.total_outstanding_amount
        payment_entry.custom_bill_no = purchase_billing.name
        payment_entry.custom_bill_date = purchase_billing.date

        # สร้าง Payment Entry Reference
        payment_entry_reference = frappe.new_doc("Payment Entry Reference")
        payment_entry_reference.reference_doctype = "Sales Billing"
        payment_entry_reference.reference_name = purchase_billing.name
        payment_entry_reference.total_amount = purchase_billing.total_billing_amount
        payment_entry_reference.outstanding_amount = purchase_billing.total_outstanding_amount
        payment_entry.append("references", payment_entry_reference)

        return payment_entry