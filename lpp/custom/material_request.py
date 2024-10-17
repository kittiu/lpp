import frappe # type: ignore
from erpnext.stock.doctype.material_request.material_request import MaterialRequest


class MaterialRequestLPP(MaterialRequest):
    def validate(self):
        if self.workflow_state == 'Approved':
            self.custom_approver = self.modified_by if self.modified_by else None
        super().validate()

@frappe.whitelist()
def trigger_notification(docname):
    try:
        # Retrieve the Material Request document using the given docname
        doc = frappe.get_doc("Material Request", docname)
        
        # Fetch the Notification document by its name
        notification = frappe.get_doc("Notification", "Send to MD For Material Request")
        
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
