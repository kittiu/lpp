import frappe
from erpnext.stock.doctype.quality_inspection.quality_inspection import QualityInspection
from erpnext.stock.doctype.quality_inspection_template.quality_inspection_template import (
    get_template_details,
)
import json
from frappe import _
from frappe.utils import flt

specs = {
            'A0 (mm)': {'valueField': 'custom_a0_tolerance', 'toleranceFieldMax': 'custom_a0_max', 'toleranceFieldMin': 'custom_a0_min'},
            'B0 (mm)': {'valueField': 'custom_b0_tolerance', 'toleranceFieldMax': 'custom_b0_max', 'toleranceFieldMin': 'custom_b0_min'},
            'K0 (mm)': {'valueField': 'custom_k0_tolerance', 'toleranceFieldMax': 'custom_k0_max', 'toleranceFieldMin': 'custom_k0_min'},
            'P1 (mm)': {'valueField': 'custom_p1_tolerance', 'toleranceFieldMax': 'custom_p1_max', 'toleranceFieldMin': 'custom_p1_min'},
            'Thickness (mm)': {'valueField': 'custom_thickness_tolerance', 'toleranceFieldMax': 'custom_thickness_max', 'toleranceFieldMin': 'custom_thickness_min'},
            'Width (mm)': {'valueField': 'custom_width_tolerance', 'toleranceFieldMax': 'custom_width_max', 'toleranceFieldMin': 'custom_width_min'},
            'Length / Reel (m)': {'valueField': 'custom_length__reel_tolerance', 'toleranceFieldMax': 'custom_length__reel_max', 'toleranceFieldMin': 'custom_length__reel_min'},
            'A (mm)': {'valueField': 'custom_a_basic', 'toleranceFieldMax': 'custom_a_basic_max', 'toleranceFieldMin': 'custom_a_basic_min'},
            '\u00d8A (mm)': {'valueField': 'custom_a_tolerance', 'toleranceFieldMax': 'custom_a_max', 'toleranceFieldMin': 'custom_a_min'},
            '\u00d8N (mm) (+)': {'valueField': 'custom_n_tolerance', 'toleranceFieldMax': 'custom_n_max', 'toleranceFieldMin': 'custom_n_min'},
            'B (mm)': {'valueField': 'custom_b_tolerance', 'toleranceFieldMax': 'custom_b_max', 'toleranceFieldMin': 'custom_b_min'},
            'C (mm)': {'valueField': 'custom_c_basic', 'toleranceFieldMax': 'custom_c_basic_max', 'toleranceFieldMin': 'custom_c_basic_min'},
            '\u00d8C (mm)': {'valueField': 'custom_c_tolerance', 'toleranceFieldMax': 'custom_c_max', 'toleranceFieldMin': 'custom_c_min'},
            'D (mm)': {'valueField': 'custom_d_basic', 'toleranceFieldMax': 'custom_d_basic_max', 'toleranceFieldMin': 'custom_d_basic_min'},
            '\u00d8D (mm)': {'valueField': 'custom_d_tolerance', 'toleranceFieldMax': 'custom_d_max', 'toleranceFieldMin': 'custom_d_min'},
            'E (mm)': {'valueField': 'custom_e_tolerance', 'toleranceFieldMax': 'custom_e_max', 'toleranceFieldMin': 'custom_e_min'},
            'F (mm)': {'valueField': 'custom_f_tolerance', 'toleranceFieldMax': 'custom_f_max', 'toleranceFieldMin': 'custom_f_min'},
            'G (mm)': {'valueField': 'custom_g_tolerance', 'toleranceFieldMax': 'custom_g_max', 'toleranceFieldMin': 'custom_g_min'},
            'H (mm)': {'valueField': 'custom_h_tolerance', 'toleranceFieldMax': 'custom_h_max', 'toleranceFieldMin': 'custom_h_min'},
            'I (mm)': {'valueField': 'custom_i_tolerance', 'toleranceFieldMax': 'custom_i_max', 'toleranceFieldMin': 'custom_i_min'},
            'J (mm)': {'valueField': 'custom_j_tolerance', 'toleranceFieldMax': 'custom_j_max', 'toleranceFieldMin': 'custom_j_min'},
            'K (mm)': {'valueField': 'custom_k_tolerance', 'toleranceFieldMax': 'custom_k_max', 'toleranceFieldMin': 'custom_k_min'},
            'T1 (mm)': {'valueField': 'custom_t1_tolerance', 'toleranceFieldMax': 'custom_t1_max', 'toleranceFieldMin': 'custom_t1_min'},
            'T2 (mm)': {'valueField': 'custom_t2_tolerance', 'toleranceFieldMax': 'custom_t2_max', 'toleranceFieldMin': 'custom_t2_min'},
            'W1 (mm)': {'valueField': 'custom_w1_tolerance', 'toleranceFieldMax': 'custom_w1_max', 'toleranceFieldMin': 'custom_w1_min'},
            'W2 (mm)': {'valueField': 'custom_w2_tolerance', 'toleranceFieldMax': 'custom_w2_max', 'toleranceFieldMin': 'custom_w2_min'},
            'Delta E': {'valueField': 'custom_delta_e_tolerance', 'toleranceFieldMax': 'custom_delta_e_max', 'toleranceFieldMin': 'custom_delta_e_min'},
            'Surface Resistivity (ohms/sq)': {'valueField': 'custom_surface_resistivity_ohmssq', 'toleranceFieldMax': 'custom_surface_resistivity_ohmssq_max', 'toleranceFieldMin': 'custom_surface_resistivity_ohmssq_min'},
            'Length (mm)': {'valueField': 'custom_length_tolerance', 'toleranceFieldMax': 'custom_length_max', 'toleranceFieldMin': 'custom_length_min'},
            'Height (mm)': {'valueField': 'custom_height_tolerance', 'toleranceFieldMax': 'custom_height_max', 'toleranceFieldMin': 'custom_height_min'},
}

