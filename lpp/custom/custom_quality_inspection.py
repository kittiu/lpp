import frappe
from erpnext.stock.doctype.quality_inspection.quality_inspection import QualityInspection
from erpnext.stock.doctype.quality_inspection_template.quality_inspection_template import (
    get_template_details,
)
import json
from frappe import _
from frappe.utils import flt

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


@frappe.whitelist()
def custom_make_quality_inspections(doctype, docname, items):
    if isinstance(items, str):
        items = json.loads(items)

    inspections = []
    for item in items:
        if flt(item.get("sample_size")) > flt(item.get("qty")):
            frappe.throw(
                _("{item_name}'s Sample Size ({sample_size}) cannot be greater than the Accepted Quantity ({accepted_quantity})")
                .format(
                    item_name=item.get("item_name"),
                    sample_size=item.get("sample_size"),
                    accepted_quantity=item.get("qty"),
                )
            )

        # quality_inspection = frappe.get_doc(
        #     {
        #         "doctype": "Quality Inspection",
        #         "inspection_type": "Incoming",
        #         "inspected_by": frappe.session.user,
        #         "reference_type": doctype,
        #         "reference_name": docname,
        #         "item_code": item.get("item_code"),
        #         "description": item.get("description"),
        #         "sample_size": flt(item.get("sample_size")),
        #         "item_serial_no": item.get("serial_no").split("\n")[0] if item.get("serial_no") else None,
        #         "batch_no": item.get("batch_no"),
        #         "custom_supplier": 'AP-601'
        #     }
        # ).insert()
        quality_inspection_data = {
            "doctype": "Quality Inspection",
            "inspection_type": "Incoming",
            "inspected_by": frappe.session.user,
            "reference_type": doctype,
            "reference_name": docname,
            "item_code": item.get("item_code"),
            "description": item.get("description"),
            "sample_size": flt(item.get("sample_size")),
            "item_serial_no": item.get("serial_no").split("\n")[0] if item.get("serial_no") else None,
            "batch_no": item.get("batch_no"),
            

        }
        if doctype == 'Purchase Receipt':
            prname = frappe.db.get_value('Purchase Receipt', docname, "supplier",)
            quality_inspection_data["custom_supplier"] = prname
            quality_inspection_data["custom_accepted_quantity_imqa_uom"] = item.get("custom_accepted_quantity_imqa_uom") if item.get("custom_accepted_quantity_imqa_uom") else None
            


        quality_inspection = frappe.get_doc(quality_inspection_data).insert()
        quality_inspection.save()
        inspections.append(quality_inspection.name)

    return inspections