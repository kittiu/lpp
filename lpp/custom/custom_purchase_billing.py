import frappe
from purchase_billing.purchase_billing.doctype.purchase_billing.purchase_billing import PurchaseBilling
from frappe.utils import get_first_day, get_last_day

class CustomPurchaseBilling(PurchaseBilling):      
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
    
    @frappe.whitelist()
    def get_purchase_invoices_in_month(self, supplier, currency, threshold_type, threshold_date, tax_type = None):
        if not (supplier, currency, tax_type, threshold_date):
            return {}

        filters = {
            "supplier": supplier,
            "currency": currency,
            "docstatus": 1,
            "outstanding_amount": [">", 0],
        }

        if tax_type:
            filters["taxes_and_charges"] = tax_type

        # Calculate the first and last day of the month for the given threshold_date
        first_day_of_month = get_first_day(threshold_date)
        last_day_of_month = get_last_day(threshold_date)

        # Apply the posting or due date condition based on threshold_type
        if threshold_type == "Due Date":
            filters["posting_date"] = ["between", [first_day_of_month, last_day_of_month]]
        if threshold_type == "Invoice Date":
            filters["due_date"] = ["between", [first_day_of_month, last_day_of_month]]

        invoices = frappe.get_list(
            "Purchase Invoice",
            filters=filters,
            pluck="name",
        )

        return invoices