class CustomQualityInspection(QualityInspection):
    
    @frappe.whitelist()  # Allow the method to be called from client side
    def custom_get_item_specification_details(self,item_code, template_key, table_key):
        # Define specifications mapping
        template_value = getattr(self, template_key, None)
        parameters = get_template_details(template_value)

        # Prepare a list to hold table data
        table_data = []

        # Fetch all item data
        item_data = frappe.db.get_value('Item', {'item_code': item_code}, "*")

        # Process each specification
        for param in parameters:
            spec_name = param["specification"]
            spec_fields = specs.get(spec_name)
            
            row = {"defects": spec_name, "status": "Accepted"}
            
            if spec_fields:
                row["nominal_value"] = item_data.get(spec_fields["valueField"])
                row["tolerance_upper"] = item_data.get(spec_fields["toleranceFieldMax"])
                row["tolerance_min"] = item_data.get(spec_fields["toleranceFieldMin"])
            
            table_data.append(row)

        # Return the table data
        return table_data
                        
@frappe.whitelist()
def trigger_notification(docname):
    try:
        # Retrieve the Material Request document using the given docname
        doc = frappe.get_doc("Quality Inspection", docname)
        # Fetch the Notification document by its name
        notification = frappe.get_doc("Notification", "New Quality Inspection from PR")
        
        # Check if the notification is enabled before sending
        if notification.enabled:
            # Manually trigger the notification by sending it for the current document
            notification.send(doc)
        
        # Return success status
        return {"status": "success", "message": "Notification triggered successfully"}
    
    except Exception as e:
        # Handle exceptions and return the error
        frappe.log_error(frappe.get_traceback(), "Notification Trigger Error")
        return {"status": "failed", "message": str(e)}

@frappe.whitelist()
def custom_make_quality_inspections(doctype, docname, items):
    if isinstance(items, str):
        items = json.loads(items)
        
    if doctype == 'Purchase Receipt':
        # check already exists 
        exist_data = frappe.db.get_list('Quality Inspection',
                filters={
                    'reference_name': docname
                },
                fields=['name'],

        )
        if exist_data:
            frappe.throw("All items in this document already have a linked Quality Inspection.")
    

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
        
        if doctype == 'Purchase Receipt' :
            prname = frappe.db.get_value('Purchase Receipt', docname, "supplier",)
            quality_inspection_data["custom_supplier"] = prname
            quality_inspection_data["custom_accepted_quantity_imqa_uom"] = item.get("custom_accepted_quantity_imqa_uom") if item.get("custom_accepted_quantity_imqa_uom") else None
            
        quality_inspection = frappe.get_doc(quality_inspection_data).insert()
        quality_inspection.save()
        inspections.append(quality_inspection.name)

    return inspections