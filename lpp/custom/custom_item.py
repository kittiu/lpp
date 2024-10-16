from erpnext.stock.doctype.item.item import Item
from frappe.model.naming import make_autoname
import frappe

class CustomItem(Item):
    def autoname(self):
        # You can call the original autoname method of Item if needed
        if self.custom_abbreviation:
            # Use dot (.) to separate the prefix from the numeric part
            self.name = make_autoname(f"{self.custom_abbreviation}-.#####")
        else:
            frappe.throw("Custom Abbreviation is required for auto-naming.")

    # Add or override any other methods specific to CustomItem
    def validate(self):
        # Call the original validate method of Item
        super().validate()
        self.meta.get_field("item_code").reqd = 0
        # Custom validation logic if needed
        if not self.custom_abbreviation:
            frappe.throw("Custom Abbreviation is mandatory for this item.")
