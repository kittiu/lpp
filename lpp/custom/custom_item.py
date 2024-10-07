from frappe.model.document import Document
from frappe.model.naming import make_autoname
import frappe

class CustomItem(Document):
    def autoname(self):
        if self.custom_abbreviation:
            # Use dot (.) to separate the prefix from the numeric part
            self.name = make_autoname(f"{self.custom_abbreviation}-.#####")
        else:
            frappe.throw("Custom Abbreviation is required for auto-naming.")
