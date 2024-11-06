from erpnext.accounts.doctype.pricing_rule.pricing_rule import PricingRule
from frappe.model.naming import make_autoname
import frappe

class CustomPricingRule(PricingRule):
    def before_save(self):
        # Set title to the document name (Naming Series)
        self.title = self.name

    def autoname(self):
        try:
            # Check if 'items' child table has rows
            if self.items and len(self.items) > 0:
                # Access the first row of the 'items' child table
                first_row = self.items[0]

                # Ensure that 'item_code' exists in the first row
                if first_row.item_code:
                    # Set the custom item code naming series
                    self.custom_item_code_naming_series = first_row.item_code

                    # Generate a name using make_autoname with the item_code
                    self.name = make_autoname(f"PRLE-{first_row.item_code}-.##")
                else:
                    # Throw an error if item_code is missing in the first row
                    frappe.throw("Item Code is missing in the first row of items.")
            else:
                # Throw an error if the items table is empty
                frappe.throw("No items available in the child table.")
        except Exception as e:
            # Handle any unexpected exceptions and show an alert with the error message
            frappe.throw(f"An error occurred while generating the name: {str(e)}")
