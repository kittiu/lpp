import frappe

@frappe.whitelist()
def get_journal_entry_naming_series():
    naming_series = frappe.get_meta("Journal Entry").get_field("naming_series").options
    return naming_series.split("\n")
