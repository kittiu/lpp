import frappe
from erpnext.stock.doctype.quality_inspection.quality_inspection import QualityInspection
from erpnext.stock.doctype.quality_inspection_template.quality_inspection_template import (
    get_template_details,
)

class CustomQualityInspection(QualityInspection):
                        
    @frappe.whitelist()
    def custom_get_item_specification_details(self, template_key="" ,table_key=""):
        # 
        template_value = getattr(self, template_key, None)
        
        if not template_value:
            template_value = frappe.db.get_value(
                "Item", self.item_code, template_key
            )
            setattr(self, template_key, template_value)

        if not template_value:
            return

        # Assuming there is a table field associated with the key
        self.set(table_key, [])
        parameters = get_template_details(template_value)
        for d in parameters:
            child = self.append(table_key, {})
            child.update(d)
            child.status = "Accepted"

